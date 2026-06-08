#!/usr/bin/env python3
"""
Update the historical data manifest file.

This script scans the data/ directory for historical JSON files and creates
a manifest that the dashboard uses to load trend data dynamically.

Should be run after fetch scripts to keep the manifest up to date.
"""

import json
import os
from pathlib import Path
from datetime import datetime


def update_manifest():
    """Scan data directory and create manifest of historical files."""
    data_dir = Path('data')

    if not data_dir.exists():
        print("❌ data/ directory not found")
        return

    # Find all historical files
    openshift_files = sorted(data_dir.glob('coderabbit-openshift-status_[0-9]*.json'))
    eee_files = sorted(data_dir.glob('coderabbit-EEE-status_[0-9]*.json'))

    manifest = {
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'openshift': [],
        'eee': []
    }

    # Process OpenShift files
    for file_path in openshift_files:
        filename = file_path.name
        timestamp = filename.replace('coderabbit-openshift-status_', '').replace('.json', '')
        manifest['openshift'].append({
            'filename': filename,
            'timestamp': timestamp,
            'path': f'data/{filename}'
        })

    # Process EEE files
    for file_path in eee_files:
        filename = file_path.name
        timestamp = filename.replace('coderabbit-EEE-status_', '').replace('.json', '')
        manifest['eee'].append({
            'filename': filename,
            'timestamp': timestamp,
            'path': f'data/{filename}'
        })

    # Write manifest
    manifest_path = data_dir / 'historical-manifest.json'
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"✅ Manifest updated: {manifest_path}")
    print(f"   OpenShift files: {len(manifest['openshift'])}")
    print(f"   EEE files: {len(manifest['eee'])}")
    print(f"   Total: {len(manifest['openshift']) + len(manifest['eee'])} historical snapshots")


if __name__ == "__main__":
    update_manifest()
