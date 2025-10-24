param(
  [switch]$OpenBrowser
)

$ErrorActionPreference = 'Stop'

$repoRoot = "C:\TripShare\trip-share-1"
Set-Location $repoRoot

# Ensure and activate Python venv (backend dependencies stay inside .venv)
if (-not (Test-Path .\.venv\Scripts\Activate.ps1)) {
  try { py -3 -m venv .venv } catch { python -m venv .venv }
}
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
. .\.venv\Scripts\Activate.ps1

# Install/refresh backend deps (safe to re-run; fast if already satisfied)
& .\.venv\Scripts\python.exe -m pip install --upgrade pip > $null 2>&1
& .\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt

# Start backend (uvicorn) in background
$backend = Start-Process -FilePath .\.venv\Scripts\python.exe -ArgumentList @('-m','uvicorn','backend.main:app','--host','0.0.0.0','--port','8000','--reload') -WorkingDirectory $repoRoot -PassThru -WindowStyle Minimized

# Start frontend (Angular) in background
$npm = "C:\\Program Files\\nodejs\\npm.cmd"
if (-not (Test-Path $npm)) { throw "npm not found at $npm" }
Set-Location .\frontend
& $npm install
$frontend = Start-Process -FilePath $npm -ArgumentList @('start') -WorkingDirectory (Get-Location).Path -PassThru -WindowStyle Minimized
Set-Location $repoRoot

Write-Host "Backend PID: $($backend.Id) | Frontend PID: $($frontend.Id)"

# Optional: wait for readiness briefly and open browser
function Test-Url($url) { try { (Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2).StatusCode -ge 200 } catch { $false } }
$deadline = (Get-Date).AddMinutes(2)
$okBack = $false; $okFront = $false
while ((Get-Date) -lt $deadline -and (-not ($okBack -and $okFront))) {
  if (-not $okBack) { $okBack = Test-Url 'http://localhost:8000/api/' }
  if (-not $okFront) { $okFront = Test-Url 'http://localhost:4200/' }
  Start-Sleep -Seconds 2
}

if ($okBack -and $okFront) {
  Write-Host "Servers are up: http://localhost:8000/api/ | http://localhost:4200/"
  if ($OpenBrowser) { Start-Process "http://localhost:4200" }
} else {
  Write-Warning "Servers may still be starting. Check terminals if needed."
}
