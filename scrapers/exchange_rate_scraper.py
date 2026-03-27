"""
Exchange Rate Scrapers
- NHNN official rate from tygiausd.org
- Vietcombank sell rate from webgia.com
- Black market FX from tygiausd.org
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import re
from config import REQUEST_TIMEOUT, RETRY_COUNT, RETRY_DELAY, SCRAPE_DELAY


def scrape_tygiausd_rates(date_str):
    """
    Scrape USD/VND rates from tygiausd.org for a specific date

    Args:
        date_str: date in format "DD-MM-YYYY"

    Returns:
        tuple: (nhnn_rate, black_market_rate) or (None, None) if failed
        where each rate is {'buy': float, 'sell': float}
    """
    url = f"https://tygiausd.org/TyGia?date={date_str}"

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find sections with exchange rate data
        # Look for text patterns like "Tỷ giá USD tự do" and "NHNN"

        text = soup.get_text()
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        nhnn_rate = None
        black_market_rate = None

        # Try to find NHNN rate and black market rate
        for i, line in enumerate(lines):
            # Black market FX pattern: "USD tự do" or "usd tự do"
            if 'tự do' in line.lower() and 'usd' in line.lower():
                # Next lines should contain "Mua" and "Bán" with values
                for j in range(i + 1, min(i + 10, len(lines))):
                    next_line = lines[j]
                    if 'Mua' in next_line or 'mua' in next_line:
                        # Extract number
                        numbers = re.findall(r'[\d,]+', next_line)
                        if numbers:
                            buy_val = float(numbers[0].replace(',', ''))
                            if j + 1 < len(lines):
                                sell_line = lines[j + 1]
                                if 'Bán' in sell_line or 'bán' in sell_line:
                                    sell_numbers = re.findall(r'[\d,]+', sell_line)
                                    if sell_numbers:
                                        sell_val = float(sell_numbers[0].replace(',', ''))
                                        black_market_rate = {'buy': buy_val, 'sell': sell_val}
                            break

        # If black market found, look for NHNN (usually before or after)
        # NHNN is typically labeled as "Ngân hàng" or "NHNN"
        for i, line in enumerate(lines):
            if 'NHNN' in line or ('Ngân hàng' in line and 'Nhà nước' in line):
                for j in range(i + 1, min(i + 10, len(lines))):
                    next_line = lines[j]
                    if 'Mua' in next_line or 'mua' in next_line:
                        numbers = re.findall(r'[\d,]+', next_line)
                        if numbers:
                            buy_val = float(numbers[0].replace(',', ''))
                            if j + 1 < len(lines):
                                sell_line = lines[j + 1]
                                if 'Bán' in sell_line or 'bán' in sell_line:
                                    sell_numbers = re.findall(r'[\d,]+', sell_line)
                                    if sell_numbers:
                                        sell_val = float(sell_numbers[0].replace(',', ''))
                                        nhnn_rate = {'buy': buy_val, 'sell': sell_val}
                            break

        return nhnn_rate, black_market_rate

    except requests.RequestException as e:
        print(f"    Error fetching {date_str}: {e}")
        return None, None


def scrape_vietcombank_rate(date_str):
    """
    Scrape Vietcombank sell rate from webgia.com

    Args:
        date_str: date in format "DD-MM-YYYY"

    Returns:
        float: USD/VND sell rate, or None if failed
    """
    url = f"https://webgia.com/ty-gia/vietcombank/{date_str}.html"

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        response.encoding = 'utf-8'

        # Try to parse HTML table
        import pandas as pd
        tables = pd.read_html(response.text)

        # Find USD row in Vietcombank table
        for table in tables:
            # Look for USD row
            for idx, row in table.iterrows():
                row_str = str(row).lower()
                if 'usd' in row_str:
                    # Last column is usually sell rate
                    values = [float(str(v).replace(',', '')) for v in row if str(v) != 'nan' and str(v) != 'USD']
                    if values:
                        return values[-1]  # Last value is sell rate

        return None

    except Exception as e:
        # This is expected to fail sometimes due to JS rendering
        return None


def scrape_historical_rates(days_back=7):
    """
    Scrape historical rates for the last N days

    Args:
        days_back: number of days to scrape back

    Returns:
        dict with 'nhnn_rate', 'vietcombank_rate', 'black_market_rate'
    """
    nhnn_data = []
    vietcombank_data = []
    black_market_data = []

    today = datetime.now()

    for i in range(days_back):
        date = today - timedelta(days=i)
        date_str = date.strftime('%d-%m-%Y')

        print(f"  Scraping rates for {date_str}...")

        # Scrape tygiausd.org
        nhnn_rate, black_market_rate = scrape_tygiausd_rates(date_str)

        if nhnn_rate:
            nhnn_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'value': nhnn_rate['sell']  # Use sell rate
            })

        if black_market_rate:
            black_market_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'value': black_market_rate['sell']  # Use sell rate
            })

        # Scrape Vietcombank (may fail due to JS)
        vcb_rate = scrape_vietcombank_rate(date_str)
        if vcb_rate:
            vietcombank_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'value': vcb_rate
            })

        time.sleep(SCRAPE_DELAY)

    return {
        'nhnn_rate': {
            'label': 'NHNN Official Exchange Rate (USD/VND)',
            'unit': 'VND/USD',
            'data': sorted(nhnn_data, key=lambda x: x['date'])
        },
        'vietcombank_rate': {
            'label': 'Vietcombank Sell Rate (USD/VND)',
            'unit': 'VND/USD',
            'data': sorted(vietcombank_data, key=lambda x: x['date'])
        },
        'black_market_rate': {
            'label': 'Black Market Exchange Rate (USD/VND)',
            'unit': 'VND/USD',
            'data': sorted(black_market_data, key=lambda x: x['date'])
        }
    }


def scrape_exchange_rates():
    """
    Scrape recent exchange rates

    Returns:
        dict with exchange rate series
    """
    print("Fetching exchange rates...")
    return scrape_historical_rates(days_back=7)


if __name__ == '__main__':
    import json
    data = scrape_exchange_rates()
    print("\n=== Exchange Rate Data ===")
    print(json.dumps(data, indent=2, default=str))
