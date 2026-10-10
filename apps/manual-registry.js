import {readFileSync} from 'node:fs';
import {buildManual} from '../packages/core/manual.js';
import {VERSION} from '../packages/config/index.js';
const feedback=JSON.parse(readFileSync(new URL('../modules/feedback/manifest.json',import.meta.url),'utf8'));
const platform=JSON.parse(readFileSync(new URL('./manual-sections.json',import.meta.url),'utf8'));
export const manual=buildManual({appName:'Tomvis Framework V3',version:VERSION,modules:[platform,feedback]});
