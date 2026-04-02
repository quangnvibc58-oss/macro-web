#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawl SJC Gold prices from webgia.com using Playwright
Playwright opens a real browser and executes JavaScript
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

async def crawl_gold_with_playwright():
    """Crawl SJC gold prices using Playwright browser automation"""

    from playwright.async_api import async_playwright

    print("[INFO] Starting SJC gold price scraping with Playwright")
    print("[INFO] Source: https://webgia.com/gia-vang/sjc/")
    print("[INFO] Sampling every 14 days for faster crawling\n")

    gold_data = []
    start_date = datetime(2010, 1, 1)  # webgia data from 2010
    end_date = datetime(2026, 3, 27)
    current_date = start_date
    day_step = 14  # Sample every 2 weeks

    success_count = 0
    error_count = 0

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        while current_date <= end_date:
            date_str = current_date.strftime('%d-%m-%Y')

            try:
                print(f"[{success_count+error_count:4d}] {date_str}... ", end='', flush=True)

                url = f"https://webgia.com/gia-vang/sjc/{date_str}.html"
                await page.goto(url, wait_until='networkidle', timeout=15000)

                # Wait for table to load (max 5 seconds)
                try:
                    await page.wait_for_selector('table', timeout=5000)
                except:
                    print("[TABLE_NOTFOUND]")
                    error_count += 1
                    current_date += timedelta(days=day_step)
                    continue

                # Extract all text from table cells
                prices = await page.evaluate('''
                    () => {
                        const tables = document.querySelectorAll('table');
                        const results = [];

                        tables.forEach(table => {
                            const rows = table.querySelectorAll('tr');
                            rows.forEach(row => {
                                const cells = row.querySelectorAll('td');
                                cells.forEach(cell => {
                                    const text = cell.innerText.trim();
                                    if (text) results.push(text);
                                });
                            });
                        });

                        return results;
                    }
                ''')

                # Parse for SJC gold price
                found = False
                for text in prices:
                    try:
                        # Remove spaces and commas
                        clean = text.replace(',', '').replace(' ', '').replace('.', '')

                        # Check if it's a number in the SJC gold price range
                        if clean.isdigit() and len(clean) >= 4:
                            price = float(clean) / 1000

                            # SJC gold is typically 55-80 million VND per tael
                            if 50 < price < 90:
                                gold_data.append({
                                    "date": current_date.strftime('%Y-%m-%d'),
                                    "value": round(price, 2)
                                })
                                print(f"[OK] {price:.2f}M")
                                success_count += 1
                                found = True
                                break
                    except:
                        pass

                if not found:
                    print("[PARSE_FAILED]")
                    error_count += 1

            except asyncio.TimeoutError:
                print("[TIMEOUT]")
                error_count += 1
            except Exception as e:
                print(f"[ERROR: {type(e).__name__}]")
                error_count += 1

            current_date += timedelta(days=day_step)
            await asyncio.sleep(0.5)

        await browser.close()

    print(f"\n{'='*60}")
    print(f"[COMPLETE] Scraping finished!")
    print(f"  Success: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total: {len(gold_data)}")
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

        output_path = Path(__file__).parent.parent / "data" / "gold_prices.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"[SUCCESS] Saved {len(gold_data_sorted)} data points to {output_path}")
        print(f"  Date range: {gold_data_sorted[0]['date']} to {gold_data_sorted[-1]['date']}")
        return True
    else:
        print("[ERROR] No data collected")
        return False

if __name__ == '__main__':
    try:
        result = asyncio.run(crawl_gold_with_playwright())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n[CANCELLED] Interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FATAL] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
