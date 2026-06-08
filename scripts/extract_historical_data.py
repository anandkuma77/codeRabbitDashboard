#!/usr/bin/env python3
"""
Extract historical CodeRabbit data from git commits.

This script:
1. Finds all commits that updated the data files
2. Extracts the file contents from each commit
3. Saves them as timestamped historical files using the commit timestamp

Usage:
    python3 scripts/extract_historical_data.py [--days DAYS]

Options:
    --days DAYS     Number of days of history to extract (default: 7)
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run_git_command(cmd):
    """Run a git command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {e}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        return None


def get_commits_for_file(file_path, days=7):
    """Get list of commits that modified a file in the last N days."""
    cmd = f'git log --since="{days} days ago" --format="%H|%ai" --all -- {file_path}'
    output = run_git_command(cmd)

    if not output:
        return []

    commits = []
    for line in output.split('\n'):
        if line:
            commit_hash, timestamp = line.split('|', 1)
            commits.append({
                'hash': commit_hash,
                'timestamp': timestamp,
                'file': file_path
            })

    return commits


def get_file_content_at_commit(commit_hash, file_path):
    """Get file content from a specific commit."""
    cmd = f'git show {commit_hash}:{file_path}'
    content = run_git_command(cmd)

    if content:
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from commit {commit_hash}: {e}", file=sys.stderr)
            return None

    return None


def format_timestamp_for_filename(git_timestamp):
    """Convert git timestamp to filename format (YYYYMMDD_HHMMSS)."""
    # Parse git timestamp: "2026-06-06 01:12:47 +0000"
    dt = datetime.strptime(git_timestamp.rsplit(' ', 1)[0], '%Y-%m-%d %H:%M:%S')
    return dt.strftime('%Y%m%d_%H%M%S')


def extract_historical_data(days=7):
    """Extract historical data from git commits."""
    files_to_extract = [
        'data/coderabbit-openshift-status.json',
        'data/coderabbit-EEE-status.json'
    ]

    print(f"🔍 Searching for commits in the last {days} days...")

    total_extracted = 0

    for file_path in files_to_extract:
        print(f"\n📄 Processing {file_path}")

        # Get commits for this file
        commits = get_commits_for_file(file_path, days)

        if not commits:
            print(f"  No commits found for {file_path}")
            continue

        print(f"  Found {len(commits)} commits")

        # Extract data from each commit
        for i, commit in enumerate(commits, 1):
            print(f"  [{i}/{len(commits)}] {commit['hash'][:7]} - {commit['timestamp']}", end=" ")

            # Get file content at this commit
            data = get_file_content_at_commit(commit['hash'], file_path)

            if not data:
                print("❌ Failed to extract")
                continue

            # Generate filename with commit timestamp
            timestamp = format_timestamp_for_filename(commit['timestamp'])

            # Determine base filename
            if 'openshift' in file_path.lower():
                base_name = 'coderabbit-openshift-status'
            else:
                base_name = 'coderabbit-EEE-status'

            historical_file = f'data/{base_name}_{timestamp}.json'

            # Check if file already exists
            if Path(historical_file).exists():
                print(f"⏭️  Already exists: {historical_file}")
                continue

            # Write historical file
            try:
                with open(historical_file, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"✅ Saved to {historical_file}")
                total_extracted += 1
            except Exception as e:
                print(f"❌ Error writing file: {e}")

    print(f"\n{'='*60}")
    print(f"✅ Extraction complete!")
    print(f"Total historical files created: {total_extracted}")
    print(f"{'='*60}")

    # Update historical manifest
    if total_extracted > 0:
        print(f"\n📋 Updating historical manifest...")
        try:
            subprocess.run(['python3', 'scripts/update_manifest.py'], check=True, capture_output=True)
            print(f"✅ Manifest updated")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Failed to update manifest: {e}", file=sys.stderr)


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description='Extract historical CodeRabbit data from git commits'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days of history to extract (default: 7)'
    )

    args = parser.parse_args()

    # Verify we're in a git repository
    if not run_git_command('git rev-parse --git-dir'):
        print("❌ Not in a git repository!", file=sys.stderr)
        sys.exit(1)

    # Create data directory if it doesn't exist
    Path('data').mkdir(exist_ok=True)

    # Extract historical data
    extract_historical_data(args.days)


if __name__ == "__main__":
    main()
