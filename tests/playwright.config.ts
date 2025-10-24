import { defineConfig, devices } from '@playwright/test';
import path from 'path';

const repoRoot = 'C:/TripShare/trip-share-1';

export default defineConfig({
  testDir: path.join(__dirname, 'e2e'),
  timeout: 30_000,
  expect: { timeout: 10_000 },
  fullyParallel: true,
  reporter: [
    ['list'],
    ['html', { outputFolder: path.join(__dirname, 'artifacts', 'html-report'), open: 'never' }],
    ['json', { outputFile: path.join(__dirname, 'artifacts', 'results.json') }],
    ['junit', { outputFile: path.join(__dirname, 'artifacts', 'junit-results.xml') }]
  ],
  outputDir: path.join(__dirname, 'artifacts', 'test-results'),
  use: {
    baseURL: 'http://localhost:4200',
    trace: 'on',
    screenshot: 'on',
    video: 'off',
    actionTimeout: 10_000,
    navigationTimeout: 15_000,
  },
  webServer: {
    command: 'cmd /c npm start',
    cwd: path.join(repoRoot, 'frontend'),
    url: 'http://localhost:4200',
    reuseExistingServer: true,
    timeout: 180_000
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } }
  ],
  globalSetup: path.join(__dirname, 'utils', 'global-setup.ts'),
});
