#!/usr/bin/env python3
"""
Fetch CodeRabbit adoption data for EEE GitHub repositories.

This script:
1. Reads the existing repo list from data/coderabbit-EEE-status.json
2. Checks each repo for .coderabbit.yaml config files via GitHub API
3. Scans recent PRs for coderabbitai[bot] review activity
4. Tracks if CodeRabbit reviewed PRs BEFORE human reviewers
5. Updates data/coderabbit-EEE-status.json with current status

Requirements:
- GITHUB_TOKEN environment variable set
- gh CLI authenticated (fallback)
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# GitHub API settings
GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# Rate limiting
REQUEST_DELAY = 0.5  # seconds between API requests
MAX_RETRIES = 3  # maximum number of retries
INITIAL_RETRY_DELAY = 1  # initial delay for exponential backoff (in seconds)


def github_api_request(endpoint: str) -> Optional[dict]:
    """Make authenticated GitHub API request with exponential backoff retry."""
    url = f"{GITHUB_API}{endpoint}"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    for attempt in range(MAX_RETRIES):
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode())
        except HTTPError as e:
            if e.code == 404:
                # 404 means resource doesn't exist, no point retrying
                return None
            elif e.code == 403:
                # Rate limit hit, wait longer
                retry_delay = INITIAL_RETRY_DELAY * (2 ** attempt)
                if attempt < MAX_RETRIES - 1:
                    print(f"  ⚠️  HTTP {e.code} (rate limit) for {endpoint}, retrying in {retry_delay}s... (attempt {attempt + 1}/{MAX_RETRIES})", file=sys.stderr)
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"  ❌ HTTP {e.code} for {endpoint} after {MAX_RETRIES} attempts", file=sys.stderr)
                    return None
            elif e.code >= 500:
                # Server error, retry with exponential backoff
                retry_delay = INITIAL_RETRY_DELAY * (2 ** attempt)
                if attempt < MAX_RETRIES - 1:
                    print(f"  ⚠️  HTTP {e.code} (server error) for {endpoint}, retrying in {retry_delay}s... (attempt {attempt + 1}/{MAX_RETRIES})", file=sys.stderr)
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"  ❌ HTTP {e.code} for {endpoint} after {MAX_RETRIES} attempts", file=sys.stderr)
                    return None
            else:
                # Other HTTP errors (4xx), no point retrying
                print(f"  ⚠️  HTTP {e.code} for {endpoint}", file=sys.stderr)
                return None
        except (URLError, Exception) as e:
            # Network errors, timeout, etc. - retry with exponential backoff
            retry_delay = INITIAL_RETRY_DELAY * (2 ** attempt)
            if attempt < MAX_RETRIES - 1:
                print(f"  ⚠️  Error fetching {endpoint}: {e}, retrying in {retry_delay}s... (attempt {attempt + 1}/{MAX_RETRIES})", file=sys.stderr)
                time.sleep(retry_delay)
                continue
            else:
                print(f"  ❌ Error fetching {endpoint} after {MAX_RETRIES} attempts: {e}", file=sys.stderr)
                return None

    # Should not reach here, but just in case
    return None


def check_config_file(owner: str, repo: str) -> Tuple[bool, Optional[str]]:
    """Check if repo has .coderabbit.yaml or .coderabbit.yml config file."""
    for filename in [".coderabbit.yaml", ".coderabbit.yml"]:
        result = github_api_request(f"/repos/{owner}/{repo}/contents/{filename}")
        if result and result.get("type") == "file":
            return True, filename
    return False, None


def get_recent_prs(owner: str, repo: str, max_prs: int = 50) -> List[dict]:
    """Get recent pull requests from a repository."""
    # Get closed and open PRs
    prs = []
    for state in ["closed", "open"]:
        result = github_api_request(f"/repos/{owner}/{repo}/pulls?state={state}&per_page=30&sort=updated&direction=desc")
        if result:
            prs.extend(result)
        time.sleep(REQUEST_DELAY)

    return prs[:max_prs]


def get_pr_reviews(owner: str, repo: str, pr_number: int) -> List[dict]:
    """Get all reviews for a specific PR."""
    result = github_api_request(f"/repos/{owner}/{repo}/pulls/{pr_number}/reviews")
    return result if result else []


def get_pr_review_comments(owner: str, repo: str, pr_number: int) -> List[dict]:
    """Get all review comments for a specific PR."""
    result = github_api_request(f"/repos/{owner}/{repo}/pulls/{pr_number}/comments")
    return result if result else []


def get_issue_comments(owner: str, repo: str, pr_number: int) -> List[dict]:
    """Get issue comments for a PR (includes CodeRabbit walkthrough summaries)."""
    result = github_api_request(f"/repos/{owner}/{repo}/issues/{pr_number}/comments")
    return result if result else []


def analyze_pr_reviews(owner: str, repo: str, prs: List[dict]) -> Dict:
    """
    Analyze PRs to determine:
    - Total PRs with CodeRabbit reviews
    - PRs where CodeRabbit reviewed before any human
    - Average time between CodeRabbit and first human review
    """
    coderabbit_prs = []
    coderabbit_first_prs = []

    for pr in prs:
        pr_number = pr['number']
        print(f"    Analyzing PR #{pr_number}...", end=" ")

        # Get all reviews, review comments, and issue comments
        reviews = get_pr_reviews(owner, repo, pr_number)
        time.sleep(REQUEST_DELAY)

        comments = get_pr_review_comments(owner, repo, pr_number)
        time.sleep(REQUEST_DELAY)

        issue_comments = get_issue_comments(owner, repo, pr_number)
        time.sleep(REQUEST_DELAY)

        # Find CodeRabbit activity (reviews, review comments, and issue comments)
        coderabbit_reviews = [r for r in reviews if r.get('user', {}).get('login') == 'coderabbitai[bot]']
        coderabbit_comments = [c for c in comments if c.get('user', {}).get('login') == 'coderabbitai[bot]']
        coderabbit_issue_comments = [c for c in issue_comments if c.get('user', {}).get('login') == 'coderabbitai[bot]']

        has_coderabbit = len(coderabbit_reviews) > 0 or len(coderabbit_comments) > 0 or len(coderabbit_issue_comments) > 0

        if has_coderabbit:
            coderabbit_prs.append(pr_number)

            # Find earliest CodeRabbit activity
            coderabbit_times = []
            for r in coderabbit_reviews:
                if r.get('submitted_at'):
                    coderabbit_times.append(r['submitted_at'])
            for c in coderabbit_comments:
                if c.get('created_at'):
                    coderabbit_times.append(c['created_at'])
            for c in coderabbit_issue_comments:
                if c.get('created_at'):
                    coderabbit_times.append(c['created_at'])

            if coderabbit_times:
                earliest_coderabbit = min(coderabbit_times)

                # Find earliest human review/comment
                human_reviews = [r for r in reviews if r.get('user', {}).get('login') != 'coderabbitai[bot]'
                                and r.get('user', {}).get('type') != 'Bot']
                human_comments = [c for c in comments if c.get('user', {}).get('login') != 'coderabbitai[bot]'
                                 and c.get('user', {}).get('type') != 'Bot']
                human_issue_comments = [c for c in issue_comments if c.get('user', {}).get('login') != 'coderabbitai[bot]'
                                       and c.get('user', {}).get('type') != 'Bot']

                human_times = []
                for r in human_reviews:
                    if r.get('submitted_at'):
                        human_times.append(r['submitted_at'])
                for c in human_comments:
                    if c.get('created_at'):
                        human_times.append(c['created_at'])
                for c in human_issue_comments:
                    if c.get('created_at'):
                        human_times.append(c['created_at'])

                if human_times:
                    earliest_human = min(human_times)

                    # CodeRabbit was first if it reviewed before any human
                    if earliest_coderabbit < earliest_human:
                        coderabbit_first_prs.append(pr_number)
                        print("✅ CodeRabbit first")
                    else:
                        print("👤 Human first")
                else:
                    # Only CodeRabbit reviewed, no humans
                    coderabbit_first_prs.append(pr_number)
                    print("✅ CodeRabbit only")
            else:
                print("❌ No timestamps")
        else:
            print("⊘ No CodeRabbit")

    return {
        'coderabbit_pr_count': len(coderabbit_prs),
        'coderabbit_first_review_count': len(coderabbit_first_prs),
        'coderabbit_first_review_pct': round(len(coderabbit_first_prs) / len(coderabbit_prs) * 100, 1) if coderabbit_prs else 0
    }


def process_repo(repo_data: dict) -> dict:
    """Process a single repository to check CodeRabbit status."""
    owner = repo_data['owner']
    repo = repo_data['repo']
    name = repo_data['name']

    print(f"\n📦 {owner}/{repo}")

    # Check for config file
    print("  🔍 Checking config file...", end=" ")
    has_config, config_file = check_config_file(owner, repo)
    if has_config:
        print(f"✅ Found {config_file}")
    else:
        print("❌ Not found")
    time.sleep(REQUEST_DELAY)

    # Get recent PRs
    print("  📋 Fetching recent PRs...", end=" ")
    prs = get_recent_prs(owner, repo, max_prs=50)
    print(f"{len(prs)} found")

    # Analyze PR reviews
    if prs:
        print(f"  🤖 Analyzing CodeRabbit reviews...")
        review_stats = analyze_pr_reviews(owner, repo, prs)
    else:
        review_stats = {
            'coderabbit_pr_count': 0,
            'coderabbit_first_review_count': 0,
            'coderabbit_first_review_pct': 0
        }

    # Determine category
    has_reviews = review_stats['coderabbit_pr_count'] > 0

    if has_config and has_reviews:
        category = "fully_active"
    elif has_reviews:
        category = "reviewing_no_config"
    elif has_config:
        category = "config_no_reviews"
    else:
        category = "not_configured"

    # Update repo data
    updated_data = repo_data.copy()
    updated_data.update({
        'has_config': has_config,
        'config_file': config_file,
        'has_coderabbit_reviews': has_reviews,
        'coderabbit_pr_count': review_stats['coderabbit_pr_count'],
        'coderabbit_first_review_count': review_stats['coderabbit_first_review_count'],
        'coderabbit_first_review_pct': review_stats['coderabbit_first_review_pct'],
        'category': category,
        'last_updated': datetime.utcnow().isoformat() + 'Z'
    })

    print(f"  ✅ {category} | {review_stats['coderabbit_pr_count']} PRs reviewed | {review_stats['coderabbit_first_review_count']} CodeRabbit-first")

    return updated_data


def calculate_summary(repos: List[dict]) -> dict:
    """Calculate summary statistics."""
    total = len(repos)
    fully_active = sum(1 for r in repos if r['category'] == 'fully_active')
    reviewing_no_config = sum(1 for r in repos if r['category'] == 'reviewing_no_config')
    config_no_reviews = sum(1 for r in repos if r['category'] == 'config_no_reviews')
    not_configured = sum(1 for r in repos if r['category'] == 'not_configured')

    has_config_total = sum(1 for r in repos if r['has_config'])
    has_reviews_total = sum(1 for r in repos if r['has_coderabbit_reviews'])

    total_prs_reviewed = sum(r.get('coderabbit_pr_count', 0) for r in repos)
    total_coderabbit_first = sum(r.get('coderabbit_first_review_count', 0) for r in repos)

    return {
        'total': total,
        'fully_active': fully_active,
        'reviewing_no_config': reviewing_no_config,
        'config_no_reviews': config_no_reviews,
        'not_configured': not_configured,
        'has_config_total': has_config_total,
        'has_reviews_total': has_reviews_total,
        'total_prs_reviewed': total_prs_reviewed,
        'total_coderabbit_first_reviews': total_coderabbit_first,
        'coderabbit_first_review_pct': round(total_coderabbit_first / total_prs_reviewed * 100, 1) if total_prs_reviewed > 0 else 0,
        'last_updated': datetime.utcnow().isoformat() + 'Z'
    }


def main():
    """Main execution."""
    # Check for GitHub token
    if not GITHUB_TOKEN:
        print("⚠️  GITHUB_TOKEN not set. API rate limits will be very restrictive.", file=sys.stderr)
        print("Set GITHUB_TOKEN environment variable for authenticated requests.", file=sys.stderr)
        response = input("Continue anyway? [y/N]: ")
        if response.lower() != 'y':
            sys.exit(1)

    # Load existing data
    data_file = 'data/coderabbit-EEE-status.json'
    print(f"📂 Loading existing data from {data_file}")

    try:
        with open(data_file, 'r') as f:
            existing_data = json.load(f)
        repos = existing_data.get('repos', [])
        print(f"✅ Loaded {len(repos)} repositories")
    except FileNotFoundError:
        print(f"❌ File not found: {data_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {data_file}: {e}")
        sys.exit(1)

    # Process each repository
    print(f"\n{'='*60}")
    print(f"Starting CodeRabbit analysis for {len(repos)} repositories...")
    print(f"{'='*60}")

    updated_repos = []
    for i, repo_data in enumerate(repos, 1):
        print(f"\n[{i}/{len(repos)}]", end=" ")
        try:
            updated_repo = process_repo(repo_data)
            updated_repos.append(updated_repo)
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user. Saving partial results...")
            break
        except Exception as e:
            print(f"  ❌ Error processing repo: {e}")
            # Keep original data on error
            updated_repos.append(repo_data)

    # Calculate summary
    print(f"\n{'='*60}")
    print("📊 Calculating summary statistics...")
    summary = calculate_summary(updated_repos)

    # Combine summary and repos
    output_data = summary.copy()
    output_data['repos'] = updated_repos

    # Write updated data to main file
    print(f"💾 Writing updated data to {data_file}")
    with open(data_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    # Write timestamped historical copy
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    historical_file = f'data/coderabbit-EEE-status_{timestamp}.json'
    print(f"💾 Writing historical copy to {historical_file}")
    with open(historical_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    # Update historical manifest
    print(f"📋 Updating historical manifest...")
    try:
        subprocess.run(['python3', 'scripts/update_manifest.py'], check=True, capture_output=True)
        print(f"✅ Manifest updated")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Failed to update manifest: {e}", file=sys.stderr)

    # Print summary
    print(f"\n{'='*60}")
    print("✅ SUMMARY")
    print(f"{'='*60}")
    print(f"Total repositories: {summary['total']}")
    print(f"  Fully active (config + reviews): {summary['fully_active']}")
    print(f"  Reviewing PRs (no config): {summary['reviewing_no_config']}")
    print(f"  Config only (no reviews): {summary['config_no_reviews']}")
    print(f"  Not configured: {summary['not_configured']}")
    print(f"\nCodeRabbit Review Activity:")
    print(f"  Total PRs reviewed: {summary['total_prs_reviewed']}")
    print(f"  CodeRabbit reviewed first: {summary['total_coderabbit_first_reviews']} ({summary['coderabbit_first_review_pct']}%)")
    print(f"\nData saved to:")
    print(f"  Main file: {data_file}")
    print(f"  Historical copy: {historical_file}")
    print(f"Last updated: {summary['last_updated']}")


if __name__ == "__main__":
    main()