"""SQLite adapter compatible with the existing alpha database and Node hashes."""
import hashlib
import hmac
import json
import secrets
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def contracts():
    return json.loads((ROOT / 'docs/generated/runtime-contracts.json').read_text(encoding='utf-8'))

def hash_password(password):
    salt = secrets.token_hex(16)
    key = hashlib.scrypt(password.encode(), salt=salt.encode(), n=16384, r=8, p=1, dklen=64, maxmem=67108864)
    return f'{salt}:{key.hex()}'

def verify_password(password, stored):
    try:
        salt, expected = stored.split(':')
        actual = hashlib.scrypt(password.encode(), salt=salt.encode(), n=16384, r=8, p=1, dklen=64, maxmem=67108864)
        return hmac.compare_digest(actual, bytes.fromhex(expected))
    except (ValueError, TypeError):
        return False

def seed(db, tenant):
    rows = [('ปรับปรุงขั้นตอนการให้บริการ','Service','open','high'),('เพิ่มช่องทางติดต่อออนไลน์','Suggestion','in_progress','medium'),('ขอบคุณทีมงานสำหรับการดูแล','Appreciation','resolved','low'),('แจ้งปัญหาการเข้าสู่ระบบ','Technical','open','high'),('เสนอเพิ่มรายงานสรุปรายเดือน','Suggestion','in_progress','medium'),('ประสบการณ์ใช้งานที่ยอดเยี่ยม','Appreciation','resolved','low')]
    db.executemany('INSERT INTO feedback(tenant_id,subject,category,status,priority) VALUES(?,?,?,?,?)', [(tenant,*row) for row in rows])

def open_database(path, password):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('PRAGMA busy_timeout=5000')
    try:
        db.execute('CREATE TABLE IF NOT EXISTS migrations(version INTEGER PRIMARY KEY)')
        if 'checksum' not in [row['name'] for row in db.execute('PRAGMA table_info(migrations)')]:
            db.execute('ALTER TABLE migrations ADD COLUMN checksum TEXT')
        db.commit()
        migrations = contracts()['migrations']
        applied = {row['version']:row['checksum'] for row in db.execute('SELECT * FROM migrations')}
        if set(applied)-{item['version'] for item in migrations}:
            raise ValueError('Unknown migration version')
        for item in migrations:
            checksum = hashlib.sha256(item['sql'].encode()).hexdigest()
            if item['version'] in applied:
                if applied[item['version']] not in (checksum, None) or (applied[item['version']] is None and item['version'] != 1):
                    raise ValueError('Migration checksum mismatch')
                continue
            with db:
                # Do not use executescript: it implicitly commits the transaction.
                db.execute('BEGIN IMMEDIATE')
                for statement in item['sql'].split(';'):
                    if statement.strip(): db.execute(statement)
                db.execute('INSERT INTO migrations(version,checksum) VALUES(?,?)', (item['version'],checksum))
        if not db.execute('SELECT id FROM tenants LIMIT 1').fetchone():
            with db:
                db.executemany('INSERT INTO tenants VALUES(?,?)',[('demo','Tomvis Demo Workspace'),('other','Isolation Test Workspace')])
                for uid,name,email,role in [('admin','Demo Administrator','admin@tomvis.demo','admin'),('staff','Demo Staff','staff@tomvis.demo','staff'),('viewer','Demo Viewer','viewer@tomvis.demo','viewer')]:
                    db.execute('INSERT INTO users(id,email,name,password) VALUES(?,?,?,?)',(uid,email,name,hash_password(password)))
                    db.execute('INSERT INTO memberships VALUES(?,?,?)',(uid,'demo',role))
                seed(db,'demo')
                seed(db,'other')
        return db
    except Exception:
        db.close()
        raise
