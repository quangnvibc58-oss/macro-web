"""
FRED API Scraper for:
- Fed Funds Effective Rate (FEDFUNDS)
- Brent Crude Oil Price (DCOILBRENTEU)
"""

import requests
from datetime import datetime, timedelta
import time
from config import (
    FRED_API_KEY, FRED_BASE_URL, SERIES_IDS, REQUEST_TIMEOUT, RETRY_COUNT, RETRY_DELAY
)

def fetch_fred_series(series_id, label, unit, start_date=None):
    """
    Fetch a single FRED series

    Args:
        series_id: FRED series ID (e.g., 'FEDFUNDS')
        label: Human-readable label
        unit: Unit of measurement
        start_date: Optional start date (YYYY-MM-DD format)

    Returns:
        dict with 'label', 'unit', 'data' (list of {date, value} dicts)
    """
    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'limit': 100000,  # Fetch all data
    }

    if start_date:
        params['observation_start'] = start_date

    print(f"Fetching FRED series {series_id}...")

    for attempt in range(RETRY_COUNT):
        try:
            response = requests.get(FRED_BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            data_dict = response.json()
            observations = data_dict.get('observations', [])

            # Convert to our format, skip NaN values
            data = []
            for obs in observations:
                value = obs.get('value')
                if value != '.':  # FRED uses '.' for missing values
                    try:
                        data.append({
                            'date': obs['date'],
                            'value': float(value)
                        })
                    except (ValueError, KeyError):
                        continue

            print(f"  [OK] Found {len(data)} observations")
            return {
                'label': label,
                'unit': unit,
                'data': data
            }

        except requests.RequestException as e:
            print(f"  [ERROR] Attempt {attempt + 1}/{RETRY_COUNT} failed: {e}")
            if attempt < RETRY_COUNT - 1:
                time.sleep(RETRY_DELAY)
            else:
                raise


def scrape_all_fred_series():
    """
    Scrape all FRED series for interest rates and fuel

    Returns:
        dict with structure:
        {
            'fed_funds': {...},
            'brent_crude': {...}
        }
    """
    result = {}

    # Fed Funds Rate (monthly)
    result['fed_funds'] = fetch_fred_series(
        SERIES_IDS['fed_funds'],
        'Fed Funds Effective Rate',
        '% p.a.'
    )

    # Brent Crude Oil (daily)
    result['brent_crude'] = fetch_fred_series(
        SERIES_IDS['brent_crude'],
        'Brent Crude Oil Price',
        '$ per barrel'
    )

    return result


if __name__ == '__main__':
    import json
    data = scrape_all_fred_series()
    print("\n=== FRED Data ===")
    print(json.dumps(data, indent=2))
