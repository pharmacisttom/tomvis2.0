# Tomvis Framework V3 — คู่มือการใช้งาน

Version: 3.0.0-alpha.1

Generated from registered module guides. In-app sections are filtered by server-side permissions.

## เริ่มต้นใช้งาน

Required permissions: Signed-in users

1. เข้าสู่ระบบด้วยอีเมลและรหัสผ่านที่ผู้ดูแลกำหนด
2. ตรวจชื่อ Workspace และป้าย Environment ด้านบนก่อนทำงาน
3. เลือกเมนูจาก Sidebar บนมือถือกดปุ่ม ☰ เพื่อเปิดเมนู
4. เมื่อเสร็จงานกด ออกจากระบบ

## อ่าน Dashboard

Required permissions: feedback.view

1. เลือก Dashboard เพื่อดูจำนวน Feedback ใน Workspace ปัจจุบัน
2. ตรวจรายการ Open, In progress และ Resolved
3. กด View all เพื่อเปิดรายการ Feedback ทั้งหมด

## ดูรายชื่อผู้ใช้งาน

Required permissions: users.view

1. เลือก Users ใน Sidebar
2. ตรวจชื่อ อีเมล บทบาท และสถานะบัญชี
3. Alpha นี้แสดงรายชื่อเท่านั้น ยังไม่มีหน้าจอเพิ่มหรือแก้ไขบัญชี

## ตรวจประวัติการทำงาน

Required permissions: audit.view

1. เลือก Audit logs
2. ตรวจ Action, Actor, Resource และเวลาที่เกิดเหตุการณ์
3. ข้อมูลแสดงเฉพาะ Workspace ของบัญชีที่เข้าสู่ระบบ

## คืนค่า Sandbox

Required permissions: sandbox.reset

1. เลือก Sandbox และตรวจว่ากำลังใช้งานพื้นที่ทดลอง
2. กด Reset sandbox แล้วอ่านผลกระทบในหน้าต่างยืนยัน
3. กดยืนยัน Reset เพื่อแทนที่ Feedback ทดลองด้วยข้อมูลเริ่มต้น
4. บัญชีผู้ใช้และ Audit ยังคงอยู่หลัง Reset

## สร้างรายงาน ส่งออก และสั่งพิมพ์

Required permissions: feedback.view

1. เลือก Reports แล้วเลือกแหล่งข้อมูลที่มีสิทธิ์
2. กรอกชื่อรายงานและตัวกรอง แล้วกด สร้างรายงาน
3. ตรวจจำนวนทั้งหมดและคำเตือนกรณีข้อมูลถูกจำกัด
4. กด ส่งออก CSV หรือ พิมพ์ / บันทึก PDF
5. ระบบบัญชีและ HR จะแสดงเมื่อเชื่อม Report Adapter จริงแล้ว

## ตรวจข้อผิดพลาด Framework

Required permissions: audit.view

1. เลือก System errors เพื่อดูข้อผิดพลาดที่บันทึกใน Workspace
2. ตรวจประเภท จำนวนครั้ง เวอร์ชัน Framework และ Request ID
3. ใช้ fingerprint และเวอร์ชันเพื่อจัดกลุ่มปัญหาที่ควรแก้ใน Core
4. ระบบยังไม่ส่งรายงานจาก VPS ลูกค้ามาศูนย์กลางโดยอัตโนมัติ

## ค้นหาและดู Feedback

Required permissions: feedback.view

1. เลือก Feedback ใน Sidebar
2. พิมพ์หัวข้อในช่องค้นหา หรือเลือกสถานะจาก All status
3. ตรวจหมวดหมู่ ความสำคัญ และสถานะของรายการ

## เพิ่ม Feedback

Required permissions: feedback.manage

1. กด New feedback บน Dashboard หรือ Feedback
2. กรอกหัวข้อ เลือกหมวดหมู่และความสำคัญ
3. กด บันทึก Feedback และตรวจว่ารายการใหม่แสดงในตาราง

## ปิดงาน Feedback

Required permissions: feedback.manage

1. เปิดรายการ Feedback ที่ต้องการดำเนินการ
2. กด Resolve เพื่อเปลี่ยนสถานะเป็น Resolved
3. ตรวจสถานะในตารางและจำนวนรายการบน Dashboard
