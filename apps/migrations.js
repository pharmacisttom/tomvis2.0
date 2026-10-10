// Application composition owns the ordered platform + module migration list.
export const migrations = [
  { version: 1, sql: `
    CREATE TABLE IF NOT EXISTS tenants(id TEXT PRIMARY KEY,name TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,email TEXT UNIQUE NOT NULL,name TEXT NOT NULL,password TEXT NOT NULL,disabled INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS memberships(user_id TEXT REFERENCES users(id),tenant_id TEXT REFERENCES tenants(id),role TEXT NOT NULL,PRIMARY KEY(user_id,tenant_id));
    CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,user_id TEXT REFERENCES users(id),tenant_id TEXT REFERENCES tenants(id),expires_at INTEGER);
    CREATE TABLE IF NOT EXISTS feedback(id INTEGER PRIMARY KEY AUTOINCREMENT,tenant_id TEXT REFERENCES tenants(id),subject TEXT,category TEXT,status TEXT,priority TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS audit_logs(id INTEGER PRIMARY KEY,tenant_id TEXT,actor TEXT,action TEXT,resource TEXT,resource_id TEXT,old_value TEXT,new_value TEXT,ip TEXT,user_agent TEXT,request_id TEXT,timestamp TEXT DEFAULT CURRENT_TIMESTAMP);
  ` },
  { version: 2, sql: `
    CREATE INDEX IF NOT EXISTS feedback_tenant_id ON feedback(tenant_id, id);
    CREATE INDEX IF NOT EXISTS audit_tenant_id ON audit_logs(tenant_id, id);
    CREATE INDEX IF NOT EXISTS sessions_expiry ON sessions(expires_at);
    CREATE INDEX IF NOT EXISTS memberships_tenant_user ON memberships(tenant_id, user_id);
  ` },
  { version: 3, sql: `
    CREATE TABLE IF NOT EXISTS error_reports(
      id INTEGER PRIMARY KEY,tenant_id TEXT NOT NULL REFERENCES tenants(id),fingerprint TEXT NOT NULL,
      category TEXT NOT NULL,component TEXT NOT NULL,framework_version TEXT NOT NULL,route TEXT NOT NULL,
      request_id TEXT NOT NULL,occurrences INTEGER NOT NULL DEFAULT 1,
      first_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,last_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(tenant_id,fingerprint)
    );
    CREATE INDEX IF NOT EXISTS error_reports_tenant_seen ON error_reports(tenant_id,last_seen);
  ` },
];
