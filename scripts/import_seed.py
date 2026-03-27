"""
Import seed data from CSV/Excel files
Converts user-provided historical data into JSON format
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime


def import_csv_seed(csv_file, series_name, label, unit):
    """
    Import CSV seed data

    CSV format expected:
        date,value
        2010-01-01,8.00
        2010-03-15,9.50
        ...

    Args:
        csv_file: path to CSV file
        series_name: key name for the series
        label: human-readable label
        unit: unit of measurement

    Returns:
        dict with series data, or None if error
    """
    try:
        df = pd.read_csv(csv_file)

        # Normalize column names
        df.columns = [col.strip().lower() for col in df.columns]

        data = []
        for idx, row in df.iterrows():
            try:
                date_str = str(row.get('date')).strip()
                value_str = str(row.get('value')).strip()

                # Parse date if not already in YYYY-MM-DD format
                if len(date_str) == 10 and date_str.count('-') == 2:
                    # Already in YYYY-MM-DD format
                    date = date_str
                else:
                    # Try to parse common formats
                    for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%Y/%m/%d']:
                        try:
                            parsed = datetime.strptime(date_str, fmt)
                            date = parsed.strftime('%Y-%m-%d')
                            break
                        except ValueError:
                            continue
                    else:
                        print(f"  ! Could not parse date: {date_str}")
                        continue

                value = float(value_str.replace(',', ''))
                data.append({'date': date, 'value': value})

            except (ValueError, AttributeError) as e:
                print(f"  ! Row {idx}: {e}")
                continue

        # Sort by date
        data.sort(key=lambda x: x['date'])

        print(f"  ✓ Imported {len(data)} rows from {csv_file}")

        return {
            'label': label,
            'unit': unit,
            'data': data
        }

    except Exception as e:
        print(f"  ✗ Error reading {csv_file}: {e}")
        return None


def merge_seed_with_existing(seed_data, existing_data):
    """
    Merge seed data with existing data, avoiding duplicates

    Args:
        seed_data: new seed data (from CSV)
        existing_data: existing data (from JSON)

    Returns:
        merged data
    """
    if not existing_data or not existing_data.get('data'):
        return seed_data

    # Create dict of existing data by date for easy lookup
    existing_dict = {item['date']: item['value'] for item in existing_data.get('data', [])}

    # Merge: seed data takes precedence for overlapping dates
    merged = seed_data['data'].copy()
    seed_dates = {item['date'] for item in merged}

    for item in existing_data.get('data', []):
        if item['date'] not in seed_dates:
            merged.append(item)

    merged.sort(key=lambda x: x['date'])

    return {
        'label': seed_data.get('label', existing_data.get('label')),
        'unit': seed_data.get('unit', existing_data.get('unit')),
        'data': merged
    }


def load_json(filepath):
    """Load JSON file if exists"""
    if Path(filepath).exists():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"  ! Error loading {filepath}: {e}")
            return {}
    return {}


def save_json(data, filepath):
    """Save data to JSON file"""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Saved to {filepath}")


def import_nhnn_refi_rate():
    """Import NHNN refinancing rate from seed CSV"""
    print("\n[1/2] Importing NHNN refinancing rate...")

    seed_file = Path(__file__).parent.parent / 'seed' / 'nhnn_refi_rate_seed.csv'

    if not seed_file.exists():
        print(f"  ! Seed file not found: {seed_file}")
        print(f"     Please create: {seed_file}")
        return None

    seed_data = import_csv_seed(
        seed_file,
        'nhnn_refi_rate',
        'NHNN Refinancing Rate',
        '% p.a.'
    )

    if seed_data is None:
        return None

    # Load existing interest rates JSON
    output_file = Path(__file__).parent.parent / 'data' / 'interest_rates.json'
    existing = load_json(output_file)

    # Merge
    if 'nhnn_refi_rate' in existing:
        seed_data = merge_seed_with_existing(seed_data, existing['nhnn_refi_rate'])

    # Save back to interest_rates.json
    existing['nhnn_refi_rate'] = seed_data
    save_json(existing, output_file)

    return seed_data


def import_black_market_fx():
    """Import black market FX from seed CSV"""
    print("\n[2/2] Importing black market FX rates...")

    seed_file = Path(__file__).parent.parent / 'seed' / 'black_market_seed.csv'

    if not seed_file.exists():
        print(f"  ! Seed file not found: {seed_file}")
        print(f"     Please create: {seed_file}")
        return None

    seed_data = import_csv_seed(
        seed_file,
        'black_market_rate',
        'Black Market Exchange Rate (USD/VND)',
        'VND/USD'
    )

    if seed_data is None:
        return None

    # Load existing exchange rates JSON
    output_file = Path(__file__).parent.parent / 'data' / 'exchange_rates.json'
    existing = load_json(output_file)

    # Merge
    if 'black_market_rate' in existing:
        seed_data = merge_seed_with_existing(seed_data, existing['black_market_rate'])

    # Save back to exchange_rates.json
    existing['black_market_rate'] = seed_data
    save_json(existing, output_file)

    return seed_data


def main():
    print("=" * 60)
    print("SEED DATA IMPORT")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    import_nhnn_refi_rate()
    import_black_market_fx()

    print("\n" + "=" * 60)
    print("Import completed!")
    print("=" * 60)


if __name__ == '__main__':
    main()
