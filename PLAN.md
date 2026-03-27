# Kế hoạch xây dựng Vietnam Macro Dashboard

## Tổng quan

Website theo dõi các chỉ số kinh tế vĩ mô Việt Nam và thế giới, tự động cập nhật 2 lần/ngày (7h sáng và 9h tối giờ Việt Nam), hoàn toàn miễn phí trên GitHub Pages.

---

## Kiến trúc hệ thống

```
GitHub Actions chạy cron 2x/ngày
    → Python scrapers thu thập dữ liệu
    → Lưu vào file JSON trong repo
    → GitHub Pages phục vụ website tĩnh
```

**Không cần server riêng, không tốn phí hosting.**

---

## Cấu trúc thư mục dự án

```
macro-web/
├── .github/
│   └── workflows/
│       └── update-data.yml        ← Cron job tự động
├── scrapers/
│   ├── config.py                  ← FRED API key, cấu hình
│   ├── fred_scraper.py            ← Fed Funds Rate + Brent crude (FRED API)
│   ├── boj_scraper.py             ← Lãi suất BOJ (BOJ API)
│   ├── boe_scraper.py             ← Lãi suất BOE (BOE CSV API)
│   ├── vietcombank_scraper.py     ← Tỷ giá Vietcombank (webgia.com)
│   ├── nhnn_exchange_scraper.py   ← Tỷ giá NHNN (tygiausd.org)
│   ├── black_market_scraper.py    ← Tỷ giá chợ đen (tygiausd.org)
│   ├── sjc_gold_scraper.py        ← Giá vàng SJC (webgia.com)
│   ├── gold_world_scraper.py      ← Giá vàng thế giới (Yahoo Finance)
│   ├── pvoil_scraper.py           ← Giá RON95-III (PVOIL)
│   └── run_all.py                 ← Chạy tất cả, lưu JSON
├── seed/
│   ├── nhnn_refi_rate_seed.csv    ← Bạn cung cấp: lịch sử lãi suất NHNN
│   └── black_market_seed.csv      ← Bạn cung cấp: lịch sử tỷ giá chợ đen
├── scripts/
│   └── import_seed.py             ← Import CSV của bạn vào JSON (chạy 1 lần)
├── data/
│   ├── interest_rates.json        ← Dữ liệu lãi suất (tự động cập nhật)
│   ├── exchange_rates.json        ← Dữ liệu tỷ giá
│   ├── gold_prices.json           ← Dữ liệu giá vàng
│   └── fuel_prices.json           ← Dữ liệu giá nhiên liệu
├── index.html                     ← Trang dashboard chính
├── style.css
├── charts.js                      ← Khởi tạo Chart.js, fetch + render
└── requirements.txt
```

---

## Chi tiết từng nguồn dữ liệu

### 1. Lãi suất

| Chỉ số | Nguồn | Cách lấy | Lịch sử |
|--------|-------|----------|---------|
| Fed Funds Rate (Mỹ) | FRED API | `requests` JSON | Từ 1954 |
| Lãi suất BOJ (Nhật) | BOJ API chính thức (ra mắt 2026) | `requests` JSON | Từ 1998 |
| Lãi suất BOE (Anh) | BOE CSV API (series IUMABEDR) | `requests` CSV | Từ 1975 |
| Lãi suất tái cấp vốn NHNN | **Bạn cung cấp file CSV** | seed import | Toàn bộ |

### 2. Tỷ giá USD/VND

| Chỉ số | Nguồn | Cách lấy | Lịch sử |
|--------|-------|----------|---------|
| Tỷ giá NHNN chính thức | tygiausd.org | `requests` + BeautifulSoup | Từ 2015 |
| Tỷ giá Vietcombank (bán ra) | webgia.com | Playwright (JS-rendered) | Từ 2010 |
| Tỷ giá chợ đen | tygiausd.org + **CSV của bạn** | requests + seed | Từ 2015 (+ seed trước đó) |

### 3. Giá vàng

| Chỉ số | Nguồn | Cách lấy | Lịch sử |
|--------|-------|----------|---------|
| Giá vàng SJC (bán ra) | webgia.com/gia-vang/sjc/ | `requests` + pandas | Từ 2010 |
| Giá vàng thế giới (Gold Futures) | Yahoo Finance (GC=F) | `yfinance` | Từ 2000 |

