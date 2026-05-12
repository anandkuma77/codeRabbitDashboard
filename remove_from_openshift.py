#!/usr/bin/env python3
"""
Remove repos from coderabbit-openshift-status.json that exist in
coderabbit-EEE-status.json (avoid duplicates between the two files).
"""

import json
from datetime import datetime

def calculate_summary(repos):
    """Calculate summary statistics from repos list."""
    total = len(repos)
    fully_active = sum(1 for r in repos if r['category'] == 'fully_active')
    reviewing_no_config = sum(1 for r in repos if r['category'] == 'reviewing_no_config')
    config_no_reviews = sum(1 for r in repos if r['category'] == 'config_no_reviews')
    not_configured = sum(1 for r in repos if r['category'] == 'not_configured')

    has_config_total = sum(1 for r in repos if r.get('has_config', False))
    has_reviews_total = sum(1 for r in repos if r.get('has_coderabbit_reviews', False))

    total_prs_reviewed = sum(r.get('coderabbit_pr_count', 0) for r in repos)
    total_coderabbit_first = sum(r.get('coderabbit_first_review_count', 0) for r in repos)

    coderabbit_first_review_pct = round(
        total_coderabbit_first / total_prs_reviewed * 100, 1
    ) if total_prs_reviewed > 0 else 0

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
        'coderabbit_first_review_pct': coderabbit_first_review_pct,
        'last_updated': datetime.utcnow().isoformat() + 'Z'
    }

def main():
    # Load both files
    print("Loading data files...")
    with open('data/coderabbit-openshift-status.json', 'r') as f:
        openshift_data = json.load(f)

    with open('data/coderabbit-EEE-status.json', 'r') as f:
        eee_data = json.load(f)

    # Create set of EEE repo keys (owner/repo)
    eee_keys = set()
    for repo in eee_data['repos']:
        key = f"{repo['owner']}/{repo['repo']}"
        eee_keys.add(key)

    print(f"EEE repos: {len(eee_keys)}")
    print(f"Openshift repos before filtering: {len(openshift_data['repos'])}")

    # Keep only openshift repos that are NOT in EEE
    filtered_openshift_repos = []
    removed_repos = []

    for openshift_repo in openshift_data['repos']:
        key = f"{openshift_repo['owner']}/{openshift_repo['repo']}"

        if key in eee_keys:
            # This repo exists in EEE, remove it from openshift
            removed_repos.append(key)
            print(f"  ✗ Removed: {key}")
        else:
            # Keep this repo (not in EEE)
            filtered_openshift_repos.append(openshift_repo)

    print(f"\nRemoved {len(removed_repos)} repos that exist in EEE")
    print(f"Kept {len(filtered_openshift_repos)} repos in Openshift")

    # Recalculate summary statistics
    print("\nRecalculating summary statistics...")
    summary = calculate_summary(filtered_openshift_repos)

    # Combine summary and repos
    output_data = summary.copy()
    output_data['repos'] = filtered_openshift_repos

    # Write back to openshift file
    print("Writing updated data to coderabbit-openshift-status.json...")
    with open('data/coderabbit-openshift-status.json', 'w') as f:
        json.dump(output_data, f, indent=2)

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY OF CHANGES")
    print("="*60)
    print(f"Total repos in Openshift (after): {summary['total']}")
    print(f"Repos removed (exist in EEE): {len(removed_repos)}")
    print(f"Fully active: {summary['fully_active']}")
    print(f"Reviewing (no config): {summary['reviewing_no_config']}")
    print(f"Config only (no reviews): {summary['config_no_reviews']}")
    print(f"Not configured: {summary['not_configured']}")
    print(f"\nTotal PRs reviewed: {summary['total_prs_reviewed']}")
    print(f"CodeRabbit reviewed first: {summary['total_coderabbit_first_reviews']} ({summary['coderabbit_first_review_pct']}%)")
    print(f"\nLast updated: {summary['last_updated']}")
    print("="*60)

    print("\nRepos removed from Openshift:")
    for repo in removed_repos:
        print(f"  - {repo}")

if __name__ == "__main__":
    main()
