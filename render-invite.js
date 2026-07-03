const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1080, height: 1920 });
  
  const filePath = path.resolve(__dirname, 'invite-card.html');
  await page.goto(`file://${filePath}`, { waitUntil: 'networkidle', timeout: 30000 });
  
  // Wait for fonts
  await page.waitForTimeout(3000);
  
  await page.screenshot({
    path: path.resolve(__dirname, 'wedding-invite.png'),
    clip: { x: 0, y: 0, width: 1080, height: 1920 },
    type: 'png'
  });
  
  console.log('Done: wedding-invite.png');
  await browser.close();
})();
