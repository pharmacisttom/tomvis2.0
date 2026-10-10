const {chromium}=require('playwright');
const {mkdir,readFile}=require('node:fs/promises');
const assert=require('node:assert/strict');
const origin=process.argv[2];
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  await mkdir('artifacts/ui',{recursive:true});
  const context=await browser.newContext({viewport:{width:1440,height:900}});
  const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(origin);
  await page.getByLabel('อีเมล',{exact:true}).fill('admin@tomvis.demo');
  await page.getByLabel('รหัสผ่าน',{exact:true}).fill('integration-test-password');
  await page.getByRole('button',{name:'เข้าสู่ระบบ →',exact:true}).click();
  await page.getByRole('button',{name:'Dashboard',exact:true}).waitFor();
  await page.screenshot({path:'artifacts/ui/dashboard-desktop.png',fullPage:true});
  await page.getByRole('button',{name:'＋ New feedback',exact:true}).click();
  await page.getByLabel('หัวข้อ',{exact:true}).fill('=FORMULA_TEST');
  await page.getByRole('button',{name:'บันทึก',exact:true}).click();
  await page.getByRole('dialog').waitFor({state:'hidden'});
  await page.getByRole('button',{name:'คู่มือการใช้งาน',exact:true}).click();
  await page.getByLabel('ค้นหาคู่มือ').fill('รายงาน');
  await page.getByRole('heading',{name:'สร้างรายงาน ส่งออก และสั่งพิมพ์',exact:true}).waitFor();
  await page.getByRole('button',{name:'Reports',exact:true}).click();
  await page.getByRole('button',{name:'สร้างรายงาน',exact:true}).click();
  await page.locator('article.print-report').waitFor();
  const downloadPromise=page.waitForEvent('download');
  await page.getByRole('button',{name:'ส่งออก CSV',exact:true}).click();
  const download=await downloadPromise;const csv=await readFile(await download.path(),'utf8');
  assert(csv.includes("'=FORMULA_TEST"),'CSV formula prefix must be neutralized');
  await page.screenshot({path:'artifacts/ui/report-desktop.png',fullPage:true});
  for(const width of [360,390,768,1024,1440]){
   await page.setViewportSize({width,height:900});
   const sizes=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,width:innerWidth}));
   assert(sizes.scroll<=sizes.width+1,`Viewport overflow at ${width}: ${JSON.stringify(sizes)}`);
   if(width===390)await page.screenshot({path:'artifacts/ui/report-mobile.png',fullPage:true});
  }
  await page.emulateMedia({media:'print'});
  await page.pdf({path:'artifacts/ui/report-print.pdf',format:'A4',landscape:true,printBackground:true});
  const hidden=await page.locator('.sidebar').evaluate(el=>getComputedStyle(el).display);
  assert.equal(hidden,'none');assert.equal(errors.length,0,errors.join('\n'));
  console.log('PASS: React login, create Feedback, manual search, report CSV, formula protection, responsive widths, print PDF and no JS runtime errors');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
