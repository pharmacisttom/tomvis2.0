'use client';
import {useEffect,useState} from 'react';
export default function ErrorBoundary({reset}){
 const [reference,setReference]=useState('');
 useEffect(()=>{fetch('/api/v1/errors/client',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code:'UI_RENDER_ERROR',component:'next-page'})}).then(r=>r.json()).then(j=>setReference(j.meta?.request_id||'')).catch(()=>{});},[]);
 return <div className="login"><section className="card"><h1>ไม่สามารถแสดงหน้านี้ได้</h1><p>กรุณาลองอีกครั้ง หากปัญหายังเกิดอยู่ ให้แจ้งผู้ดูแลพร้อมรหัสอ้างอิง</p>{reference&&<p>Request ID: {reference}</p>}<button onClick={reset}>ลองใหม่</button></section></div>;
}
