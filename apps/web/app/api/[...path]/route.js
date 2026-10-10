const upstream=new URL(process.env.TOMVIS_API_URL||'http://127.0.0.1:8000');
if(upstream.protocol!=='http:'||!['127.0.0.1','localhost'].includes(upstream.hostname)||upstream.username||upstream.password||upstream.pathname!=='/'||upstream.search||upstream.hash)throw Error('Invalid backend origin');
export const dynamic='force-dynamic';
async function forward(request,{params}){
 const {path}=await params;
 if(!path.every(p=>/^[a-zA-Z0-9_-]+$/.test(p)))return Response.json({success:false,error:{code:'NOT_FOUND',message:'Not found'}},{status:404});
 const headers=new Headers();for(const key of ['cookie','origin','content-type','sec-fetch-site','user-agent']){const value=request.headers.get(key);if(value)headers.set(key,value);}
 let body;
 if(!['GET','HEAD'].includes(request.method)){
  const reader=request.body?.getReader();const chunks=[];let size=0;
  if(reader){while(true){const {done,value}=await reader.read();if(done)break;size+=value.length;if(size>16384){await reader.cancel();return Response.json({success:false,error:{code:'TOO_LARGE',message:'Request too large'}},{status:413});}chunks.push(value);}}
  body=Buffer.concat(chunks);
 }
 try{
  const response=await fetch(new URL('/api/'+path.join('/')+new URL(request.url).search,upstream),{method:request.method,headers,body,cache:'no-store',redirect:'error',signal:AbortSignal.timeout(15000)});
  const output=new Headers({'Content-Type':'application/json','Cache-Control':'no-store'});for(const key of ['set-cookie','x-request-id']){const value=response.headers.get(key);if(value)output.set(key,value);}
  return new Response(response.body,{status:response.status,headers:output});
 }catch{return Response.json({success:false,error:{code:'BACKEND_UNAVAILABLE',message:'บริการ Backend ยังไม่พร้อมใช้งาน'}},{status:503});}
}
export {forward as GET,forward as POST,forward as PATCH,forward as DELETE};
