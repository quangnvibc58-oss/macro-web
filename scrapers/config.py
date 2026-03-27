import os
from datetime import datetime, timedelta

# FRED API Key
FRED_API_KEY = os.getenv('FRED_API_KEY', 'eb05f78f21330395c0d1df20fa235a3c')

# Base URLs
FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
BOJ_API_BASE = "https://www.stat-search.boj.or.jp/api/v1"
BOE_API_BASE = "https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp"

# FRED Series IDs
SERIES_IDS = {
    'fed_funds': 'FEDFUNDS',
    'brent_crude': 'DCOILBRENTEU',
}

# BOJ Series
BOJ_SERIES = {
    'overnight_call_rate': 'FM01:STRDCLUCON'  # Overnight call rate
}

# Requests settings
REQUEST_TIMEOUT = 15
RETRY_COUNT = 3
RETRY_DELAY = 1  # seconds

# Scrape settings
SCRAPE_DELAY = 0.3  # seconds between requests to avoid blocking
HISTORICAL_START_YEAR = 2010

# Date format
DATE_FORMAT = "%Y-%m-%d"
