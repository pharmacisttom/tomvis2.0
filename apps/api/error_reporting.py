"""Safe incident metadata for shared Framework remediation, never exception text."""
import hashlib
import traceback

def incident_metadata(error, version, path):
    frames=traceback.extract_tb(error.__traceback__)
    location=frames[-1].name if frames else 'unknown'
    category=type(error).__name__
    # No exception message, locals, payload, full file path, credentials or PII.
    fingerprint=hashlib.sha256(f'{version}:{category}:{location}:{path}'.encode()).hexdigest()
    return {'fingerprint':fingerprint,'category':category,'component':location,'framework_version':version,'route':path}

def record_incident(db, tenant, request_id, metadata):
    db.execute('INSERT INTO error_reports(tenant_id,fingerprint,category,component,framework_version,route,request_id) VALUES(?,?,?,?,?,?,?) ON CONFLICT(tenant_id,fingerprint) DO UPDATE SET occurrences=occurrences+1,last_seen=CURRENT_TIMESTAMP,request_id=excluded.request_id', (tenant,metadata['fingerprint'],metadata['category'],metadata['component'],metadata['framework_version'],metadata['route'],request_id))
