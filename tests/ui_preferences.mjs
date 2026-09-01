import { chromium } from "playwright";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const errors = [];
page.on("pageerror", (error) => errors.push(error.message));

await page.goto("http://host.docker.internal:8080/app");
await page.fill('#login-form input[name="email"]', process.env.TASKFLOW_TEST_EMAIL);
await page.fill('#login-form input[name="password"]', process.env.TASKFLOW_TEST_PASSWORD);
await page.click('#login-form button[type="submit"]');
await page.waitForSelector("#app-view:not(.hidden)");
await page.click('[data-view="profile"]');

const themes = ["forest", "ocean", "coral", "graphite", "sakura"];
const themeColors = [];
for (const theme of themes) {
  await page.click(`[data-theme-choice="${theme}"]`);
  themeColors.push(await page.evaluate(() => getComputedStyle(document.documentElement).getPropertyValue("--forest").trim()));
  await page.screenshot({ path: `/artifacts/theme-${theme}.png`, fullPage: false });
}
if (new Set(themeColors).size !== themes.length) throw new Error("Five themes did not produce distinct primary colors");

await page.click('[data-language="en"]');
await page.waitForFunction(() => document.querySelector('[data-view="dashboard"]')?.textContent.includes("Overview"));
await page.click('[data-language="ja"]');
await page.waitForFunction(() => document.querySelector('[data-view="dashboard"]')?.textContent.includes("タスク概要"));
await page.screenshot({ path: "/artifacts/preferences-ja.png", fullPage: true });

await page.click('[data-view="dashboard"]');
if (!await page.locator("#quick-theme-select").isVisible()) throw new Error("Homepage theme selector is not visible");
if (!await page.locator("#quick-language-select").isVisible()) throw new Error("Homepage language selector is not visible");
for (const theme of themes) {
  await page.selectOption("#quick-theme-select", theme);
  await page.screenshot({ path: `/artifacts/dashboard-theme-${theme}.png`, fullPage: true });
}
await page.screenshot({ path: "/artifacts/dashboard-quick-preferences.png", fullPage: true });
const priorityClasses = await page.locator(".priority-badge").evaluateAll((nodes) => nodes.map((node) => node.className));
if (priorityClasses.some((name) => !/priority-[1-5]/.test(name))) throw new Error("Priority color class missing");
const priorityColors = await page.evaluate(() => {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const colors = [1, 2, 3, 4, 5].map((priority) => {
    const badge = document.createElement("span");
    badge.className = `priority-badge priority-${priority}`;
    host.appendChild(badge);
    return getComputedStyle(badge).backgroundColor;
  });
  host.remove();
  return colors;
});
if (new Set(priorityColors).size !== 5) throw new Error("Priority levels do not have five distinct colors");
await page.setViewportSize({ width: 390, height: 844 });
await page.evaluate(() => document.querySelector(".sidebar").classList.remove("open"));
await page.evaluate(() => window.scrollTo(0, 0));
await page.waitForTimeout(3500);
const sidebarBox = await page.locator(".sidebar").boundingBox();
if (sidebarBox && sidebarBox.x + sidebarBox.width > 1) throw new Error(`Mobile sidebar remained visible at x=${sidebarBox.x}`);
await page.screenshot({ path: "/artifacts/dashboard-mobile-quick-preferences.png", fullPage: false });
await page.click("#menu-button");
await page.click('[data-view="profile"]');
await page.screenshot({ path: "/artifacts/preferences-mobile-ja.png", fullPage: true });
if (errors.length) throw new Error(`Browser errors: ${errors.join("; ")}`);

console.log(JSON.stringify({ themes, themeColors, languages: ["zh", "en", "ja"], priorityClasses, priorityColors }));
await browser.close();
