$ErrorActionPreference = 'Stop'

$repoRoot = "C:\TripShare\trip-share-1"
$git = Join-Path $env:ProgramFiles 'Git\cmd\git.exe'
if (-not (Test-Path $git)) { throw "Git not found at $git" }

Set-Location $repoRoot

# Ordinary pull of current branch with rebase to keep history linear
& $git pull --rebase
if ($LASTEXITCODE -ne 0) { throw "git pull failed" }

Write-Host "Pull complete."
