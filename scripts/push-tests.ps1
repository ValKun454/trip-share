<#
.SYNOPSIS
  Commit and push to the 'tests' branch on origin (Windows PowerShell).

.DESCRIPTION
  - Ensures we're in the repo root.
  - Optionally stages all changes and creates a commit.
  - Pushes the current branch to origin/tests and sets upstream on first push.
  - Supports --dry-run and --force-with-lease.

.PARAMETER Message
  Commit message. If omitted and -AddAll is used with changes, a timestamped message is generated.

.PARAMETER AddAll
  Stage all modified/untracked files before committing. Default: true.

.PARAMETER NoCommit
  Do not create a commit; push existing commits only.

.PARAMETER DryRun
  Simulate push without sending any data to the remote.

.PARAMETER Force
  Use --force-with-lease for the push.

.PARAMETER SwitchToTests
  If current branch is not 'tests', switch to it (create from origin/front-dev if missing).

.EXAMPLES
  # Dry-run: see exactly where push would go
  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\push-tests.ps1 -DryRun

  # Add all, commit with message, push to origin/tests
  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\push-tests.ps1 -Message "feat: my changes"

  # Push without creating a commit
  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\push-tests.ps1 -NoCommit
#>
[CmdletBinding()]
param(
  [string]$Message,
  [switch]$AddAll = $true,
  [switch]$NoCommit,
  [switch]$DryRun,
  [switch]$Force,
  [switch]$SwitchToTests
)

$ErrorActionPreference = 'Stop'

function Write-Info($msg)  { Write-Host "[info]  $msg" -ForegroundColor Cyan }
function Write-Warn($msg)  { Write-Host "[warn]  $msg" -ForegroundColor Yellow }
function Write-Ok($msg)    { Write-Host "[ok]    $msg" -ForegroundColor Green }
function Write-Fail($msg)  { Write-Host "[fail]  $msg" -ForegroundColor Red }

# Move to repo root (the script sits in /scripts)
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
Set-Location $repoRoot
Write-Info "Repo root: $repoRoot"

# Ensure git is available
try { git --version | Out-Null } catch { Write-Fail 'Git is not available in PATH'; exit 1 }

# Current branch
$branch = (git rev-parse --abbrev-ref HEAD).Trim()
Write-Info "Current branch: $branch"

if ($branch -ne 'tests') {
  if ($SwitchToTests) {
    Write-Info "Switching to 'tests'..."
    $existsLocal = $false
    try { git show-ref --verify --quiet refs/heads/tests; $existsLocal = $true } catch { $existsLocal = $false }
    if (-not $existsLocal) {
      Write-Info "Local 'tests' not found. Checking origin/front-dev..."
      $hasFrontDev = git ls-remote --heads origin front-dev | Select-String 'refs/heads/front-dev'
      if ($hasFrontDev) {
        git checkout -b tests origin/front-dev | Out-Null
      } else {
        Write-Warn "origin/front-dev not found; creating 'tests' from current branch '$branch'"
        git checkout -b tests | Out-Null
      }
    } else {
      git checkout tests | Out-Null
    }
    $branch = 'tests'
    Write-Ok "Now on 'tests'"
  } else {
    Write-Fail "You are on '$branch'. Use -SwitchToTests to switch automatically, or checkout 'tests' manually. Aborting."
    exit 1
  }
}

# Remote validation
$originUrl = (git remote get-url origin)
Write-Info "origin: $originUrl"

# Stage + commit (unless NoCommit)
if (-not $NoCommit) {
  $status = git status --porcelain
  if ($AddAll) {
    git add -A | Out-Null
    $status = git status --porcelain
  }
  if ($status) {
    if (-not $Message) { $Message = "chore: auto-commit $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" }
    Write-Info "Creating commit: $Message"
    git commit -m $Message | Out-Null
  } else {
    Write-Info 'No changes to commit.'
  }
}

# Determine if upstream exists
$hasUpstream = $true
try { git rev-parse --abbrev-ref --symbolic-full-name '@{u}' | Out-Null } catch { $hasUpstream = $false }

# Build push command
$pushArgs = @('push')
if ($DryRun) { $pushArgs += '--dry-run' }
if ($Force) { $pushArgs += '--force-with-lease' }

if (-not $hasUpstream) {
  Write-Info "No upstream set; will push with -u to origin/tests"
  $pushArgs += @('-u','origin','tests')
} else {
  # Ensure we push to origin/tests explicitly
  $pushArgs += @('origin','HEAD:tests')
}

Write-Info ("Executing: git " + ($pushArgs -join ' '))
& git @pushArgs
if ($LASTEXITCODE -ne 0) { Write-Fail "Push failed."; exit $LASTEXITCODE }
Write-Ok 'Push completed.'
