# CodeRabbit Adoption Dashboard

**Live Dashboard**: https://anandkuma77.github.io/codeRabbitDashboard/

## 📊 Current Data

- **Total Repositories**: 43 (41 fetched)
- **CodeRabbit Active**: 24 repos (55.8%)
- **Total PRs Reviewed**: 1,084
- **Last Updated**: April 29, 2026

### Categories
- ✅ **Fully Active**: 3 repos
- ⚠️ **Reviewing, No Config**: 21 repos
- 📝 **Config, No Reviews**: 0 repos
- ❌ **Not Configured**: 19 repos

### Teams (7 teams)
- Application Platform: 6/7 (85.7%)
- CID: 1/1 (100.0%)
- Edge: 4/7 (57.1%)
- Metal Platform: 8/19 (42.1%)
- Multi Architecture: 3/3 (100.0%)
- OKD: 0/3 (0.0%)
- Specialist Platform Team (SPLAT): 2/3 (66.7%)

## 📁 Files

```
host/
├── index.html                    # Dashboard (32 KB)
├── data/
│   └── coderabbit-status.json   # Data file (26 KB)
└── README.md                     # This file
```

## 🚀 Deploy to GitHub Pages

1. **Create new repository** on GitHub (e.g., "coderabbit-dashboard")

2. **Push from this folder**
   ```bash
   cd host
   git init
   git add .
   git commit -m "Initial commit: CodeRabbit Dashboard"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
   git push -u origin main
   ```

3. **Enable GitHub Pages**
   - Settings → Pages → Source: **main** branch → Save
   - Access at: `https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/`

## 🔄 Update Dashboard Data

```bash
# 1. Fetch fresh data (from parent directory)
export GITHUB_TOKEN=$(cat token | tr -d '\n')
python3 scripts/fetch_coderabbit_data.py

# 2. Copy to host folder
cp data/coderabbit-status.json host/data/

# 3. Commit and push
cd host
git add data/coderabbit-status.json
git commit -m "Update dashboard data - $(date +%Y-%m-%d)"
git push
```

GitHub Pages auto-updates in 1-2 minutes.

---

**Generated**: April 29, 2026  
**Data**: 43 repos from 7 teams | 24 with CodeRabbit (55.8%) | 1,084 PRs reviewed
