import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import unittest
from contextlib import contextmanager
from fastapi.testclient import TestClient
from apps.api.main import create_app
from apps.api.error_reporting import incident_metadata
from apps.api.database import open_database

class APITests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=Path(self.temp.name)/'test.sqlite'
        self.app=create_app(self.path,'test-password-long')
        self.client=TestClient(self.app)
        self.headers={'Origin':'http://localhost:3000'}
    def tearDown(self):
        self.client.close()
        self.temp.cleanup()
    def login(self,email='admin@tomvis.demo'):
        result=self.client.post('/api/v1/login',json={'email':email,'password':'test-password-long'},headers=self.headers)
        self.assertEqual(result.status_code,200)
        return result
    @contextmanager
    def db(self):
        db=sqlite3.connect(self.path)
        try:
            with db: yield db
        finally: db.close()
    def test_auth_rbac_csrf_and_revocation(self):
        self.assertEqual(self.client.get('/api/v1/feedback').status_code,401)
        self.login('staff@tomvis.demo')
        self.assertEqual(self.client.get('/api/v1/users').status_code,403)
        self.assertEqual(self.client.post('/api/v1/sandbox/reset',json={'confirm':'RESET'},headers=self.headers).status_code,403)
        self.assertEqual(self.client.post('/api/v1/feedback',json={},headers={'Origin':'https://evil.example'}).status_code,403)
        with self.db() as db: db.execute("UPDATE users SET disabled=1 WHERE id='staff'")
        self.assertEqual(self.client.get('/api/v1/feedback').status_code,401)
        self.assertEqual(self.client.post('/api/v1/login',json={'email':'staff@tomvis.demo','password':'test-password-long'},headers=self.headers).status_code,401)
    def test_feedback_tenant_reset_and_audit(self):
        self.login()
        with self.db() as db: other=db.execute("SELECT id FROM feedback WHERE tenant_id='other' LIMIT 1").fetchone()[0]
        self.assertEqual(self.client.patch(f'/api/v1/feedback/{other}',json={'status':'resolved'},headers=self.headers).status_code,404)
        self.assertEqual(self.client.post('/api/v1/feedback',json={'subject':'Python integration','category':'Technical','priority':'high'},headers=self.headers).status_code,201)
        self.assertEqual(self.client.post('/api/v1/sandbox/reset',json={'confirm':'RESET'},headers=self.headers).status_code,200)
        with self.db() as db:
            self.assertEqual(db.execute("SELECT count(*) FROM feedback WHERE tenant_id='other'").fetchone()[0],6)
            self.assertEqual(db.execute("SELECT count(*) FROM feedback WHERE tenant_id='demo'").fetchone()[0],6)
            self.assertGreater(db.execute("SELECT count(*) FROM audit_logs WHERE action='sandbox.reset'").fetchone()[0],0)
    def test_manual_and_reports_are_permission_and_tenant_scoped(self):
        self.login('viewer@tomvis.demo')
        guide=self.client.get('/api/v1/manual').json()['data']
        self.assertFalse(any(s['id']=='feedback-create' for s in guide['sections']))
        catalog=self.client.get('/api/v1/reports/catalog').json()['data']
        self.assertEqual([s['id'] for s in catalog],['feedback'])
        self.assertEqual(self.client.post('/api/v1/reports/run',json={'source':'users'},headers=self.headers).status_code,403)
        report=self.client.post('/api/v1/reports/run',json={'source':'feedback','groupBy':'status','columns':['subject','status']},headers=self.headers)
        self.assertEqual(report.status_code,200)
        data=report.json()['data']
        self.assertEqual(data['summary']['total'],6)
        self.assertEqual(len(data['rows']),6)
        self.assertEqual(sum(data['summary']['groups'].values()),6)
        self.assertEqual(self.client.post('/api/v1/reports/run',json={'source':'feedback','columns':['password']},headers=self.headers).status_code,422)
    def test_backend_failure_rolls_back_and_records_safe_framework_incident(self):
        self.login()
        with self.db() as db:
            before=db.execute('SELECT count(*) FROM feedback').fetchone()[0]
            db.execute("CREATE TRIGGER reject_audit BEFORE INSERT ON audit_logs WHEN NEW.action='feedback.created' BEGIN SELECT RAISE(ABORT,'sensitive-password=never-log-me'); END")
        result=self.client.post('/api/v1/feedback',json={'subject':'Failure test','category':'Technical','priority':'high'},headers=self.headers)
        self.assertEqual(result.status_code,500)
        self.assertNotIn('never-log-me',result.text)
        with self.db() as db: self.assertEqual(db.execute('SELECT count(*) FROM feedback').fetchone()[0],before)
        errors=self.client.get('/api/v1/errors').json()['data']
        self.assertEqual(len(errors),1)
        self.assertEqual(errors[0]['request_id'],result.headers['x-request-id'])
        self.assertNotIn('sensitive',json.dumps(errors))
    def test_node_database_and_session_are_compatible_with_python(self):
        legacy=Path(self.temp.name)/'node.sqlite'
        script="import {createDatabase} from './packages/database/index.js'; import {migrations} from './apps/migrations.js'; import {createHash} from 'node:crypto'; const db=createDatabase(process.argv[1],'test-password-long',migrations); db.prepare('INSERT INTO sessions VALUES(?,?,?,?)').run(createHash('sha256').update('cross-runtime-session').digest('hex'),'admin','demo',Date.now()+60000); db.close();"
        subprocess.run(['node','--input-type=module','-e',script,str(legacy)],check=True,capture_output=True)
        app=create_app(legacy,'test-password-long')
        with TestClient(app) as client:
            client.cookies.set('tv_session','cross-runtime-session')
            self.assertEqual(client.get('/api/v1/me').status_code,200)
            result=client.post('/api/v1/login',json={'email':'admin@tomvis.demo','password':'test-password-long'},headers=self.headers)
            self.assertEqual(result.status_code,200)
        db=open_database(legacy,'test-password-long');db.close()
    def test_invalid_config_and_no_raw_error_text(self):
        with self.assertRaises(ValueError):create_app(self.path,'test-password-long',mode='production')
        with self.assertRaises(ValueError):create_app(self.path,'test-password-long',public_origin='https://external.example')
        metadata=incident_metadata(RuntimeError('api_key=secret'),'3','route')
        self.assertNotIn('secret',json.dumps(metadata))
    def test_ui_incident_metadata_is_restricted_and_requires_session(self):
        payload={'code':'UI_RENDER_ERROR','component':'next-page'}
        self.assertEqual(self.client.post('/api/v1/errors/client',json=payload,headers=self.headers).status_code,401)
        self.login()
        self.assertEqual(self.client.post('/api/v1/errors/client',json={**payload,'stack':'sensitive'},headers=self.headers).status_code,422)
        self.assertEqual(self.client.post('/api/v1/errors/client',json=payload,headers=self.headers).status_code,201)
        self.assertEqual(self.client.post('/api/v1/errors/client',json=payload,headers=self.headers).status_code,201)
        errors=self.client.get('/api/v1/errors').json()['data']
        self.assertEqual(errors[0]['category'],'UI_RENDER_ERROR')
        self.assertEqual(errors[0]['occurrences'],2)

if __name__=='__main__': unittest.main()
