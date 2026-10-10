"""Python owns the active application's identity, business API and database writes."""
import hashlib
import json
import os
import re
import secrets
import time
import uuid
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .database import ROOT, contracts, hash_password, open_database, seed, verify_password
from .report_adapters import DATASETS, load_rows
from .error_reporting import incident_metadata, record_incident
from packages.reporting.engine import render_report

class APIError(Exception):
    def __init__(self, status, message): self.status, self.message = status, message

def require(condition, status, message):
    if not condition: raise APIError(status, message)

def redact(value):
    if isinstance(value, dict): return {key:'[REDACTED]' if re.search(r'password|token|secret|api.?key',key,re.I) else redact(item) for key,item in value.items()}
    if isinstance(value, list): return [redact(item) for item in value]
    return value

def create_app(database_path=None, password=None, mode=None, public_origin=None):
    mode = mode or os.getenv('TOMVIS_MODE','sandbox')
    if mode not in ('sandbox','demo','development'): raise ValueError('Production/staging are not enabled in this alpha')
    password = password or os.getenv('TOMVIS_DEMO_PASSWORD','')
    if not 12 <= len(password) <= 256: raise ValueError('Set TOMVIS_DEMO_PASSWORD to 12–256 characters')
    public_origin = public_origin or os.getenv('TOMVIS_PUBLIC_ORIGIN','http://localhost:3000')
    origin = urlparse(public_origin)
    if origin.scheme != 'http' or origin.hostname not in ('localhost','127.0.0.1') or origin.username or origin.password or origin.path or origin.query or origin.fragment:
        raise ValueError('Public origin must be a local HTTP origin without path')
    database_path = str(database_path or ROOT / f'data/{mode}.sqlite')
    if database_path == ':memory:': raise ValueError('Use a temporary file database for API tests')
    Path(database_path).parent.mkdir(parents=True,exist_ok=True)
    db = open_database(database_path,password)
    db.close()
    contract = contracts()
    roles = contract['roles']
    dummy_password = hash_password(secrets.token_hex(16))
    buckets = {}
    app = FastAPI(title='Tomvis Python API',docs_url=None,redoc_url=None,openapi_url=None)
    app.state.database_path = database_path

    @app.middleware('http')
    async def headers(request, call_next):
        request.state.request_id = str(uuid.uuid4())
        response = await call_next(request)
        for key,value in {'X-Request-ID':request.state.request_id,'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','X-Frame-Options':'DENY','Referrer-Policy':'no-referrer'}.items(): response.headers[key] = value
        return response

    @app.api_route('/api/{path:path}',methods=['GET','POST','PATCH','DELETE'])
    async def api(request: Request,path: str):
        db = None
        user = None
        def response(data=None,status=200,error=None):
            content = {'success':False,'error':{'code':f'HTTP_{status}','message':error}} if error else {'success':True,'data':data}
            content['meta'] = {'request_id':request.state.request_id,'mode':mode}
            return JSONResponse(content,status_code=status)
        try:
            if path == 'health' and request.method == 'GET': return response({'status':'ok','version':contract['manual']['version'],'backend':'python-fastapi'})
            now = time.time()
            # Loopback BFF traffic shares an aggregate limit; forwarded IPs are never trusted.
            ip = request.client.host if request.client else 'unknown'
            for key in list(buckets):
                if buckets[key]['expires'] <= now: del buckets[key]
            bucket = buckets.setdefault(ip,{'count':0,'expires':now+60})
            bucket['count'] += 1
            require(bucket['count'] <= 120,429,'Too many requests')
            body = {}
            if request.method in ('POST','PATCH','DELETE'):
                require(request.headers.get('origin') == public_origin and request.headers.get('sec-fetch-site') != 'cross-site',403,'Origin rejected')
                require(request.headers.get('content-type','').split(';')[0].strip() == 'application/json',415,'JSON required')
                raw = bytearray()
                async for chunk in request.stream():
                    raw.extend(chunk)
                    require(len(raw) <= 16384,413,'Request too large')
                try: body = json.loads(raw or b'{}')
                except (ValueError,UnicodeDecodeError): raise APIError(400,'Invalid JSON')
                require(isinstance(body,dict),422,'Invalid body')
            db = __import__('sqlite3').connect(database_path)
            db.row_factory = __import__('sqlite3').Row
            db.execute('PRAGMA foreign_keys=ON')
            db.execute('PRAGMA busy_timeout=5000')
            token = request.cookies.get('tv_session','')
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            record = db.execute('SELECT u.id,u.name,u.email,u.disabled,s.tenant_id,m.role FROM sessions s JOIN users u ON u.id=s.user_id JOIN memberships m ON m.user_id=u.id AND m.tenant_id=s.tenant_id WHERE s.token=? AND s.expires_at>?',(token_hash,int(now*1000))).fetchone() if token else None
            user = dict(record) if record else None
            def can(permission): return bool(user and ('*' in roles.get(user['role'],[]) or permission in roles.get(user['role'],[])))
            def permission(name): require(can(name),403,'Permission denied')
            def audit(action,resource,rid='',old=None,new=None,actor=None):
                actor = actor or user or {'id':'anonymous','tenant_id':'demo'}
                db.execute('INSERT INTO audit_logs(tenant_id,actor,action,resource,resource_id,old_value,new_value,ip,user_agent,request_id) VALUES(?,?,?,?,?,?,?,?,?,?)',(actor['tenant_id'],actor['id'],action,resource,str(rid),json.dumps(redact(old)),json.dumps(redact(new)),ip,request.headers.get('user-agent','')[:300],request.state.request_id))
            if path == 'v1/login' and request.method == 'POST':
                require(set(body)=={'email','password'} and isinstance(body.get('email'),str) and isinstance(body.get('password'),str) and len(body['email'])<=254 and len(body['password'])<=256,422,'Invalid credentials')
                require(bucket['count']<=20,429,'Login rate limit reached')
                account = db.execute('SELECT * FROM users WHERE email=?',(body['email'],)).fetchone()
                valid = verify_password(body['password'],account['password'] if account else dummy_password)
                if not account or account['disabled'] or not valid:
                    with db: audit('login.failed','session')
                    raise APIError(401,'Email or password incorrect')
                member = db.execute('SELECT * FROM memberships WHERE user_id=? ORDER BY tenant_id LIMIT 1',(account['id'],)).fetchone()
                require(member is not None,403,'No workspace membership')
                session = secrets.token_hex(32)
                with db:
                    db.execute('INSERT INTO sessions VALUES(?,?,?,?)',(hashlib.sha256(session.encode()).hexdigest(),account['id'],member['tenant_id'],int(now*1000)+28800000))
                    audit('login.success','session',actor={'id':account['id'],'tenant_id':member['tenant_id']})
                result = response({'name':account['name']})
                result.set_cookie('tv_session',session,max_age=28800,httponly=True,samesite='strict',path='/')
                return result
            require(user is not None and not user['disabled'],401,'Please sign in')
            tenant = user['tenant_id']
            if path == 'v1/errors/client' and request.method == 'POST':
                require(set(body)=={'code','component'} and body.get('code')=='UI_RENDER_ERROR' and body.get('component') in ('next-page','next-global'),422,'Invalid incident metadata')
                metadata={'fingerprint':hashlib.sha256(f"{contract['manual']['version']}:UI_RENDER_ERROR:{body['component']}".encode()).hexdigest(),'category':'UI_RENDER_ERROR','component':body['component'],'framework_version':contract['manual']['version'],'route':'ui'}
                with db: record_incident(db,tenant,request.state.request_id,metadata)
                return response({'recorded':True},201)
            if path == 'v1/reports/catalog' and request.method == 'GET':
                return response([{k:v for k,v in item.items() if k!='permission'} for item in DATASETS if can(item['permission'])])
            if path == 'v1/reports/run' and request.method == 'POST':
                require(not set(body)-{'source','title','columns','groupBy','filters'},422,'Invalid report request')
                dataset=next((item for item in DATASETS if item['id']==body.get('source')),None)
                require(dataset is not None,422,'Unknown report source')
                permission(dataset['permission'])
                try:
                    rows,total=load_rows(db,dataset,tenant,body.get('filters',{}))
                    workspace=db.execute('SELECT name FROM tenants WHERE id=?',(tenant,)).fetchone()['name']
                    report=render_report(dataset,rows,body,workspace,total)
                except (ValueError,TypeError,KeyError): raise APIError(422,'Invalid report configuration')
                with db: audit('report.generated','report',dataset['id'],new={'returned':len(rows),'total':total})
                return response(report)
            if path == 'v1/errors' and request.method == 'GET':
                permission('audit.view')
                return response([dict(row) for row in db.execute('SELECT fingerprint,category,component,framework_version,route,request_id,occurrences,first_seen,last_seen FROM error_reports WHERE tenant_id=? ORDER BY last_seen DESC,id DESC LIMIT 100',(tenant,))])
            if path == 'v1/me' and request.method == 'GET': return response({**user,'roles':roles,'mode':mode,'workspace':db.execute('SELECT name FROM tenants WHERE id=?',(tenant,)).fetchone()['name']})
            if path == 'v1/manual' and request.method == 'GET':
                guide = contract['manual']
                sections = [{key:value for key,value in section.items() if key != 'permissions'} for section in guide['sections'] if all(can(p) for p in section['permissions'])]
                return response({**guide,'sections':sections})
            if path == 'v1/logout' and request.method == 'POST':
                with db:
                    db.execute('DELETE FROM sessions WHERE token=?',(token_hash,))
                    audit('logout','session')
                result = response({})
                result.delete_cookie('tv_session',path='/',httponly=True,samesite='strict')
                return result
            if path == 'v1/feedback' and request.method == 'GET':
                permission('feedback.view')
                q = request.query_params.get('q','')
                require(len(q)<=200,422,'Search too long')
                return response([dict(row) for row in db.execute('SELECT id,subject,category,status,priority,created_at FROM feedback WHERE tenant_id=? AND subject LIKE ? ORDER BY id DESC LIMIT 100',(tenant,f'%{q}%'))])
            if path == 'v1/feedback' and request.method == 'POST':
                permission('feedback.manage')
                require(set(body)=={'subject','category','priority'} and isinstance(body.get('subject'),str) and 1<=len(body['subject'].strip())<=200 and body.get('category') in ('Service','Suggestion','Appreciation','Technical') and body.get('priority') in ('low','medium','high'),422,'Invalid feedback')
                body['subject'] = body['subject'].strip()
                with db:
                    cursor = db.execute('INSERT INTO feedback(tenant_id,subject,category,status,priority) VALUES(?,?,?,?,?)',(tenant,body['subject'],body['category'],'open',body['priority']))
                    audit('feedback.created','feedback',cursor.lastrowid,new=body)
                return response({'id':cursor.lastrowid},201)
            match = re.fullmatch(r'v1/feedback/(\d+)',path)
            if match and request.method == 'PATCH':
                permission('feedback.manage')
                require(set(body)=={'status'} and body.get('status') in ('open','in_progress','resolved'),422,'Invalid status')
                rid = match.group(1)
                with db:
                    db.execute('BEGIN IMMEDIATE')
                    old = db.execute('SELECT * FROM feedback WHERE id=? AND tenant_id=?',(rid,tenant)).fetchone()
                    require(old is not None,404,'Feedback not found')
                    db.execute('UPDATE feedback SET status=? WHERE id=? AND tenant_id=?',(body['status'],rid,tenant))
                    audit('feedback.updated','feedback',rid,old=dict(old),new=body)
                return response({})
            if path == 'v1/users' and request.method == 'GET':
                permission('users.view')
                return response([dict(row) for row in db.execute('SELECT u.name,u.email,m.role,u.disabled FROM users u JOIN memberships m ON m.user_id=u.id WHERE m.tenant_id=?',(tenant,))])
            if path == 'v1/audit' and request.method == 'GET':
                permission('audit.view')
                return response([dict(row) for row in db.execute('SELECT actor,action,resource,timestamp,request_id FROM audit_logs WHERE tenant_id=? ORDER BY id DESC LIMIT 100',(tenant,))])
            if path == 'v1/sandbox/reset' and request.method == 'POST':
                permission('sandbox.reset')
                require(body == {'confirm':'RESET'},422,'Confirmation required')
                with db:
                    db.execute('DELETE FROM feedback WHERE tenant_id=?',(tenant,))
                    seed(db,tenant)
                    audit('sandbox.reset','tenant',tenant,new={'synthetic':True})
                return response({})
            raise APIError(404,'Not found')
        except APIError as error: return response(status=error.status,error=error.message)
        except Exception as error:
            if db:
                try:
                    db.rollback()
                    if user:
                        safe_path=re.sub(r'/\d+(?=/|$)','/:id',path)
                        if safe_path not in ('v1/reports/run','v1/feedback','v1/feedback/:id','v1/me','v1/manual','v1/users','v1/audit','v1/errors','v1/sandbox/reset','v1/logout'): safe_path='unknown'
                        with db: record_incident(db,user['tenant_id'],request.state.request_id,incident_metadata(error,contract['manual']['version'],safe_path))
                except Exception: pass
            return response(status=500,error='Internal server error')
        finally:
            if db: db.close()
    return app
