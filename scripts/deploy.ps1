# deploy.ps1 — Deploy Peyo Agent to Ubuntu server at 192.168.1.203
# Usage: .\scripts\deploy.ps1
# Requires: OpenSSH client (built into Windows 10/11)

param(
    [string]$Server    = "192.168.1.203",
    [string]$User      = "dphoompat",
    [string]$RemoteDir = "/home/dphoompat/peyo-agent",
    [string]$KeyFile   = "$env:USERPROFILE\.ssh\id_ubuntu_local",
    [switch]$FirstTime
)

$ErrorActionPreference = "Stop"
$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$SSH_OPTS   = @("-i", $KeyFile, "-o", "StrictHostKeyChecking=accept-new")
$SCP_OPTS   = @("-i", $KeyFile, "-o", "StrictHostKeyChecking=accept-new", "-q")

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Peyo Agent — Deploy to $User@$Server" -ForegroundColor Cyan
Write-Host " Key: $KeyFile" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# ── Step 1: Create remote project directory ──────────────────
Write-Host "`n[1/4] Creating remote directory..." -ForegroundColor Yellow
ssh @SSH_OPTS "${User}@${Server}" "mkdir -p $RemoteDir"

# ── Step 2: Sync project files (exclude venv, cache, .env) ───
Write-Host "[2/4] Syncing project files via SCP..." -ForegroundColor Yellow
Write-Host "      (Excluding: venv/, __pycache__/, db.sqlite3, .env, media/)" -ForegroundColor Gray

# Build exclusion list
$exclude = @("venv", "__pycache__", "*.pyc", ".env", "node_modules", ".git")

# Use scp to copy files (Windows-compatible)
# First create a tar of the project, then extract on server
$tarExcludes = ($exclude | ForEach-Object { "--exclude=./$_" }) -join " "

# scp individual important directories
$dirs = @("AI_automate", "blog", "pages", "portfolio", "dashboard", "templates", "static", "workflows", ".claude", "scripts", "content_backlog")
$files = @("manage.py", "requirements.txt", "CLAUDE.md")

foreach ($dir in $dirs) {
    $localPath = Join-Path $ProjectDir $dir
    if (Test-Path $localPath) {
        Write-Host "      -> $dir/" -ForegroundColor Gray
        scp @SCP_OPTS -r "$localPath" "${User}@${Server}:${RemoteDir}/"
    }
}

foreach ($file in $files) {
    $localPath = Join-Path $ProjectDir $file
    if (Test-Path $localPath) {
        Write-Host "      -> $file" -ForegroundColor Gray
        scp @SCP_OPTS "$localPath" "${User}@${Server}:${RemoteDir}/"
    }
}

# ── Step 3: First-time setup (install deps) ───────────────────
if ($FirstTime) {
    Write-Host "[3/4] Running first-time server setup..." -ForegroundColor Yellow
    Write-Host "      This will take 3-5 minutes..." -ForegroundColor Gray
    scp @SCP_OPTS "$ScriptDir\setup_server.sh" "${User}@${Server}:${RemoteDir}/"
    ssh @SSH_OPTS "${User}@${Server}" "chmod +x ${RemoteDir}/setup_server.sh && bash ${RemoteDir}/setup_server.sh"
} else {
    Write-Host "[3/4] Skipping full setup (use -FirstTime for initial install)" -ForegroundColor Gray
}

# ── Step 4: Post-deploy (migrate, collectstatic, restart) ────
Write-Host "[4/4] Running post-deploy tasks..." -ForegroundColor Yellow
scp @SCP_OPTS "$ScriptDir\post_deploy.sh" "${User}@${Server}:${RemoteDir}/"
ssh @SSH_OPTS "${User}@${Server}" "chmod +x ${RemoteDir}/post_deploy.sh && bash ${RemoteDir}/post_deploy.sh"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host " Deploy complete!" -ForegroundColor Green
Write-Host " Site: http://$Server" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green
