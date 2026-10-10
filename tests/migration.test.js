import { test } from 'node:test';
import assert from 'node:assert/strict';
import { DatabaseSync } from 'node:sqlite';
import { migrate } from '../packages/database/migrate.js';
import { migrations } from '../apps/migrations.js';
import { runtimeConfig } from '../packages/config/index.js';

test('migrations apply once, preserve legacy V2 records, and add indexes', () => {
  const db = new DatabaseSync(':memory:');
  try {
    db.exec('CREATE TABLE migrations(version INTEGER PRIMARY KEY); INSERT INTO migrations VALUES(1)');
    db.exec(migrations[0].sql);
    db.prepare('INSERT INTO tenants VALUES(?,?)').run('existing', 'Existing workspace');
    assert.deepEqual(migrate(db, migrations), [2]);
    assert.deepEqual(migrate(db, migrations), []);
    assert.equal(db.prepare('SELECT name FROM tenants WHERE id=?').get('existing').name, 'Existing workspace');
    assert(db.prepare("SELECT name FROM sqlite_master WHERE name='feedback_tenant_id'").get());
  } finally { db.close(); }
});

test('failed migration rolls back both schema and migration marker', () => {
  const db = new DatabaseSync(':memory:');
  try {
    assert.throws(() => migrate(db, [{version:1,sql:'CREATE TABLE partial(id INTEGER); INSERT INTO missing VALUES(1);'}]));
    assert.equal(db.prepare("SELECT name FROM sqlite_master WHERE name='partial'").get(), undefined);
    assert.equal(db.prepare('SELECT count(*) n FROM migrations').get().n, 0);
  } finally { db.close(); }
});

test('modified or unknown migrations fail closed', () => {
  const db = new DatabaseSync(':memory:');
  try {
    migrate(db, migrations);
    assert.throws(() => migrate(db, [{...migrations[0], sql:migrations[0].sql+' SELECT 1;'},migrations[1]]));
    assert.throws(() => migrate(db, [migrations[0]]));
  } finally { db.close(); }
});

test('configuration rejects unsupported environments and invalid ports', () => {
  const env = {TOMVIS_DEMO_PASSWORD:'test-password-long'};
  assert.equal(runtimeConfig(env).databasePath, 'data/sandbox.sqlite');
  assert.throws(() => runtimeConfig({...env,TOMVIS_MODE:'production'}));
  assert.throws(() => runtimeConfig({...env,PORT:'-1'}));
  assert.throws(() => runtimeConfig({...env,PORT:'abc'}));
  assert.throws(() => runtimeConfig({}));
});
