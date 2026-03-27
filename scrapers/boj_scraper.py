"""
Bank of Japan (BOJ) Scraper
- Uses official BOJ Time-Series Data API (launched Feb 2026)
- Fetches overnight call rate
"""

import requests
from datetime import datetime
import time
from config import BOJ_API_BASE, REQUEST_TIMEOUT, RETRY_COUNT, RETRY_DELAY


def fetch_boj_overnight_call_rate():
    """
    Fetch BOJ Overnight Call Rate from official BOJ API

    Returns:
        dict with 'label', 'unit', 'data' (list of {date, value} dicts)
    """
    url = f"{BOJ_API_BASE}/getDataCode"

    params = {
        'lang': 'EN',
        'db': 'FM01',
        'code': 'STRDCLUCON',  # Overnight call rate
        'startDate': '1998-01-05',
        'endDate': datetime.now().strftime('%Y-%m-%d'),
        'format': 'json'
    }

    print("Fetching BOJ overnight call rate...")

    for attempt in range(RETRY_COUNT):
        try:
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            result = response.json()

            # BOJ API response structure: {result: [{date: "YYYY-MM-DD", value: "X.XX"}, ...]}
            observations = result.get('result', [])

            data = []
            for obs in observations:
                try:
                    date_str = obs.get('date')
                    value_str = obs.get('value')

                    # Skip if missing
                    if not date_str or value_str == '':
                        continue

                    data.append({
                        'date': date_str,
                        'value': float(value_str)
                    })
                except (ValueError, KeyError, TypeError):
                    continue

            # Sort by date
            data.sort(key=lambda x: x['date'])

            print(f"  [OK] Found {len(data)} observations")
            return {
                'label': 'BOJ Overnight Call Rate',
                'unit': '% p.a.',
                'data': data
            }

        except requests.RequestException as e:
            print(f"  [ERROR] Attempt {attempt + 1}/{RETRY_COUNT} failed: {e}")
            if attempt < RETRY_COUNT - 1:
                time.sleep(RETRY_DELAY)
            else:
                raise


def scrape_boj():
    """
    Scrape all BOJ data

    Returns:
        dict with 'boj_rate'
    """
    return {
        'boj_rate': fetch_boj_overnight_call_rate()
    }


if __name__ == '__main__':
    import json
    data = scrape_boj()
    print("\n=== BOJ Data ===")
    print(json.dumps(data, indent=2))
