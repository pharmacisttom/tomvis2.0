import {existsSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {resolve} from 'node:path';
import {runtimeConfig} from '../packages/config/index.js';
const local=process.platform==='win32'?'.venv/Scripts/python.exe':'.venv/bin/python';
const python=process.env.TOMVIS_PYTHON||(existsSync(local)?resolve(local):'python');
const result=spawnSync(python,['-c','import fastapi,uvicorn; print("ready")'],{encoding:'utf8',windowsHide:true});
let configValid=true;try{runtimeConfig();}catch{configValid=false;}
const checks=[['Node runtime',Number(process.versions.node.split('.')[0])>=22],['Python API dependencies',result.status===0],['Local environment/password config',configValid],['Generated runtime contracts',existsSync('docs/generated/runtime-contracts.json')],['Next frontend',existsSync('apps/web/app/page.jsx')],['Database migrations',existsSync('apps/migrations.js')]];
for(const [name,ok] of checks)console.log(`${ok?'PASS':'FAIL'} ${name}`);
console.log('WARNING Local alpha: production/MySQL, customer VPS, Drive backup execution and centralized incident delivery remain pending');
if(process.argv.includes('--deploy')){console.log('FAIL Production deployment is not enabled in this alpha');process.exitCode=1;}
else if(checks.some(([,ok])=>!ok))process.exitCode=1;
