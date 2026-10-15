# 🚀 GitHub Setup & Deployment Guide for PRICEGUARD

This guide walks you through publishing the **PRICEGUARD** project (FastAPI Backend + Streamlit UI + XGBoost Analytics Engine) to your GitHub account.

---

## ⚡ Option 1: Automated 1-Click Setup (Recommended)

If you are on Windows and have Git installed:

1. Open your terminal in the `PRICEGUARD` directory:
   ```cmd
   cd PRICEGUARD
   ```
2. Run the automated script:
   - **Using Command Prompt / Batch**:
     ```cmd
     setup_git.bat
     ```
   - **Using PowerShell**:
     ```powershell
     .\setup_git.ps1
     ```
3. When prompted, paste your GitHub repository URL (e.g. `https://github.com/YOUR_USERNAME/PRICEGUARD.git`).

---

## 🛠️ Option 2: Step-by-Step Manual Setup

### Step 1: Install Git (If Not Already Installed)
- Download and install **Git for Windows** from: [https://git-scm.com/download/win](https://git-scm.com/download/win)
- During installation, keep the default options ("Git from the command line and also from 3rd-party software").
- Restart your Command Prompt or PowerShell after installation to refresh your `PATH`.

### Step 2: Configure Your Git Identity
Run these commands once in your terminal:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Step 3: Create a New Repository on GitHub
1. Go to [https://github.com/new](https://github.com/new).
2. Repository name: `PRICEGUARD` (or your preferred name).
3. Set visibility: **Public** or **Private**.
4. **IMPORTANT**: Leave **"Add a README file"**, **"Add .gitignore"**, and **"Choose a license"** **UNCHECKED** (we have already created high-quality versions of these).
5. Click **Create repository**.
6. Copy the repository URL (e.g., `https://github.com/YOUR_USERNAME/PRICEGUARD.git`).

### Step 4: Initialize and Push the Local Code
In your project directory (`PRICEGUARD/`), run:

```bash
# 1. Initialize Git in the project folder
git init

# 2. Stage all project files (ignoring venv, cache, etc. via .gitignore)
git add .

# 3. Create the initial commit
git commit -m "feat: complete PRICEGUARD system with FastAPI backend, Streamlit UI, and XGBoost models"

# 4. Rename the default branch to main
git branch -M main

# 5. Link your GitHub remote repository (replace with your URL)
git remote add origin https://github.com/YOUR_USERNAME/PRICEGUARD.git

# 6. Push code to GitHub
git push -u origin main
```

---

## 🔑 GitHub Authentication Tip (Personal Access Token / GitHub CLI)

If Git asks for your password during `git push`, note that GitHub requires a **Personal Access Token (PAT)** or the **GitHub CLI (`gh`)**:

1. Go to **GitHub Settings** -> **Developer Settings** -> **Personal Access Tokens** -> **Tokens (classic)** ([link](https://github.com/settings/tokens)).
2. Click **Generate new token (classic)**.
3. Check the `repo` scope and click **Generate token**.
4. Copy the token and paste it when Git prompts for your password in the terminal.

Alternatively, you can use **GitHub Desktop** ([https://desktop.github.com/](https://desktop.github.com/)) to drag and drop the `PRICEGUARD` folder and publish with one click!

---

## 🔄 Making Future Updates to GitHub

Whenever you make changes to PRICEGUARD:
```bash
git add .
git commit -m "update: describe your changes here"
git push
```
