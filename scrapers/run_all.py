"""
Main orchestrator: run all scrapers and save to JSON files
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fred_scraper import scrape_all_fred_series
from boj_alternative_scraper import scrape_boj
from boe_alternative_scraper import scrape_boe
from exchange_rate_scraper import scrape_exchange_rates
from gold_fuel_scraper import scrape_gold_fuel


def merge_data(existing, new):
    """
    Merge new data with existing data, avoiding duplicates

    For each series, keeps all existing data and adds new unique dates
    """
    if not existing or not existing.get('data'):
        return new

    # Create set of existing dates
    existing_dates = {item['date'] for item in existing.get('data', [])}

    # Merge
    merged_data = existing.get('data', []).copy()
    for item in new.get('data', []):
        if item['date'] not in existing_dates:
            merged_data.append(item)

    # Sort by date
    merged_data.sort(key=lambda x: x['date'])

    return {
        'label': new.get('label', existing.get('label')),
        'unit': new.get('unit', existing.get('unit')),
        'data': merged_data
    }


def save_json(data, filename):
    """Save data to JSON file"""
    filepath = Path(__file__).parent.parent / 'data' / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  [OK] Saved to {filepath}")
    return filepath


def load_json(filename):
    """Load existing JSON file if it exists"""
    filepath = Path(__file__).parent.parent / 'data' / filename
    if filepath.exists():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"  ! Error loading {filename}: {e}")
            return {}
    return {}


def main():
    print("=" * 60)
    print("MACRO DASHBOARD - DATA UPDATE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    all_data = {}

    # 1. Scrape FRED (Fed Funds + Brent)
    print("\n[1/5] Scraping FRED data...")
    try:
        fred_data = scrape_all_fred_series()
        existing = load_json('interest_rates.json')

        # Merge and save
        interest_rates = existing.copy() if existing else {}
        for key, value in fred_data.items():
            if key in interest_rates:
                interest_rates[key] = merge_data(interest_rates[key], value)
            else:
                interest_rates[key] = value

        save_json(interest_rates, 'interest_rates.json')
        all_data['interest_rates'] = interest_rates
    except Exception as e:
        print(f"  [ERROR] Error: {e}")

    time.sleep(1)

    # 2. Scrape BOJ
    print("\n[2/5] Scraping BOJ data...")
    try:
        boj_data = scrape_boj()
        existing = load_json('interest_rates.json')

        interest_rates = existing.copy() if existing else all_data.get('interest_rates', {})
        for key, value in boj_data.items():
            if key in interest_rates:
                interest_rates[key] = merge_data(interest_rates[key], value)
            else:
                interest_rates[key] = value

        save_json(interest_rates, 'interest_rates.json')
        all_data['interest_rates'] = interest_rates
    except Exception as e:
        print(f"  [ERROR] Error: {e}")

    time.sleep(1)

    # 3. Scrape BOE
    print("\n[3/5] Scraping BOE data...")
    try:
        boe_data = scrape_boe()
        existing = load_json('interest_rates.json')

        interest_rates = existing.copy() if existing else all_data.get('interest_rates', {})
        for key, value in boe_data.items():
            if key in interest_rates:
                interest_rates[key] = merge_data(interest_rates[key], value)
            else:
                interest_rates[key] = value

        save_json(interest_rates, 'interest_rates.json')
        all_data['interest_rates'] = interest_rates
    except Exception as e:
        print(f"  [ERROR] Error: {e}")

    time.sleep(1)

    # 4. Scrape Exchange Rates
    print("\n[4/5] Scraping exchange rates...")
    try:
        ex_data = scrape_exchange_rates()
        existing = load_json('exchange_rates.json')

        exchange_rates = existing.copy() if existing else {}
        for key, value in ex_data.items():
            if key in exchange_rates:
                exchange_rates[key] = merge_data(exchange_rates[key], value)
            else:
                exchange_rates[key] = value

        save_json(exchange_rates, 'exchange_rates.json')
        all_data['exchange_rates'] = exchange_rates
    except Exception as e:
        print(f"  [ERROR] Error: {e}")

    time.sleep(1)

    # 5. Scrape Gold & Fuel
    print("\n[5/5] Scraping gold and fuel prices...")
    try:
        gf_data = scrape_gold_fuel()

        # Gold prices
        existing_gold = load_json('gold_prices.json')
        gold_prices = existing_gold.copy() if existing_gold else {}

        for key in ['sjc_gold', 'world_gold']:
            if key in gf_data:
                if key in gold_prices:
                    gold_prices[key] = merge_data(gold_prices[key], gf_data[key])
                else:
                    gold_prices[key] = gf_data[key]

        if gold_prices:
            save_json(gold_prices, 'gold_prices.json')
            all_data['gold_prices'] = gold_prices

        # Fuel prices
        existing_fuel = load_json('fuel_prices.json')
        fuel_prices = existing_fuel.copy() if existing_fuel else {}

        for key in ['ron95_iii', 'brent_crude']:
            if key in gf_data:
                if key in fuel_prices:
                    fuel_prices[key] = merge_data(fuel_prices[key], gf_data[key])
                else:
                    fuel_prices[key] = gf_data[key]
            elif key in all_data.get('interest_rates', {}) and key == 'brent_crude':
                # Brent was already added to interest_rates by FRED, move it to fuel
                fuel_prices['brent_crude'] = all_data['interest_rates'].pop('brent_crude', None)

        if fuel_prices:
            save_json(fuel_prices, 'fuel_prices.json')
            all_data['fuel_prices'] = fuel_prices

    except Exception as e:
        print(f"  [ERROR] Error: {e}")

    print("\n" + "=" * 60)
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == '__main__':
    main()
