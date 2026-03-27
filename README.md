# Vietnam Macro Dashboard

A web application that tracks Vietnamese and global macroeconomic indicators with automatic daily updates.

## 📊 Features

- **Real-time data tracking** for 11 key economic indicators
- **Automatic updates** twice daily (7 AM & 9 PM Vietnam time)
- **Interactive charts** with zoom, pan, and hover tooltips
- **Free hosting** on GitHub Pages
- **No server required** - runs entirely on GitHub Actions

## 📈 Indicators Tracked

### 1. Interest Rates
- Fed Funds Rate (USA)
- Bank of Japan Overnight Call Rate
- Bank of England Bank Rate
- NHNN Vietnam Refinancing Rate

### 2. Exchange Rates (USD/VND)
- NHNN Official Reference Rate
- Vietcombank Commercial Rate
- Black Market Rate

### 3. Gold Prices
- SJC Gold Sell Price (Vietnam)
- World Gold Spot Price (USD/oz)

### 4. Fuel Prices
- RON95-III Gasoline (Vietnam)
- Brent Crude Oil (Global)

## 🚀 Quick Start

### 1. Initial Setup

```bash
# Clone or create the repo
git clone https://github.com/YOUR_USERNAME/macro-web.git
cd macro-web

# Install Python dependencies (for local testing)
pip install -r requirements.txt
```

### 2. Configure FRED API Key

1. Register free FRED API key at: https://fred.stlouisfed.org/docs/api/fred/
2. Add to GitHub Secrets:
   - Go to repo Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `FRED_API_KEY`
   - Value: Your API key

### 3. Prepare Seed Data

Create two CSV files with your historical data:

**`seed/nhnn_refi_rate_seed.csv`** — NHNN Refinancing Rate
```csv
date,value
2010-01-01,8.00
2010-03-15,9.50
2011-05-01,14.00
...
```

**`seed/black_market_seed.csv`** — Black Market USD/VND Rate
```csv
date,value
2010-01-01,19500
2011-01-01,21000
...
```

### 4. Import Seed Data

```bash
# From project root
python scripts/import_seed.py
```

This will merge your seed data with scraped data.

### 5. Initial Data Scrape

```bash
# From project root, scrape historical data
cd scrapers
python run_all.py
```

⚠️ **Warning**: First run may take 15-30 minutes to scrape all historical data from 2010 onwards.

### 6. Deploy to GitHub Pages

1. Push all code to GitHub
2. Go to repo Settings → Pages
3. Select source: `main` branch, `/root` (or `/docs` if you move `index.html` there)
4. Your site will be live at: `https://YOUR_USERNAME.github.io/macro-web/`

## 📋 Project Structure

```
macro-web/
├── .github/workflows/
│   └── update-data.yml           # GitHub Actions cron job
├── scrapers/
│   ├── config.py                 # Configuration & API keys
│   ├── fred_scraper.py           # Fed Funds Rate, Brent crude
│   ├── boj_scraper.py            # Bank of Japan rate
│   ├── boe_scraper.py            # Bank of England rate
│   ├── exchange_rate_scraper.py  # FX rates (NHNN, VCB, black market)
│   ├── gold_fuel_scraper.py      # Gold & fuel prices
│   └── run_all.py                # Master orchestrator
├── scripts/
│   └── import_seed.py            # Import user-provided CSV data
├── seed/
│   ├── nhnn_refi_rate_seed.csv   # Your NHNN rate history
│   └── black_market_seed.csv     # Your black market FX history
├── data/                         # Auto-generated JSON data (committed to repo)
│   ├── interest_rates.json
│   ├── exchange_rates.json
│   ├── gold_prices.json
│   └── fuel_prices.json
├── index.html                    # Dashboard website
├── style.css                     # Styling
├── charts.js                     # Chart.js visualization
└── requirements.txt
```

## 🔄 Data Update Schedule

- **7:00 AM Vietnam time** (UTC+7) = 00:00 UTC
- **9:00 PM Vietnam time** (UTC+7) = 14:00 UTC

Updates run automatically via GitHub Actions. You can manually trigger updates:

1. Go to repo → Actions tab
2. Select "Update Macro Data" workflow
3. Click "Run workflow"

## 📚 Data Sources

| Indicator | Source | Update Frequency |
|-----------|--------|------------------|
| Fed Funds Rate | FRED API | Monthly |
| BOJ Rate | Bank of Japan API | Daily |
| BOE Rate | Bank of England CSV API | Monthly |
| NHNN Rate (seed) | Manual import | As provided |
| NHNN Ref Rate | tygiausd.org | Daily |
| Vietcombank FX | webgia.com | Daily |
| Black Market FX | tygiausd.org + seed | Daily + historical |
| SJC Gold | webgia.com | Daily |
| World Gold | Yahoo Finance | Daily |
| RON95-III | PVOIL | Daily |
| Brent Crude | FRED API | Daily |

## 🛠️ Local Development

### Run scrapers locally:

```bash
cd scrapers
python run_all.py
```

### View the dashboard:

```bash
# Using Python's built-in server
python -m http.server 8000
# Open http://localhost:8000
```

### Debug a specific scraper:

```bash
cd scrapers
python fred_scraper.py      # Test FRED scraper
python boj_scraper.py       # Test BOJ scraper
python exchange_rate_scraper.py
# etc.
```

## 🐛 Troubleshooting

### "FRED API Key not found"
- Ensure `FRED_API_KEY` is set in GitHub Secrets
- Or set locally: `export FRED_API_KEY=your_key_here`

### "No data returned" from scrapers
- Check internet connection
- Verify website hasn't changed structure (common for webgia.com)
- Check GitHub Actions logs for detailed errors

### Charts not displaying
- Verify `data/*.json` files exist and have proper format
- Check browser console for JavaScript errors
- Ensure Chart.js library loaded: `https://cdn.jsdelivr.net/npm/chart.js@4.4.0`

### Git push fails in Actions
- Ensure branch protection rules allow Actions commits
- Check that Actions has write permissions (Settings → Actions → General)

## 📝 Notes

- **Playwright requirement**: Some scrapers use Playwright for JavaScript-heavy websites. GitHub Actions automatically installs it.
- **Rate limiting**: Scrapers include delays (0.3s) between requests to respect website policies.
- **Historical data**: User must provide seed CSV for indicators with limited scraping history (SJC Gold from 2010, tygiausd.org from 2015).
- **Data preservation**: JSON files are committed to repo, so full history is always preserved.

## 🤝 Contributing

To add new indicators:

1. Create new scraper in `scrapers/`
2. Add to `run_all.py` orchestrator
3. Create corresponding chart in `charts.js`
4. Update section in `index.html`
5. Document in this README

## 📄 License

Open source - use freely

## 📧 Support

For issues:
1. Check GitHub Actions logs (Actions tab)
2. Review website structure (may have changed)
3. Test scraper independently: `python scrapers/SCRAPER_NAME.py`

---

**Last updated**: March 2026
**Dashboard**: [Live Demo](https://YOUR_USERNAME.github.io/macro-web/)
