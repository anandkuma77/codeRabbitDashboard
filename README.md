# CodeRabbit Adoption Dashboard

Static dashboard for **CodeRabbit** adoption across tracked GitHub repositories. The UI in `index.html` has two tabs—**OpenShift** and **EEE**—each loading its own JSON under `data/`. It renders KPIs, adoption breakdowns, Mermaid diagrams, and a filterable repository table.

**Live site**: [https://anandkuma77.github.io/codeRabbitDashboard/](https://anandkuma77.github.io/codeRabbitDashboard/)

---

## Data files (source of truth)

| Tab        | JSON file                         | Updated by |
| ---------- | --------------------------------- | ---------- |
| OpenShift  | `data/coderabbit-openshift-status.json` | `scripts/fetch_coderabbit_Openshift_data.py` |
| EEE        | `data/coderabbit-EEE-status.json`       | `scripts/fetch_coderabbit_EEE_data.py` |

Treat the `summary` fields and `last_updated` at the top of each JSON as authoritative. README numbers can drift between refreshes.

---

## Repository layout

```
codeRabbitDashboard/
├── index.html              # Dashboard UI (GitHub Pages entry; tab switcher)
├── data/
│   ├── coderabbit-openshift-status.json
│   └── coderabbit-EEE-status.json
├── scripts/
│   ├── fetch_coderabbit_Openshift_data.py
│   └── fetch_coderabbit_EEE_data.py
├── .github/workflows/
│   └── fetch-coderabbit-data.yml
└── README.md
```

---

## How data is collected

Each Python script **does not discover new repos by itself**: it loads the existing `repos` array from its JSON file, then for each repository it:

1. Looks for `.coderabbit.yaml` or `.coderabbit.yml` via the GitHub contents API.
2. Fetches up to 50 recent PRs (closed and open, by last update).
3. For each PR, loads reviews, review comments, and issue comments and detects activity from `coderabbitai[bot]`.
4. Computes per-repo and summary stats, including how often CodeRabbit commented before any human reviewer.
5. Writes the file back in place.

**Requirements**: Python 3.11+ (stdlib only). Set `GITHUB_TOKEN` for authenticated requests and sensible rate limits. The scripts can fall back to an authenticated `gh` CLI when useful.

**Token scope**: fine-grained or classic token able to read repository metadata and pull requests for the orgs/repos listed in the JSON (same access you use to browse those repos on GitHub).

---

## Refresh data locally

From the repository root:

```bash
export GITHUB_TOKEN="your-token"
python3 scripts/fetch_coderabbit_Openshift_data.py
python3 scripts/fetch_coderabbit_EEE_data.py
```

Commit and push when you want the site to reflect the change (GitHub Pages will pick it up after the next deploy).

---

## Automated updates (GitHub Actions)

Workflow: `.github/workflows/fetch-coderabbit-data.yml`

- **Schedule**: weekdays (Monday–Friday) at **01:00** and **13:00 UTC**.
- **Manual run**: Actions → *Fetch CodeRabbit Data* → *Run workflow*.
- Runs both fetch scripts, then commits **only if** either JSON changed (commit message: `Update CodeRabbit adoption data [skip ci]`).

---

## Dashboard features (`index.html`)

- Tab switcher for OpenShift vs EEE datasets.
- KPI strip driven by each JSON summary.
- Adoption overview bar and integration flow (Mermaid).
- Breakdowns by team, domain, and repo lifecycle **status** (Active / Maintenance / Deprecated from the JSON).
- Sortable table with filters (CodeRabbit presence, repo status, team) and search.

---

## Maintenance notes

- To **add or remove** tracked repositories, edit the `repos` entries in the appropriate JSON file, then run the matching fetch script so metrics stay consistent.
- Prefer updating README narrative here; copy exact counts from the JSON when sharing a formal status report.
