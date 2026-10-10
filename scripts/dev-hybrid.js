import {spawn} from 'node:child_process';
import {existsSync} from 'node:fs';
import {resolve} from 'node:path';
import {runtimeConfig} from '../packages/config/index.js';
runtimeConfig();
const local=process.platform==='win32'?'.venv/Scripts/python.exe':'.venv/bin/python';
const python=process.env.TOMVIS_PYTHON||(existsSync(local)?resolve(local):'python');
const apiPort=Number(process.env.TOMVIS_API_PORT||8000);
if(!Number.isInteger(apiPort)||apiPort<1||apiPort>65535)throw Error('Invalid API port');
const port=Number(process.env.PORT||3000);
if(port===apiPort)throw Error('Frontend and API need distinct ports');
const env={...process.env,TOMVIS_PUBLIC_ORIGIN:process.env.TOMVIS_PUBLIC_ORIGIN||`http://localhost:${port}`,TOMVIS_API_URL:`http://127.0.0.1:${apiPort}`};
const productionBuild=process.argv.includes('--production-build');
const children=[];
let stopping=false;
function stop(code=0){if(stopping)return;stopping=true;for(const child of children)child.kill();process.exitCode=code;}
function launch(binary,args){const child=spawn(binary,args,{env,stdio:'inherit'});children.push(child);child.on('error',error=>{console.error(error.message);stop(1);});child.on('exit',code=>stop(code||0));}
launch(python,['-m','uvicorn','apps.api.main:create_app','--factory','--host','127.0.0.1','--port',String(apiPort),'--no-access-log']);
launch(process.execPath,['node_modules/next/dist/bin/next',productionBuild?'start':'dev','apps/web','--hostname','127.0.0.1','--port',String(port)]);
process.on('SIGINT',()=>stop());process.on('SIGTERM',()=>stop());
