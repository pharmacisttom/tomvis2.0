'use client';
import {useEffect} from 'react';
export default function GlobalError({reset}){
 useEffect(()=>{fetch('/api/v1/errors/client',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code:'UI_RENDER_ERROR',component:'next-global'})}).catch(()=>{});},[]);
 return <html lang="th"><body><h1>ระบบแสดงผลขัดข้อง</h1><p>กรุณาลองใหม่หรือติดต่อผู้ดูแลระบบ</p><button onClick={reset}>ลองใหม่</button></body></html>;
}
