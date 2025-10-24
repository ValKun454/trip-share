import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const logFile = process.env.PLAYWRIGHT_RUN_LOG || path.join(__dirname, '..', 'logs', `run.log`);

function append(line: string) {
  try {
    fs.appendFileSync(logFile, line + '\n', 'utf-8');
  } catch {}
}

test.beforeEach(async ({ page }, testInfo) => {
  append(`\n=== TEST START: ${testInfo.title} ===`);
  page.on('console', (msg) => append(`[console:${msg.type()}] ${msg.text()}`));
  page.on('request', (req) => append(`[request] ${req.method()} ${req.url()}`));
  page.on('response', async (res) => append(`[response] ${res.status()} ${res.url()}`));
});

test.afterEach(async ({}, testInfo) => {
  append(`=== TEST END: ${testInfo.title} | status=${testInfo.status} ===`);
});

test('home page shows greeting', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /Hello,\s*trip-share-frontend/i })).toBeVisible();
  await expect(page.getByText('Congratulations! Your app is running.')).toBeVisible();
});
