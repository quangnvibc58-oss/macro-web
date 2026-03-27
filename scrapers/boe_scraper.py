"""
Bank of England (BOE) Scraper
- Uses BOE's public CSV API
- Fetches Bank Rate (IUMABEDR series)
"""

import requests
import io
import pandas as pd
from datetime import datetime
import time
from config import REQUEST_TIMEOUT, RETRY_COUNT, RETRY_DELAY


def fetch_boe_bank_rate():
    """
    Fetch BOE Bank Rate from BOE's CSV API

    Returns:
        dict with 'label', 'unit', 'data' (list of {date, value} dicts)
    """
    url = "https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp"

    params = {
        'csv.x': 'yes',
        'Datefrom': '01/Jan/1975',
        'Dateto': datetime.now().strftime('%d/%b/%Y'),
        'SeriesCodes': 'IUMABEDR',  # Bank Rate series
        'CSVF': 'TN',  # Tabular, no titles
        'UsingCodes': 'Y',
        'VPD': 'Y',
        'VFD': 'N'
    }

    print("Fetching BOE Bank Rate...")

    for attempt in range(RETRY_COUNT):
        try:
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            # Parse CSV
            df = pd.read_csv(io.StringIO(response.text), header=None)

            data = []
            for idx, row in df.iterrows():
                try:
                    # Format: date (e.g., "31 Jan 1975"), value
                    date_str = row[0].strip()
                    value_str = row[1].strip()

                    # Parse date "31 Jan 1975" -> "1975-01-31"
                    from datetime import datetime as dt
                    date_obj = dt.strptime(date_str, '%d %b %Y')
                    formatted_date = date_obj.strftime('%Y-%m-%d')

                    data.append({
                        'date': formatted_date,
                        'value': float(value_str)
                    })
                except (ValueError, IndexError, AttributeError):
                    continue

            # Sort by date
            data.sort(key=lambda x: x['date'])

            print(f"  ✓ Found {len(data)} observations")
            return {
                'label': 'BOE Bank Rate',
                'unit': '% p.a.',
                'data': data
            }

        except Exception as e:
            print(f"  ✗ Attempt {attempt + 1}/{RETRY_COUNT} failed: {e}")
            if attempt < RETRY_COUNT - 1:
                time.sleep(RETRY_DELAY)
            else:
                raise


def scrape_boe():
    """
    Scrape all BOE data

    Returns:
        dict with 'boe_rate'
    """
    return {
        'boe_rate': fetch_boe_bank_rate()
    }


if __name__ == '__main__':
    import json
    data = scrape_boe()
    print("\n=== BOE Data ===")
    print(json.dumps(data, indent=2, default=str))
