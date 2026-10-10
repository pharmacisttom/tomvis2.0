DATASETS = [
    {'id':'feedback','name':'รายงาน Feedback','permission':'feedback.view','columns':{'id':'รหัส','subject':'หัวข้อ','category':'หมวดหมู่','status':'สถานะ','priority':'ความสำคัญ','created_at':'วันที่สร้าง'},'groupable':['category','status','priority']},
    {'id':'users','name':'รายงานผู้ใช้งาน','permission':'users.view','columns':{'name':'ชื่อ','email':'อีเมล','role':'บทบาท','disabled':'ปิดใช้งาน'},'groupable':['role','disabled']},
]

def load_rows(db,dataset,tenant,filters):
    if not isinstance(filters,dict) or set(filters)-{'q','status'}: raise ValueError('Invalid report filters')
    q=filters.get('q','')
    if not isinstance(q,str) or len(q)>200: raise ValueError('Invalid search')
    if dataset['id']=='feedback':
        status=filters.get('status','')
        if status not in ('','open','in_progress','resolved'): raise ValueError('Invalid status')
        clause='tenant_id=? AND subject LIKE ?'
        params=[tenant,f'%{q}%']
        if status: clause+=' AND status=?';params.append(status)
        total=db.execute('SELECT count(*) n FROM feedback WHERE '+clause,params).fetchone()['n']
        rows=db.execute('SELECT id,subject,category,status,priority,created_at FROM feedback WHERE '+clause+' ORDER BY id DESC LIMIT 1000',params).fetchall()
    else:
        if filters.get('status'): raise ValueError('Status filter not supported')
        clause='m.tenant_id=? AND u.name LIKE ?'
        params=[tenant,f'%{q}%']
        total=db.execute('SELECT count(*) n FROM users u JOIN memberships m ON m.user_id=u.id WHERE '+clause,params).fetchone()['n']
        rows=db.execute('SELECT u.name,u.email,m.role,u.disabled FROM users u JOIN memberships m ON m.user_id=u.id WHERE '+clause+' ORDER BY u.name,u.id LIMIT 1000',params).fetchall()
    return [dict(row) for row in rows],total
