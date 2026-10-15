@echo off
setlocal enabledelayedexpansion

echo ====================================================================
echo   PRICEGUARD - GitHub Repository Setup Helper (Windows Batch)
echo ====================================================================
echo.

:: Check if git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in your system PATH!
    echo Please download and install Git from: https://git-scm.com/download/win
    echo After installing, reopen your terminal and run this script again.
    pause
    exit /b 1
)

echo [1/5] Initializing Git repository...
if not exist ".git" (
    git init
    echo [+] Git repository initialized.
) else (
    echo [*] Git repository already initialized.
)

echo.
echo [2/5] Staging files (respecting .gitignore)...
git add .
echo [+] Files staged.

echo.
echo [3/5] Creating initial commit...
git commit -m "feat: initial release with FastAPI REST backend, XGBoost multi-horizon models, Streamlit dashboard, and CI/CD"
echo [+] Commit created.

echo.
echo [4/5] Setting default branch to main...
git branch -M main

echo.
echo ====================================================================
echo   Ready to link to your GitHub Remote Repository!
echo ====================================================================
echo.
echo 1. Go to https://github.com/new and create a new repository (e.g. 'PRICEGUARD').
echo 2. Do NOT initialize it with README, .gitignore, or license (already created).
echo 3. Copy your GitHub repository URL (e.g., https://github.com/YOUR_USERNAME/PRICEGUARD.git)
echo.
set /p REPO_URL="Enter your GitHub Repository URL (or press ENTER to skip): "

if not "%REPO_URL%"=="" (
    echo.
    echo [5/5] Adding remote and pushing to GitHub...
    git remote remove origin >nul 2>nul
    git remote add origin %REPO_URL%
    git push -u origin main
    if %errorlevel% equ 0 (
        echo.
        echo ================================================================
        echo [SUCCESS] PRICEGUARD successfully published to GitHub!
        echo ================================================================
    ) else (
        echo.
        echo [!] Push failed. Check your GitHub credentials / authentication or try:
        echo     git push -u origin main
    )
) else (
    echo.
    echo [*] Remote push skipped. When you are ready, run:
    echo     git remote add origin ^<YOUR_GITHUB_REPO_URL^>
    echo     git push -u origin main
)

echo.
pause
