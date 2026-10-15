# PRICEGUARD - GitHub Repository Setup Helper (PowerShell)
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "  PRICEGUARD - GitHub Repository Setup Helper (PowerShell)" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

# Check Git
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCmd) {
    Write-Host "[ERROR] Git was not detected on your PATH!" -ForegroundColor Red
    Write-Host "Please install Git for Windows from: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "After installation, open a new PowerShell window and run this script." -ForegroundColor Yellow
    exit 1
}

# 1. Init
Write-Host "[1/5] Initializing Git repository..." -ForegroundColor Green
if (-not (Test-Path ".git")) {
    git init
    Write-Host "[+] Initialized empty Git repository." -ForegroundColor Gray
} else {
    Write-Host "[*] Git repository already exists." -ForegroundColor Gray
}

# 2. Stage
Write-Host ""
Write-Host "[2/5] Staging files..." -ForegroundColor Green
git add .
Write-Host "[+] All files staged (excluding .gitignore entries)." -ForegroundColor Gray

# 3. Commit
Write-Host ""
Write-Host "[3/5] Creating initial commit..." -ForegroundColor Green
git commit -m "feat: complete PRICEGUARD system with FastAPI REST backend, XGBoost time-series engine, Streamlit UI, Docker, and CI/CD"

# 4. Branch
Write-Host ""
Write-Host "[4/5] Setting main branch..." -ForegroundColor Green
git branch -M main

# 5. Remote Link
Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "  Ready to connect to GitHub!" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "1. Create a repository on GitHub: https://github.com/new"
Write-Host "2. Copy the HTTPS/SSH URL (e.g. https://github.com/YOUR_USER/PRICEGUARD.git)"
Write-Host ""
$repoUrl = Read-Host "Paste your GitHub Repository URL (or press Enter to skip)"

if ($repoUrl -and $repoUrl.Trim() -ne "") {
    Write-Host ""
    Write-Host "[5/5] Adding remote origin and pushing..." -ForegroundColor Green
    git remote remove origin 2>$null
    git remote add origin $repoUrl.Trim()
    git push -u origin main
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host " [SUCCESS] Repository successfully pushed to GitHub!" -ForegroundColor Green
        Write-Host "================================================================" -ForegroundColor Green
    } else {
        Write-Host "[!] Git push encountered an error. Please verify your permissions and run: git push -u origin main" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "[*] Skipped remote push. When ready, execute:" -ForegroundColor Gray
    Write-Host "    git remote add origin <YOUR_GITHUB_REPO_URL>" -ForegroundColor White
    Write-Host "    git push -u origin main" -ForegroundColor White
}
