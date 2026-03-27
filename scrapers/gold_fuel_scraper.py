"""
Gold & Fuel Price Scrapers
- SJC gold price from webgia.com
- World gold spot price from yfinance
- RON95-III gasoline from PVOIL
"""

import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time
import re
from config import REQUEST_TIMEOUT, SCRAPE_DELAY, RETRY_COUNT, RETRY_DELAY


def scrape_sjc_gold(date_str):
    """
    Scrape SJC gold sell price from webgia.com

    Args:
        date_str: date in format "DD-MM-YYYY"

    Returns:
        float: SJC gold sell price (VND per tael), or None
    """
    url = f"https://webgia.com/gia-vang/sjc/{date_str}.html"

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        tables = pd.read_html(response.text)

        # Find SJC table with "Bán ra" column
        for table in tables:
            if 'Bán ra' in table.columns or 'Bán ra' in str(table.columns):
                # Get the last row (end of day price)
                sell_col = None
                for col in table.columns:
                    if 'Bán' in str(col):
                        sell_col = col
                        break

                if sell_col is not None:
                    last_row = table.iloc[-1]
                    try:
                        value = float(str(last_row[sell_col]).replace(',', '').replace('.', ''))
                        # SJC prices are in millions of VND per tael
                        return value
                    except (ValueError, TypeError):
                        pass

        return None

    except Exception as e:
        return None


def scrape_historical_sjc_gold(days_back=7):
    """
    Scrape historical SJC gold prices

    Args:
        days_back: number of days to scrape

    Returns:
        list of {date, value} dicts
    """
    data = []
    today = datetime.now()

    for i in range(days_back):
        date = today - timedelta(days=i)
        date_str = date.strftime('%d-%m-%Y')

        price = scrape_sjc_gold(date_str)
        if price:
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'value': price
            })

        time.sleep(SCRAPE_DELAY)

    return sorted(data, key=lambda x: x['date'])


def fetch_world_gold_spot(start_date=None):
    """
    Fetch world gold spot price from yfinance

    Args:
        start_date: start date (YYYY-MM-DD format), defaults to 2 years ago

    Returns:
        list of {date, value} dicts, value in USD/oz
    """
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')

    print(f"Fetching world gold spot price (yfinance GC=F) from {start_date}...")

    try:
        # GC=F is gold futures on COMEX (proxy for spot)
        gold = yf.download('GC=F', start=start_date, progress=False)

        if gold.empty:
            print("  [ERROR] No data returned")
            return []

        # Use closing price
        data = []
        for idx, row in gold.iterrows():
            try:
                close_price = row['Close']
                if pd.notna(close_price):
                    data.append({
                        'date': idx.strftime('%Y-%m-%d'),
                        'value': float(close_price)
                    })
            except (ValueError, TypeError, AttributeError):
                pass

        print(f"  [OK] Found {len(data)} observations")
        return sorted(data, key=lambda x: x['date'])

    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        return []


def scrape_pvoil_gasoline(date_str=None):
    """
    Scrape RON95-III gasoline price from PVOIL

    Args:
        date_str: optional date in format "DD/MM/YYYY", defaults to today

    Returns:
        float: price in VND/liter, or None
    """
    if date_str is None:
        date_str = datetime.now().strftime('%d/%m/%Y')

    url = "https://pvoil.com.vn/en/petroleum-retail-price"

    try:
        # PVOIL page uses AJAX to load data
        # The main page gives us current prices
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find RON95-III row in the price table
        text = soup.get_text()
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        for i, line in enumerate(lines):
            if 'RON 95-III' in line or 'RON95-III' in line:
                # Next lines should have price
                for j in range(i, min(i + 5, len(lines))):
                    # Extract number pattern
                    numbers = re.findall(r'[\d,]+[\.\d]*', lines[j])
                    if numbers:
                        try:
                            price = float(numbers[0].replace(',', ''))
                            return price
                        except ValueError:
                            pass
                break

        return None

    except Exception as e:
        return None


def scrape_gold_fuel():
    """
    Scrape all gold and fuel prices

    Returns:
        dict with gold and fuel price series
    """
    print("Fetching gold and fuel prices...")

    result = {}

    # SJC gold (recent days)
    print("Scraping SJC gold...")
    sjc_data = scrape_historical_sjc_gold(days_back=7)
    result['sjc_gold'] = {
        'label': 'SJC Gold Sell Price',
        'unit': 'Million VND per tael',
        'data': sjc_data
    }

    # World gold spot
    world_gold_data = fetch_world_gold_spot()
    result['world_gold'] = {
        'label': 'World Gold Spot Price (Futures)',
        'unit': 'USD/oz',
        'data': world_gold_data
    }

    # PVOIL RON95-III (current only, historical needs AJAX reverse-engineering)
    print("Fetching PVOIL RON95-III...")
    pvoil_price = scrape_pvoil_gasoline()
    pvoil_data = []
    if pvoil_price:
        pvoil_data.append({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'value': pvoil_price
        })

    result['ron95_iii'] = {
        'label': 'Vietnam RON95-III Gasoline Price',
        'unit': 'VND/liter',
        'data': pvoil_data
    }

    return result


if __name__ == '__main__':
    import json
    data = scrape_gold_fuel()
    print("\n=== Gold & Fuel Data ===")
    print(json.dumps(data, indent=2, default=str))
