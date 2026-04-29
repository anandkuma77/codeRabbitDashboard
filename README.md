# CodeRabbit Adoption Dashboard - GitHub Pages

This folder contains everything needed to deploy the CodeRabbit dashboard to GitHub Pages.

## 📊 Current Data

- **Total Repositories**: 631
- **Successfully Fetched**: 610 repos (96.7%)
- **CodeRabbit Active**: 329 repos (52.1%)
- **Last Updated**: April 29, 2026

### Categories
- ✅ **Fully Active**: 64 repos (config + reviews)
- ⚠️ **Reviewing, No Config**: 265 repos
- 📝 **Config, No Reviews**: 4 repos
- ❌ **Not Configured**: 298 repos

## 📁 Files in This Folder

```
host/
├── index.html                    # Dashboard (32 KB)
├── data/
│   └── coderabbit-status.json   # Data file (367 KB)
└── README.md                     # This file
```

## 🚀 Deploy to GitHub Pages

### Option 1: New Repository

1. **Create a new GitHub repository**
   ```bash
   # On GitHub: Create a new repository (e.g., "coderabbit-dashboard")
   ```

2. **Initialize and push from this folder**
   ```bash
   cd host
   git init
   git add .
   git commit -m "Initial commit: CodeRabbit Dashboard with 610 repos"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
   git push -u origin main
   ```

3. **Enable GitHub Pages**
   - Go to your repo on GitHub
   - Click **Settings** → **Pages**
   - Under **Source**, select **main** branch
   - Click **Save**

4. **Access your dashboard**
   - URL: `https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/`
   - Wait 1-2 minutes for deployment

### Option 2: Existing Repository

If you already have a repository:

```bash
# Copy files to your repo
cp -r host/* /path/to/your/repo/

# Or copy to a subdirectory
cp -r host/* /path/to/your/repo/dashboard/

cd /path/to/your/repo
git add .
git commit -m "Add CodeRabbit Dashboard - 610 repos, 329 with CodeRabbit"
git push
```

Then enable GitHub Pages in Settings → Pages.

## 🔄 Updating the Dashboard

When you have new data:

1. **Update the data file**
   ```bash
   # In the parent directory
   export GITHUB_TOKEN=$(cat token | tr -d '\n')
   python3 scripts/fetch_coderabbit_data.py
   ```

2. **Copy updated data to host folder**
   ```bash
   cp data/coderabbit-status.json host/data/
   ```

3. **Commit and push**
   ```bash
   cd host
   git add data/coderabbit-status.json
   git commit -m "Update dashboard data - $(date +%Y-%m-%d)"
   git push
   ```

4. **GitHub Pages will auto-update** in 1-2 minutes

## 🌐 Live Dashboard

Once deployed, your dashboard will be accessible at:
- `https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/`

The dashboard:
- ✅ Loads data dynamically from `data/coderabbit-status.json`
- ✅ Works without any server-side code
- ✅ Self-contained (no external dependencies except Mermaid.js CDN)
- ✅ Responsive design
- ✅ Interactive filters and sorting

## 📊 Dashboard Features

- **7 KPI Cards**: Total repos, active repos, CodeRabbit metrics
- **Adoption Overview**: Visual breakdown with Mermaid flowchart
- **Team & Domain Charts**: See which teams have CodeRabbit
- **Repository Status**: Active, Maintenance, Deprecated
- **Top Repositories**: Most PRs reviewed, highest bot-first rate
- **Full Repository Table**: Searchable, filterable, sortable
- **Bottom Line**: Key findings and recommendations

## 🔧 Technical Details

- **No build step required**: Pure HTML/CSS/JS
- **Data loading**: Fetches `data/coderabbit-status.json` at runtime
- **Charts**: Mermaid.js from CDN (https://cdn.jsdelivr.net/npm/mermaid@10)
- **Size**: ~400 KB total (HTML + data)
- **Browser support**: Modern browsers (Chrome, Firefox, Safari, Edge)

## 🐛 Troubleshooting

### Dashboard shows no data
- Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
- Check browser console (F12) for errors
- Verify `data/coderabbit-status.json` exists

### GitHub Pages not updating
- Check Actions tab for deployment status
- Wait 2-3 minutes after pushing
- Clear browser cache

### 404 error
- Verify GitHub Pages is enabled (Settings → Pages)
- Check the branch is set to `main`
- Ensure `index.html` is in the root directory

## 📝 Data File Schema

The `data/coderabbit-status.json` file contains:

```json
{
  "total": 631,
  "fully_active": 64,
  "reviewing_no_config": 265,
  "config_no_reviews": 4,
  "not_configured": 298,
  "has_config_total": 68,
  "has_reviews_total": 329,
  "total_prs_reviewed": 10661,
  "total_coderabbit_first_reviews": 0,
  "coderabbit_first_review_pct": 0.0,
  "last_updated": "2026-04-29T06:35:16.977436Z",
  "repos": [
    {
      "name": "repo-name",
      "url": "https://github.com/owner/repo-name",
      "owner": "owner",
      "repo": "repo-name",
      "team": "Team Name",
      "status": "Active",
      "has_config": true,
      "config_file": ".coderabbit.yaml",
      "has_coderabbit_reviews": true,
      "coderabbit_pr_count": 100,
      "coderabbit_first_review_count": 50,
      "coderabbit_first_review_pct": 50.0,
      "category": "fully_active",
      "last_updated": "2026-04-29T06:35:16.977436Z"
    }
  ]
}
```

## 📞 Support

For issues or questions about:
- **Data generation**: Check parent directory documentation
- **GitHub Pages**: https://docs.github.com/pages
- **Dashboard bugs**: Open an issue in your repository

---

**Generated**: April 29, 2026
**Data**: 610 repos from 89 teams
**CodeRabbit Adoption**: 52.1% (329 repos)
