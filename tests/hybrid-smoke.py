"""Real HTTP integration through built Next.js -> FastAPI; temporary synthetic DB."""
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import httpx

def port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0))
        return sock.getsockname()[1]

root=Path(__file__).resolve().parents[1]
backend_port,frontend_port=port(),port()
origin=f'http://127.0.0.1:{frontend_port}'
processes=[]
with tempfile.TemporaryDirectory() as folder:
    env={**os.environ,'TOMVIS_MODE':'sandbox','TOMVIS_DEMO_PASSWORD':'integration-test-password','TOMVIS_PUBLIC_ORIGIN':origin,'TOMVIS_API_URL':f'http://127.0.0.1:{backend_port}','TOMVIS_TEST_DB':str(Path(folder)/'synthetic.sqlite'),'TOMVIS_TEST_PORT':str(backend_port),'NEXT_TELEMETRY_DISABLED':'1'}
    log=open(Path(folder)/'process.log','w',encoding='utf-8')
    try:
        code="import os,uvicorn; from apps.api.main import create_app; uvicorn.run(create_app(os.environ['TOMVIS_TEST_DB']),host='127.0.0.1',port=int(os.environ['TOMVIS_TEST_PORT']),access_log=False)"
        processes.append(subprocess.Popen([sys.executable,'-c',code],cwd=root,env=env,stdout=log,stderr=log))
        processes.append(subprocess.Popen(['node','node_modules/next/dist/bin/next','start','apps/web','--hostname','127.0.0.1','--port',str(frontend_port)],cwd=root,env=env,stdout=log,stderr=log))
        with httpx.Client(base_url=origin,timeout=10,headers={'Origin':origin}) as client:
            deadline=time.monotonic()+45
            while True:
                try:
                    result=client.get('/api/health')
                    if result.status_code==200:break
                except httpx.HTTPError:pass
                if any(p.poll() is not None for p in processes) or time.monotonic()>deadline:raise RuntimeError('Hybrid startup failed')
                time.sleep(.3)
            assert result.json()['data']['backend']=='python-fastapi'
            assert client.get('/').status_code==200
            assert client.get('/api/v1/feedback').status_code==401
            result=client.post('/api/v1/login',json={'email':'admin@tomvis.demo','password':'integration-test-password'})
            assert result.status_code==200,result.text
            assert 'HttpOnly' in result.headers['set-cookie']
            assert client.get('/api/v1/me').json()['data']['role']=='admin'
            assert len(client.get('/api/v1/feedback').json()['data'])==6
            assert client.post('/api/v1/feedback',json={'subject':'Next to Python integration','category':'Technical','priority':'high'}).status_code==201
            assert client.post('/api/v1/feedback',json={},headers={'Origin':'https://evil.example'}).status_code==403
            report=client.post('/api/v1/reports/run',json={'source':'feedback','groupBy':'status'})
            assert report.status_code==200,report.text
            assert report.json()['data']['summary']['total']==7
            assert len(client.get('/api/v1/manual').json()['data']['sections'])>=8
            assert client.get('/api/v1/errors').status_code==200
            assert client.post('/api/v1/logout',json={}).status_code==200
            assert client.get('/api/v1/me').status_code==401
            print('PASS: real Next.js -> FastAPI login, cookie, tenant API, report, manual, error listing, CSRF and logout')
            if '--browser' in sys.argv:
                subprocess.run(['node','tests/browser-smoke.cjs',origin],cwd=root,env=env,check=True)
    finally:
        for process in processes:
            if process.poll() is None:process.terminate()
        for process in processes:
            try:process.wait(timeout=10)
            except subprocess.TimeoutExpired:process.kill();process.wait(timeout=10)
        log.close()
