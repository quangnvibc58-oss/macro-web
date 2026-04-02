#!/usr/bin/env python3
"""
Import seed data from CSV files into JSON data files
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
        print(f"  [OK] Loaded {len(data)} points from {csv_path.name}")
        return data
    except Exception as e:
        print(f"  [ERROR] Failed to load {csv_path.name}: {e}")
        return []


def merge_data(existing, new):
    """Merge new data with existing, avoiding duplicates"""
    if not existing or not existing.get('data'):
        return new

    existing_dates = {item['date'] for item in existing.get('data', [])}
    merged_data = existing.get('data', []).copy()

    for item in new:
        if item['date'] not in existing_dates:
            merged_data.append(item)

    merged_data.sort(key=lambda x: x['date'])

    return {
        'label': existing.get('label', 'Unknown'),
        'unit': existing.get('unit', ''),
        'data': merged_data
    }


def import_seed_data():
    """Import all seed CSV files"""
    project_root = Path(__file__).parent.parent
    seed_dir = project_root / 'seed'
    data_dir = project_root / 'data'

    print("=" * 60)
    print("SEED DATA IMPORT")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # BOJ Rate seed
    print("\n[1/3] Importing BOJ Rate...")
    boj_csv = seed_dir / 'boj_rate_seed.csv'
    if boj_csv.exists():
        boj_data = load_csv(boj_csv)
        if boj_data:
            interest_rates_path = data_dir / 'interest_rates.json'
            interest_rates = {}
            if interest_rates_path.exists():
                try:
                    with open(interest_rates_path, 'r', encoding='utf-8') as f:
                        interest_rates = json.load(f)
                except:
                    pass

            if 'boj_rate' not in interest_rates:
                interest_rates['boj_rate'] = {
                    'label': 'BOJ Overnight Call Rate',
                    'unit': '% p.a.',
                    'data': boj_data
                }
            else:
                interest_rates['boj_rate'] = merge_data(
                    interest_rates['boj_rate'],
                    boj_data
                )

            with open(interest_rates_path, 'w', encoding='utf-8') as f:
                json.dump(interest_rates, f, indent=2, ensure_ascii=False)
            print(f"  [OK] Merged into interest_rates.json")

    # BOE Rate seed
    print("\n[2/3] Importing BOE Bank Rate...")
    boe_csv = seed_dir / 'boe_rate_seed.csv'
    if boe_csv.exists():
        boe_data = load_csv(boe_csv)
        if boe_data:
            interest_rates_path = data_dir / 'interest_rates.json'
            interest_rates = {}
            if interest_rates_path.exists():
                try:
                    with open(interest_rates_path, 'r', encoding='utf-8') as f:
                        interest_rates = json.load(f)
                except:
                    pass

            if 'boe_rate' not in interest_rates:
                interest_rates['boe_rate'] = {
                    'label': 'BOE Bank Rate',
                    'unit': '% p.a.',
                    'data': boe_data
                }
            else:
                interest_rates['boe_rate'] = merge_data(
                    interest_rates['boe_rate'],
                    boe_data
                )

            with open(interest_rates_path, 'w', encoding='utf-8') as f:
                json.dump(interest_rates, f, indent=2, ensure_ascii=False)
            print(f"  [OK] Merged into interest_rates.json")

    # SJC Gold seed
    print("\n[3/3] Importing SJC Gold prices...")
    sjc_csv = seed_dir / 'sjc_gold_seed.csv'
    if sjc_csv.exists():
        sjc_data = load_csv(sjc_csv)
        if sjc_data:
            gold_prices_path = data_dir / 'gold_prices.json'
            gold_prices = {}
            if gold_prices_path.exists():
                try:
                    with open(gold_prices_path, 'r', encoding='utf-8') as f:
                        gold_prices = json.load(f)
                except:
                    pass

            if 'sjc_gold' not in gold_prices:
                gold_prices['sjc_gold'] = {
                    'label': 'SJC Gold (Tael)',
                    'unit': 'Million VND per tael',
                    'data': sjc_data
                }
            else:
                gold_prices['sjc_gold'] = merge_data(
                    gold_prices['sjc_gold'],
                    sjc_data
                )

            with open(gold_prices_path, 'w', encoding='utf-8') as f:
                json.dump(gold_prices, f, indent=2, ensure_ascii=False)
            print(f"  [OK] Merged into gold_prices.json")

    print("\n" + "=" * 60)
    print("SEED DATA IMPORT COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    import_seed_data()