### 4. Giá nhiên liệu

| Chỉ số | Nguồn | Cách lấy | Lịch sử |
|--------|-------|----------|---------|
| Giá RON95-III Việt Nam | PVOIL (endpoint AJAX nội bộ) | `requests` | Từ 2018 |
| Giá dầu Brent thế giới | FRED API (DCOILBRENTEU) | `requests` JSON | Từ 1987 |

---

## Giao diện website

**4 section dọc**, mỗi section là một nhóm chỉ số:

```
┌─────────────────────────────────────────────┐
│  🏦 LÃI SUẤT                                │
│  [Chart: Fed / BOJ / BOE / NHNN trên 1 biểu│
│   đồ, trục Y là %, có thể zoom/pan]         │
├─────────────────────────────────────────────┤
│  💵 TỶ GIÁ USD/VND                          │
│  [Chart: NHNN / Vietcombank / Chợ đen]      │
├─────────────────────────────────────────────┤
│  🥇 GIÁ VÀNG                                │
│  [Chart trái: SJC (VND/lượng)]              │
│  [Chart phải: Gold Futures (USD/oz)]        │
├─────────────────────────────────────────────┤
│  ⛽ GIÁ NHIÊN LIỆU                          │
│  [Chart trái: RON95 Việt Nam (VND/lít)]     │
│  [Chart phải: Brent crude (USD/barrel)]     │
└─────────────────────────────────────────────┘
```

**Tính năng chart:**
- Di chuột vào → tooltip hiện ngày + giá trị cụ thể
- Zoom bằng chuột, kéo để pan
- Nhiều series màu khác nhau, có legend
- Responsive (mobile + desktop)

---

## GitHub Actions — Lịch cập nhật

```yaml
schedule:
  - cron: '0 0 * * *'    # 7:00 sáng giờ Việt Nam (00:00 UTC)
  - cron: '0 14 * * *'   # 9:00 tối giờ Việt Nam (14:00 UTC)
```

Mỗi lần chạy:
1. Pull repo mới nhất
2. Chạy tất cả scrapers
3. Merge với dữ liệu cũ (không xóa lịch sử)
4. Commit file JSON mới vào repo
5. GitHub Pages tự động serve bản mới

---

## Các bước triển khai

| Bước | Việc cần làm |
|------|-------------|
| 1 | Tạo GitHub repo public `macro-web` |
| 2 | Viết các Python scrapers |
| 3 | Build frontend HTML/CSS/Chart.js |
| 4 | Cấu hình GitHub Actions + thêm secret `FRED_API_KEY` |
| 5 | **Bạn upload 2 file CSV seed** (format: `date,value`) |
| 6 | Chạy initial scrape thủ công (lấy toàn bộ lịch sử, ~15-30 phút) |
| 7 | Bật GitHub Pages → website live tại `https://[username].github.io/macro-web/` |

---

## Định dạng CSV seed bạn cần cung cấp

**File 1: `nhnn_refi_rate_seed.csv`** — Lãi suất tái cấp vốn NHNN
```csv
date,value
2010-01-01,8.00
2011-05-01,14.00
2012-03-13,13.00
...
```

**File 2: `black_market_seed.csv`** — Tỷ giá chợ đen USD/VND
```csv
date,value
2010-01-01,19500
2011-01-01,21000
...
```
*(Cột `value` là giá bán ra, đơn vị VND/USD)*

---

## Lưu ý kỹ thuật

- **Playwright** cần cài thêm trong GitHub Actions: `playwright install chromium --with-deps` (dùng cho webgia.com vì JS-rendered)
- **Scrape lịch sử lần đầu** sẽ tốn 15-30 phút do cần loop qua từng ngày từ 2010→nay; cần delay 0.3s/request để tránh bị block
- **tygiausd.org** có dữ liệu từ 2015 → bạn cần cung cấp seed cho giai đoạn trước 2015 nếu cần
- **FRED API key** sẽ được lưu vào GitHub Secrets, không lộ trong code
