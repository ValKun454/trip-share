import fs from 'fs';
import path from 'path';
import { FullConfig } from '@playwright/test';

export default async function globalSetup(_config: FullConfig) {
  const logsDir = path.join(__dirname, '..', 'logs');
  if (!fs.existsSync(logsDir)) fs.mkdirSync(logsDir, { recursive: true });
  const stamp = new Date()
    .toISOString()
    .replace(/[:.]/g, '')
    .replace('T', '-')
    .slice(0, 15);
  const logFile = path.join(logsDir, `run-${stamp}.log`);
  process.env.PLAYWRIGHT_RUN_LOG = logFile;
  fs.writeFileSync(logFile, `Playwright run started: ${new Date().toISOString()}\n`, 'utf-8');
}