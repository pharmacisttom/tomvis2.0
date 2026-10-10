"""Domain-neutral tabular reporting. Never executes user-supplied SQL."""
from collections import Counter
from datetime import datetime, timezone

def render_report(dataset, rows, request, workspace, total):
    columns = request.get('columns') or list(dataset['columns'])
    if not isinstance(columns,list) or not columns or len(set(columns))!=len(columns) or any(c not in dataset['columns'] for c in columns):
        raise ValueError('Invalid report columns')
    title = request.get('title') or dataset['name']
    if not isinstance(title,str) or not 1<=len(title.strip())<=160: raise ValueError('Invalid report title')
    group = request.get('groupBy') or None
    if group and group not in dataset.get('groupable',[]): raise ValueError('Invalid grouping column')
    return {'title':title.strip(),'workspace':workspace,'source':dataset['id'],'generatedAt':datetime.now(timezone.utc).isoformat(),'columns':[{'key':c,'label':dataset['columns'][c]} for c in columns],'rows':[{c:row.get(c) for c in columns} for row in rows],'summary':{'total':total,'returned':len(rows),'truncated':total>len(rows),'groups':dict(Counter(str(row[group]) for row in rows)) if group else {},'groupCoverage':'returned_rows'},'filters':request.get('filters',{}),'formats':['csv','print']}
