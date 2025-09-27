const puppeteer = require('puppeteer');
const path = require('path');
(async () => {
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox','--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  page.on('console', msg => console.log('PAGE_CONSOLE:', msg.text()));
  page.on('response', res => console.log('PAGE_RESPONSE:', res.status(), res.url()));
  page.on('requestfailed', req => console.log('PAGE_REQ_FAILED:', req.url(), req.failure()));

  await page.goto('http://localhost:5173', { waitUntil: 'networkidle0' });
  const input = await page.$('input[type=file]');
  if (!input) {
    console.error('No file input found');
    await browser.close();
    process.exit(2);
  }
  const filePath = path.resolve(process.env.HOME, 'Downloads/stories.zip');
  console.log('Uploading', filePath);
  await input.uploadFile(filePath);
  await page.waitForTimeout(3000);
  await page.screenshot({ path: '/tmp/upload_test.png', fullPage: true });
  console.log('Screenshot saved to /tmp/upload_test.png');
  await browser.close();
})();
