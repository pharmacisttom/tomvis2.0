import { createHash } from 'node:crypto';

// The runner receives module-owned migrations; core never imports domain SQL.
export function migrate(db, migrations) {
  db.exec('CREATE TABLE IF NOT EXISTS migrations(version INTEGER PRIMARY KEY)');
  const columns = db.prepare('PRAGMA table_info(migrations)').all();
  if (!columns.some(column => column.name === 'checksum')) {
    db.exec('ALTER TABLE migrations ADD COLUMN checksum TEXT');
  }
  const versions = new Set();
  let previous = 0;
  for (const migration of migrations) {
    if (!Number.isInteger(migration.version) || migration.version <= previous || versions.has(migration.version) || typeof migration.sql !== 'string' || !migration.sql.trim()) {
      throw new Error('Migrations must have unique ascending positive versions and SQL');
    }
    versions.add(migration.version);
    previous = migration.version;
  }
  const applied = db.prepare('SELECT version, checksum FROM migrations ORDER BY version').all();
  if (applied.some(row => !versions.has(row.version))) throw new Error('Database has an unknown migration version');
  const completed = [];
  for (const migration of migrations) {
    const checksum = createHash('sha256').update(migration.sql).digest('hex');
    const existing = applied.find(row => row.version === migration.version);
    if (existing) {
      if (existing.checksum && existing.checksum !== checksum) throw new Error(`Migration ${migration.version} was changed after application`);
      // V2 recorded only version 1. Preserve its legacy marker without claiming
      // that an unverifiable historical SQL body has been checksum-validated.
      if (!existing.checksum && migration.version !== 1) throw new Error('Missing migration checksum');
      continue;
    }
    db.exec('BEGIN IMMEDIATE');
    try {
      db.exec(migration.sql);
      db.prepare('INSERT INTO migrations(version, checksum) VALUES(?, ?)').run(migration.version, checksum);
      db.exec('COMMIT');
      completed.push(migration.version);
    } catch (error) {
      db.exec('ROLLBACK');
      throw error;
    }
  }
  return completed;
}
