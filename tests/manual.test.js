import {test} from 'node:test';
import assert from 'node:assert/strict';
import {buildManual,manualForUser} from '../packages/core/manual.js';
import {manual} from '../apps/manual-registry.js';
import {createDatabase} from '../packages/database/index.js';
import {migrations} from '../apps/migrations.js';
import {createApp} from '../apps/server.js';
test('manual excludes privileged content for viewer and includes permitted feedback guides',()=>{const result=manualForUser(manual,p=>p==='feedback.view');assert(result.sections.some(s=>s.id==='feedback-read'));assert(!result.sections.some(s=>s.id==='sandbox-reset'));assert(!result.sections.some(s=>s.id==='feedback-create'));assert(!result.sections.some(s=>s.id==='audit'));});
test('registered modules require complete and unique guide metadata',()=>{assert.throws(()=>buildManual({appName:'App',version:'1',modules:[{name:'new-module'}]}));const section={id:'same',title:'Guide',permissions:[],steps:['Open page']};assert.throws(()=>buildManual({appName:'App',version:'1',modules:[{name:'one',guide:[section,section]}]}));});
test('manual API enforces authentication and filters sections on server',async t=>{
 const db=createDatabase(':memory:','test-password-long',migrations);const server=createApp(db);await new Promise(r=>server.listen(0,'127.0.0.1',r));t.after(()=>{server.close();db.close();});const origin=`http://127.0.0.1:${server.address().port}`;
 assert.equal((await fetch(origin+'/api/v1/manual')).status,401);
 const login=await fetch(origin+'/api/v1/login',{method:'POST',headers:{Origin:origin,'Content-Type':'application/json'},body:JSON.stringify({email:'viewer@tomvis.demo',password:'test-password-long'})});
 const cookie=login.headers.get('set-cookie').split(';')[0];const response=await fetch(origin+'/api/v1/manual',{headers:{Cookie:cookie}});assert.equal(response.status,200);const guide=(await response.json()).data;
 assert(guide.sections.some(s=>s.id==='feedback-read'));assert(!guide.sections.some(s=>s.id==='sandbox-reset'));assert(!guide.sections.some(s=>s.id==='feedback-create'));
});
