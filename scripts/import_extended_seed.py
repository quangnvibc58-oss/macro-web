#!/usr/bin/env python3
"""
Import extended seed data from CSV files
"""

import json
import csv
from pathlib import Path
from datetime import datetime


def load_csv(csv_path):
    """Load CSV file and return list of {date, value} dicts"""
    data = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    data.append({
                        'date': row['date'].strip(),
                        'value': float(row['value'])
                    })
                except (ValueError, KeyError):
                    continue
        return data
    except Exception as e:
        print(f"  [ERROR] Failed to load {csv_path.name}: {e}")
        return []


def merge_data(existing, new):
    """Merge new data with existing, avoiding duplicates"""
    if not existing or not existing.get('data'):
        return new

    existing_dates = {item['date'] for item in existing.get('data', [])}
    merged_data = list(existing.get('data', []))

    for item in new:
        if item['date'] not in existing_dates:
            merged_data.append(item)

    merged_data.sort(key=lambda x: x['date'])

    return {
        'label': existing.get('label', 'Unknown'),
        'unit': existing.get('unit', ''),
        'data': merged_data
    }


def import_extended_seed():
    """Import all extended seed CSV files"""
    project_root = Path(__file__).parent.parent
    seed_dir = project_root / 'seed'
    data_dir = project_root / 'data'

    print("=" * 60)
    print("EXTENDED SEED DATA IMPORT")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Load interest rates
    interest_rates_path = data_dir / 'interest_rates.json'
    with open(interest_rates_path, 'r', encoding='utf-8') as f:
        interest_rates = json.load(f)

    # Import BOJ Extended
    print("\n[1/3] Importing Extended BOJ Rate...")
    boj_csv = seed_dir / 'extended_boj_rate.csv'
    if boj_csv.exists():
        boj_data = load_csv(boj_csv)
        print(f"  [OK] Loaded {len(boj_data)} points from extended_boj_rate.csv")
        interest_rates['boj_rate'] = merge_data(
            interest_rates.get('boj_rate', {}),
            boj_data
        )
        print(f"  [OK] BOJ now has {len(interest_rates['boj_rate']['data'])} points")

    # Import BOE Extended
    print("\n[2/3] Importing Extended BOE Rate...")
    boe_csv = seed_dir / 'extended_boe_rate.csv'
    if boe_csv.exists():
        boe_data = load_csv(boe_csv)
        print(f"  [OK] Loaded {len(boe_data)} points from extended_boe_rate.csv")
        interest_rates['boe_rate'] = merge_data(
            interest_rates.get('boe_rate', {}),
            boe_data
        )
        print(f"  [OK] BOE now has {len(interest_rates['boe_rate']['data'])} points")

    # Import NHNN Refi Extended
    print("\n[3/3] Importing Extended NHNN Refi Rate...")
    nhnn_csv = seed_dir / 'extended_nhnn_refi_rate.csv'
    if nhnn_csv.exists():
        nhnn_data = load_csv(nhnn_csv)
        print(f"  [OK] Loaded {len(nhnn_data)} points from extended_nhnn_refi_rate.csv")
        interest_rates['nhnn_refi_rate'] = merge_data(
            interest_rates.get('nhnn_refi_rate', {}),
            nhnn_data
        )
        print(f"  [OK] NHNN Refi now has {len(interest_rates['nhnn_refi_rate']['data'])} points")

    # Save updated interest_rates.json
    with open(interest_rates_path, 'w', encoding='utf-8') as f:
        json.dump(interest_rates, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("EXTENDED SEED DATA IMPORT COMPLETE")
    print("=" * 60)
    print("\nFinal Interest Rates Series:")
    for key, value in interest_rates.items():
        total = len(value.get('data', []))
        if total > 0:
            first = value['data'][0]['date']
            last = value['data'][-1]['date']
            print(f"  {key:20s}: {total:5d} points ({first} to {last})")


if __name__ == '__main__':
    import_extended_seed()
