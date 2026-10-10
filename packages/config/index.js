export const VERSION = '3.0.0-alpha.1';
export function runtimeConfig(env = process.env) {
  const mode = env.TOMVIS_MODE || 'sandbox';
  if (!['sandbox', 'demo', 'development'].includes(mode)) throw new Error('This alpha permits local sandbox/demo/development only');
  const port = Number(env.PORT || 3000);
  if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error('PORT must be an integer from 1 to 65535');
  const password = env.TOMVIS_DEMO_PASSWORD;
  if (typeof password !== 'string' || password.length < 12 || password.length > 256) throw new Error('Set TOMVIS_DEMO_PASSWORD to 12–256 characters');
  return Object.freeze({ mode, port, password, databasePath: `data/${mode}.sqlite`, host: '127.0.0.1' });
}
