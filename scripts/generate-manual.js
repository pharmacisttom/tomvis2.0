import {mkdirSync,writeFileSync} from 'node:fs';
import {manual} from '../apps/manual-registry.js';
mkdirSync('docs/generated',{recursive:true});
const sections=manual.sections.map(s=>`## ${s.title}\n\nRequired permissions: ${s.permissions.join(', ')||'Signed-in users'}\n\n${s.steps.map((step,i)=>`${i+1}. ${step}`).join('\n')}`).join('\n\n');
writeFileSync('docs/generated/USER_MANUAL.md',`# ${manual.appName} — คู่มือการใช้งาน\n\nVersion: ${manual.version}\n\nGenerated from registered module guides. In-app sections are filtered by server-side permissions.\n\n${sections}\n`);
console.log(`Generated ${manual.sections.length} manual sections`);
