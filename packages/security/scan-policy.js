// Policy validation only. This module never contacts a target or launches a scanner.
// Policy/authorization inputs must come from trusted server-side records.
export function authorizeScan(context, policy, request, now = Date.now()) {
  if (!context?.permissions?.includes('security.scan')) throw new Error('Scan permission required');
  if (!policy || policy.tenantId !== context.tenantId) throw new Error('Tenant mismatch');
  if (!['sandbox', 'staging', 'production'].includes(policy.environment)) throw new Error('Invalid scan environment');
  if (!['passive', 'active'].includes(request?.mode)) throw new Error('Invalid scan mode');
  if (!policy.enabled) throw new Error('Scanning disabled');
  const approval = policy.authorization;
  if (!approval?.approvedBy || !Number.isFinite(approval.expiresAt) || now >= approval.expiresAt) throw new Error('Current target-owner authorization required');
  if (!Number.isFinite(approval.startsAt) || now < approval.startsAt) throw new Error('Outside authorized scan window');
  if (policy.environment === 'production' && request.mode !== 'passive') throw new Error('Production active scans prohibited by default policy');
  if (request.mode === 'active' && !policy.allowActive) throw new Error('Active scan not permitted');
  if (!Array.isArray(policy.allowedOrigins) || !policy.allowedOrigins.length) throw new Error('Target allowlist required');
  const target = new URL(request.target);
  if (target.protocol !== 'https:' || target.username || target.password || target.hash || target.search || target.pathname !== '/') throw new Error('Target must be an HTTPS origin without credentials');
  if (!policy.allowedOrigins.includes(target.origin) || !approval.origins?.includes(target.origin)) throw new Error('Target outside authorized scope');
  if (!Number.isInteger(policy.requestsPerMinute) || policy.requestsPerMinute < 1 || policy.requestsPerMinute > 60) throw new Error('Invalid request rate');
  if (!Number.isInteger(policy.maxDurationSeconds) || policy.maxDurationSeconds < 1 || policy.maxDurationSeconds > 900) throw new Error('Invalid scan duration');
  return Object.freeze({tenantId:context.tenantId,actorId:context.userId,environment:policy.environment,target:target.origin,mode:request.mode,requestsPerMinute:policy.requestsPerMinute,maxDurationSeconds:Math.min(policy.maxDurationSeconds,Math.floor((approval.expiresAt-now)/1000))});
}
