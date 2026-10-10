import {DatabaseSync} from 'node:sqlite';
import {hashPassword} from '../security/index.js';
import {migrate} from './migrate.js';
export function createDatabase(path,password,migrations) {
 if(!Array.isArray(migrations))throw Error('Application migration list required');
 const db=new DatabaseSync(path);db.exec('PRAGMA foreign_keys=ON; PRAGMA busy_timeout=5000;');
 try {migrate(db,migrations);} catch(error) {db.close();throw error;}
 if(!db.prepare('SELECT id FROM tenants LIMIT 1').get()) {
 db.exec('BEGIN');try {for(const [id,name] of [['demo','Tomvis Demo Workspace'],['other','Isolation Test Workspace']]) db.prepare('INSERT INTO tenants VALUES(?,?)').run(id,name);
 for(const [id,name,email,role] of [['admin','Demo Administrator','admin@tomvis.demo','admin'],['staff','Demo Staff','staff@tomvis.demo','staff'],['viewer','Demo Viewer','viewer@tomvis.demo','viewer']]) {db.prepare('INSERT INTO users(id,email,name,password) VALUES(?,?,?,?)').run(id,email,name,hashPassword(password));db.prepare('INSERT INTO memberships VALUES(?,?,?)').run(id,'demo',role);}
 seed(db,'demo');seed(db,'other');db.exec('COMMIT');}catch(e){db.exec('ROLLBACK');throw e;}}
 return db;
}
export function seed(db,tenant) {for(const [subject,category,status,priority] of [['ปรับปรุงขั้นตอนการให้บริการ','Service','open','high'],['เพิ่มช่องทางติดต่อออนไลน์','Suggestion','in_progress','medium'],['ขอบคุณทีมงานสำหรับการดูแล','Appreciation','resolved','low'],['แจ้งปัญหาการเข้าสู่ระบบ','Technical','open','high'],['เสนอเพิ่มรายงานสรุปรายเดือน','Suggestion','in_progress','medium'],['ประสบการณ์ใช้งานที่ยอดเยี่ยม','Appreciation','resolved','low']])db.prepare('INSERT INTO feedback(tenant_id,subject,category,status,priority) VALUES(?,?,?,?,?)').run(tenant,subject,category,status,priority);}
