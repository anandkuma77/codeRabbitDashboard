# CodeRabbit Dashboard - GitHub Pages Deployment

This folder contains all files needed to host the CodeRabbit Adoption Dashboard on GitHub Pages.

## 📁 Files Included

```
host/
├── index.html                    # Main dashboard (self-contained HTML)
├── data/
│   └── coderabbit-status.json   # Dashboard data (630 repos)
└── README.md                     # This file
```

## 🚀 Deploy to GitHub Pages

### Option 1: Deploy from this folder

1. **Create a new GitHub repository** (or use existing one)
   
2. **Initialize git in this folder**:
   ```bash
   cd host
   git init
   git add .
   git commit -m "Initial commit: CodeRabbit Dashboard"
   ```

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
   git branch -M main
   git push -u origin main
   ```

4. **Enable GitHub Pages**:
   - Go to your repo on GitHub
   - Click **Settings** → **Pages**
   - Under **Source**, select **main** branch
   - Click **Save**

5. **Access your dashboard**:
   - URL: `https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/`
   - Wait 1-2 minutes for deployment

### Option 2: Deploy to existing repo

If you already have a repository:

1. **Copy files to your repo**:
   ```bash
   cp -r host/* /path/to/your/repo/
   cd /path/to/your/repo/
   ```

2. **Commit and push**:
   ```bash
   git add index.html data/
   git commit -m "Add CodeRabbit Dashboard"
   git push
   ```

3. **Enable GitHub Pages** (if not already enabled):
   - Settings → Pages → Source: main branch → Save

## 🔄 Updating the Dashboard

When you want to update the data:

1. **Run the fetch script** (in the parent directory):
   ```bash
   cd ..
   export GITHUB_TOKEN=$(cat token | tr -d '\n')
   python3 scripts/fetch_coderabbit_data.py
   ```

2. **Copy updated data**:
   ```bash
   cp data/coderabbit-status.json host/data/
   ```

3. **Commit and push**:
   ```bash
   cd host
   git add data/coderabbit-status.json
   git commit -m "Update dashboard data - $(date +%Y-%m-%d)"
   git push
   ```

4. **GitHub Pages will auto-update** in 1-2 minutes

## 📊 Dashboard Features

- **630 repositories** tracked across 99 teams
- Live CodeRabbit adoption metrics
- Interactive filtering and sorting
- Team and domain breakdowns
- Top repositories by activity
- Bot-first review analytics

## 🔧 Customization

The dashboard is a single self-contained HTML file with:
- Inline CSS (no external stylesheets)
- Inline JavaScript (no build step)
- Mermaid.js loaded from CDN
- Data loaded from `data/coderabbit-status.json`

To customize, edit `index.html` directly.

## 📝 Notes

- The dashboard loads data via `fetch()`, which works on GitHub Pages (HTTP/HTTPS)
- No server-side code needed - it's pure static HTML/CSS/JS
- Data file is ~500KB - well within GitHub Pages limits
- Updates to `data/coderabbit-status.json` require a git push to deploy

## 🐛 Troubleshooting

**Dashboard shows no data:**
- Check browser console (F12) for errors
- Verify `data/coderabbit-status.json` exists in the repo
- Do a hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

**GitHub Pages not updating:**
- Check the Actions tab for deployment status
- Wait 2-3 minutes after pushing
- Clear browser cache

**404 error:**
- Verify GitHub Pages is enabled in Settings → Pages
- Check the branch is set to `main`
- Ensure `index.html` is in the root directory
