#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawl SJC Gold prices from webgia.com
Using urllib + regex to avoid dependency issues
"""

import json
import sys
import time
import re
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

def crawl_gold_prices():
    """Crawl SJC gold prices from webgia.com"""

    print("[INFO] Starting SJC gold price scraping")
    print("[INFO] Source: https://webgia.com/gia-vang/sjc/")
    print("[INFO] Date range: 2008-01-01 to 2026-03-27")
    print("[INFO] Sampling: every 7 days\n")

    gold_data = []
    start_date = datetime(2008, 1, 1)
    end_date = datetime(2026, 3, 27)
    current_date = start_date
    day_step = 7

    success_count = 0
    error_count = 0

    while current_date <= end_date:
        date_str = current_date.strftime('%d-%m-%Y')
        url = f"https://webgia.com/gia-vang/sjc/{date_str}.html"

        try:
            # Create request with User-Agent
            req = Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })

            print(f"[FETCH] {date_str}... ", end='', flush=True)

            with urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8', errors='ignore')

                # Look for price patterns in HTML
                # webgia.com typically has prices in table cells or spans
                # Pattern: numbers like 70123, 70.123, etc (in VND)

                # Try to find price in table rows
                table_rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)

                found = False
                for row in table_rows:
                    cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)

                    if len(cells) >= 2:
                        # Look for price in cells
                        for cell in cells:
                            # Clean HTML tags
                            clean = re.sub(r'<[^>]*>', '', cell)
                            clean = clean.strip()

                            # Extract numbers
                            numbers = re.findall(r'[\d.,]+', clean)

                            for num_str in numbers:
                                try:
                                    # Remove separators
                                    num_str_clean = num_str.replace(',', '').replace('.', '')

                                    if len(num_str_clean) >= 4:
                                        price = float(num_str) / 1000 if ',' in num_str or '.' in num_str else float(num_str_clean) / 1000

                                        # SJC gold price range check (50-85 million VND)
                                        if 50 < price < 85:
                                            gold_data.append({
                                                "date": current_date.strftime('%Y-%m-%d'),
                                                "value": round(price, 2)
                                            })
                                            print(f"[OK] {price:.2f}M VND")
                                            found = True
                                            success_count += 1
                                            break
                                except:
                                    pass

                            if found:
                                break

                    if found:
                        break

                if not found:
                    print("[NOTFOUND]")
                    error_count += 1

        except HTTPError as e:
            print(f"[HTTP {e.code}]")
            error_count += 1
        except URLError as e:
            print(f"[URLERROR]")
            error_count += 1
        except Exception as e:
            print(f"[ERROR: {str(e)[:20]}]")
            error_count += 1

        time.sleep(0.3)  # Throttle requests
        current_date += timedelta(days=day_step)

    print(f"\n{'='*60}")
    print(f"[SUMMARY] Crawling complete!")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total collected: {len(gold_data)}")
    print(f"{'='*60}\n")

    if gold_data:
        # Sort by date
        gold_data_sorted = sorted(gold_data, key=lambda x: x['date'])

        # Save to JSON
        output_data = {
            "sjc_gold": {
                "label": "SJC Gold Sell Price",
                "unit": "Million VND per tael",
                "data": gold_data_sorted
            }
        }

        output_path = "data/gold_prices.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"[SUCCESS] Saved to {output_path}")
        print(f"  Total data points: {len(gold_data_sorted)}")
        print(f"  Date range: {gold_data_sorted[0]['date']} to {gold_data_sorted[-1]['date']}")
        return True
    else:
        print("[WARNING] No data collected - website structure may have changed")
        print("[INFO] Consider using Playwright-based scraper instead")
        return False

if __name__ == '__main__':
    try:
        result = crawl_gold_prices()
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n[CANCELLED] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FATAL] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
