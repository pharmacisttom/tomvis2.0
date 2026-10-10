export function buildManual({appName,version,modules}) {
  if(!appName || !version || !Array.isArray(modules)) throw Error('Manual requires app metadata and registered modules');
  const ids=new Set();
  const sections=[];
  for(const module of modules) {
    if(!module.name || !Array.isArray(module.guide) || !module.guide.length) throw Error(`Module ${module.name||'unknown'} requires a user guide`);
    for(const entry of module.guide) {
      if(!entry.id || ids.has(entry.id) || !entry.title || !Array.isArray(entry.steps) || !entry.steps.length || entry.steps.some(s=>typeof s!=='string'||!s.trim()) || !Array.isArray(entry.permissions) || entry.permissions.some(p=>typeof p!=='string')) throw Error('Invalid or duplicate manual section');
      ids.add(entry.id);
      sections.push({id:entry.id,module:module.name,title:entry.title,permissions:[...entry.permissions],steps:[...entry.steps]});
    }
  }
  return {appName,version,sections};
}
export function manualForUser(manual,hasPermission) {
  return {...manual,sections:manual.sections.filter(section=>section.permissions.every(hasPermission)).map(({permissions,...section})=>section)};
}
