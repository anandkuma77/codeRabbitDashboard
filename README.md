# CodeRabbit Adoption Dashboard

Static dashboard for **CodeRabbit** adoption across tracked EEE GitHub repositories. It reads `data/coderabbit-status.json` and renders KPIs, team and status breakdowns, Mermaid diagrams, and a filterable repository table in `index.html`.

**Live site**: [https://anandkuma77.github.io/codeRabbitDashboard/](https://anandkuma77.github.io/codeRabbitDashboard/)

---

## Snapshot (from `data/coderabbit-status.json`)

Values below match the committed JSON. For the freshest numbers, open the live dashboard or inspect the `summary` fields at the top of that file.

- **Last updated**: 2026-05-05 (UTC, see `last_updated` in JSON)
- **Total repositories**: 47
- **Repos with CodeRabbit PR activity** (recent PRs scanned): 30 (63.8%)
- **Repos with `.coderabbit.yaml` / `.coderabbit.yml`**: 4
- **Total PRs with CodeRabbit reviews** (counts from analyzed PRs): 783
- **CodeRabbit reviewed before any human** (aggregate): 353 PRs (45.1% of PRs with CodeRabbit activity)

### Categories (how each repo is classified)

| Category | Count | Meaning |
| -------- | ----- | ------- |
| Fully active | 4 | Config file present **and** CodeRabbit activity on recent PRs |
| Reviewing, no config | 26 | CodeRabbit activity **without** a checked-in config file |
| Config, no reviews | 0 | Config present but no CodeRabbit activity in the sampled PRs |
| Not configured | 17 | No config and no CodeRabbit activity in the sampled PRs |

### Team adoption (repos with CodeRabbit PR activity / team size)

| Team | Adoption |
| ---- | -------- |
| Application Platform | 9/9 (100%) |
| CID | 1/1 (100%) |
| Edge | 4/7 (57.1%) |
| Metal Platform | 8/19 (42.1%) |
| Multi Architecture | 4/4 (100%) |
| OKD | 0/3 (0%) |
| Specialist Platform Team (SPLAT) | 4/4 (100%) |

---

## Repository layout

```
codeRabbitDashboard/
├── index.html              # Dashboard UI (GitHub Pages entry)
├── data/
│   └── coderabbit-status.json   # Repo list + scraped metrics (committed)
├── scripts/
│   └── fetch_coderabbit_data.py # Refreshes JSON via GitHub API
├── .github/workflows/
│   └── fetch-coderabbit-data.yml
└── README.md
```

---

## How data is collected

The Python script **does not discover new repos by itself**: it loads the existing `repos` array from `data/coderabbit-status.json`, then for each repository it:

1. Looks for `.coderabbit.yaml` or `.coderabbit.yml` via the GitHub contents API.
2. Fetches up to 50 recent PRs (closed and open, by last update).
3. For each PR, loads reviews, review comments, and issue comments and detects activity from `coderabbitai[bot]`.
4. Computes per-repo and summary stats, including how often CodeRabbit commented before any human reviewer.
5. Writes the file back in place.

**Requirements**: Python 3.11+ (stdlib only). Set `GITHUB_TOKEN` for authenticated requests and sensible rate limits.

**Token scope**: fine-grained or classic token able to read repository metadata and pull requests for the orgs/repos listed in the JSON (same access you use to browse those repos on GitHub).

---

## Refresh data locally

From the repository root:

```bash
export GITHUB_TOKEN="your-token"
python3 scripts/fetch_coderabbit_data.py
```

This updates `data/coderabbit-status.json`. Commit and push when you want the site to reflect the change (GitHub Pages will pick it up after the next deploy).

---

## Automated updates (GitHub Actions)

Workflow: `.github/workflows/fetch-coderabbit-data.yml`

- **Schedule**: weekdays (Monday–Friday) at **01:00** and **13:00 UTC**.
- **Manual run**: Actions → *Fetch CodeRabbit Data* → *Run workflow*.
- Uses `secrets.GITHUB_TOKEN` with `contents: write` to commit only when `data/coderabbit-status.json` changes (commit message: `Update CodeRabbit adoption data [skip ci]`).

---

## Dashboard features (`index.html`)

- KPI strip driven by the JSON summary.
- Adoption overview bar and integration flow (Mermaid).
- Breakdowns by team, domain, and repo lifecycle **status** (Active / Maintenance / Deprecated from the JSON).
- Sortable table with filters (CodeRabbit presence, repo status, team) and search.

---

## Maintenance notes

- To **add or remove** tracked repositories, edit the `repos` entries in `data/coderabbit-status.json` (or regenerate the list elsewhere and merge), then run the fetch script so metrics stay consistent.
- README totals can drift between edits; treat **`data/coderabbit-status.json`** as the source of truth and refresh this snapshot when you cut a release or share a status report.
