# TripShare Frontend

Single-page application built with **Angular (standalone)** and **Angular Material**.  
Backend (FastAPI) is expected at `http://localhost:8000/api`.

## Quick Start

1. **Install Node.js (LTS)**
   - Download from https://nodejs.org (LTS).
   - Verify versions:
     ```bash
     node -v
     npm -v
     ```
   - If `node`/`npm` is “not found”, reopen the terminal or add Node.js to PATH.

2. **Install dependencies**
   ```bash
   cd frontend
   npm ci      # or: npm install
````

3. **Start the dev server**

   ```bash
   npm start
   ```

   Open `http://localhost:4200/`.

   > If you see `ng: command not found`:
   >
   > * You **do not** need a global Angular CLI. Use:
   >
   >   ```bash
   >   npx ng serve
   >   ```
   > * On Windows PowerShell with script-execution errors:
   >
   >   ```powershell
   >   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
   >   npx ng serve
   >   ```

4. **API base URL**

   * Configured in `src/app/core/services/api.service.ts`:

     ```ts
     private base = 'http://localhost:8000/api';
     ```
   * Adjust if your backend runs elsewhere.

---

## Scripts

```bash
npm start     # run dev server (ng serve)
npm run build # production build (outputs to dist/)
```

---

## Routes

* `/login`, `/register`
* `/trips`, `/expenses`, `/profile`, `/contact`
* `/**` → 404

Guards: `noAuthGuard` (public), `authGuard` (protected).
