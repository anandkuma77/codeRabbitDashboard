#!/usr/bin/env python3
"""
Remove repos from coderabbit-EEE-status.json that exist in
coderabbit-openshift-status.json (keep only unique EEE repos).
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
        'last_updated': datetime.now(datetime.UTC).isoformat().replace('+00:00', 'Z')
    }

def main():
    # Load both files
    print("Loading data files...")
    with open('data/coderabbit-openshift-status.json', 'r') as f:
        openshift_data = json.load(f)

    with open('data/coderabbit-EEE-status.json', 'r') as f:
        eee_data = json.load(f)

    # Create set of openshift repo keys (owner/repo)
    openshift_keys = set()
    for repo in openshift_data['repos']:
        key = f"{repo['owner']}/{repo['repo']}"
        openshift_keys.add(key)

    print(f"Openshift repos: {len(openshift_keys)}")
    print(f"EEE repos before filtering: {len(eee_data['repos'])}")

    # Keep only EEE repos that are NOT in openshift
    filtered_eee_repos = []
    removed_repos = []

    for eee_repo in eee_data['repos']:
        key = f"{eee_repo['owner']}/{eee_repo['repo']}"

        if key in openshift_keys:
            # This repo exists in openshift, remove it
            removed_repos.append(key)
            print(f"  ✗ Removed: {key}")
        else:
            # Keep this repo (unique to EEE)
            filtered_eee_repos.append(eee_repo)
            print(f"  ✓ Kept: {key}")

    print(f"\nRemoved {len(removed_repos)} duplicate repos")
    print(f"Kept {len(filtered_eee_repos)} unique EEE repos")

    if len(filtered_eee_repos) == 0:
        print("\n⚠️  WARNING: No unique repos left in EEE file!")
        print("All EEE repos exist in Openshift file.")
        response = input("Continue anyway and create empty EEE file? [y/N]: ")
        if response.lower() != 'y':
            print("Aborted. No changes made.")
            return

    # Recalculate summary statistics
    print("\nRecalculating summary statistics...")
    summary = calculate_summary(filtered_eee_repos)

    # Combine summary and repos
    output_data = summary.copy()
    output_data['repos'] = filtered_eee_repos

    # Write back to EEE file
    print("Writing updated data to coderabbit-EEE-status.json...")
    with open('data/coderabbit-EEE-status.json', 'w') as f:
        json.dump(output_data, f, indent=2)

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY OF CHANGES")
    print("="*60)
    print(f"Total repos in EEE (after): {summary['total']}")
    print(f"Repos removed (duplicates): {len(removed_repos)}")
    print(f"Fully active: {summary['fully_active']}")
    print(f"Reviewing (no config): {summary['reviewing_no_config']}")
    print(f"Config only (no reviews): {summary['config_no_reviews']}")
    print(f"Not configured: {summary['not_configured']}")
    print(f"\nTotal PRs reviewed: {summary['total_prs_reviewed']}")
    print(f"CodeRabbit reviewed first: {summary['total_coderabbit_first_reviews']} ({summary['coderabbit_first_review_pct']}%)")
    print(f"\nLast updated: {summary['last_updated']}")
    print("="*60)

if __name__ == "__main__":
    main()
