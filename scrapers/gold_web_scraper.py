#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrape SJC Gold prices from webgia.com
Requires: playwright, beautifulsoup4
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    from playwright.async_api import async_playwright
    import pandas as pd
except ImportError:
    print("[ERROR] Please install: pip install playwright beautifulsoup4 pandas")
    sys.exit(1)

async def scrape_gold_prices():
    """Scrape SJC gold prices from webgia.com using Playwright"""

    print("[INFO] Starting SJC gold price scraping from webgia.com")
    print("[INFO] Date range: 2008-01-01 to 2026-03-27")
    print("[INFO] This will take time - sampling every 7 days for efficiency...\n")

    gold_data = []
    start_date = datetime(2008, 1, 1)
    end_date = datetime(2026, 3, 27)
    current_date = start_date
    day_step = 7

    success_count = 0
    error_count = 0

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        while current_date <= end_date:
            date_str = current_date.strftime('%d-%m-%Y')
            url = f"https://webgia.com/gia-vang/sjc/{date_str}.html"

            try:
                print(f"[FETCH] {date_str}... ", end='', flush=True)
                await page.goto(url, wait_until='load', timeout=10000)

                # Wait for table to load
                try:
                    await page.wait_for_selector('table', timeout=5000)
                except:
                    print("[NOTFOUND]")
                    error_count += 1
                    current_date += timedelta(days=day_step)
                    await asyncio.sleep(0.5)
                    continue

                # Extract table data
                rows_data = await page.evaluate("""
                    () => {
                        const tables = document.querySelectorAll('table');
                        const results = [];
                        tables.forEach(table => {
                            const rows = table.querySelectorAll('tr');
                            rows.forEach(row => {
                                const cells = row.querySelectorAll('td');
                                if (cells.length > 0) {
                                    const text = Array.from(cells).map(c => c.textContent.trim()).join('|');
                                    results.push(text);
                                }
                            });
                        });
                        return results;
                    }
                """)

                # Parse for price
                found = False
                for row_text in rows_data:
                    parts = row_text.split('|')
                    for part in parts:
                        # Clean and extract numbers
                        clean = part.replace(',', '').replace('.', '').replace(' ', '')
                        try:
                            if len(clean) >= 5 and clean.isdigit():
                                price = float(clean) / 1000
                                if 50 < price < 90:  # SJC gold range
                                    gold_data.append({
                                        "date": current_date.strftime('%Y-%m-%d'),
                                        "value": price
                                    })
                                    success_count += 1
                                    print(f"[OK] {price:.2f}M VND")
                                    found = True
                                    break
                        except:
                            pass
                    if found:
                        break

                if not found:
                    print("[PARSE_FAILED]")
                    error_count += 1

            except asyncio.TimeoutError:
                print("[TIMEOUT]")
                error_count += 1
            except Exception as e:
                print(f"[ERROR: {str(e)[:20]}]")
                error_count += 1

            current_date += timedelta(days=day_step)
            await asyncio.sleep(0.8)  # Throttle

        await browser.close()

    print(f"\n{'='*60}")
    print(f"[SUMMARY] Scraping complete!")
    print(f"  Successes: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"{'='*60}\n")

    if success_count > 0:
        # Save to JSON
        gold_data_sorted = sorted(gold_data, key=lambda x: x['date'])
        gold_json = {
            "sjc_gold": {
                "label": "SJC Gold Sell Price",
                "unit": "Million VND per tael",
                "data": gold_data_sorted
            }
        }

        output_path = Path(__file__).parent.parent / 'data' / 'gold_prices.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(gold_json, f, ensure_ascii=False, indent=2)

        print(f"[SUCCESS] Saved to {output_path}")
        print(f"  Total points: {len(gold_data_sorted)}")
        print(f"  Date range: {gold_data_sorted[0]['date']} to {gold_data_sorted[-1]['date']}")
        return True
    else:
        print("[ERROR] No data collected")
        return False

if __name__ == '__main__':
    try:
        result = asyncio.run(scrape_gold_prices())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n[CANCELLED] User interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        sys.exit(1)
