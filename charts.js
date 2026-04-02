/**
 * Vietnam Macro Dashboard - Complete Chart.js Implementation
 * With proper data filtering by time period
 */

const COLORS = {
    fed: '#3b82f6',
    boj: '#ef4444',
    boe: '#10b981',
    nhnn: '#f59e0b',
    vietcombank: '#8b5cf6',
    blackmarket: '#ec4899',
    sjc: '#eab308',
    worldgold: '#06b6d4',
    ron95: '#f97316',
    brent: '#6366f1'
};

let chartsData = {};
let charts = {};

// Time period configurations (in days)
const PERIODS = {
    day: 180,      // Last 180 data points ≈ 6 months for daily data
    week: 1008,    // Last 144 weeks * 7 days ≈ 2.8 years
    month: 1800,   // Last 60 months * 30 days ≈ 5 years
    year: Infinity // All data
};

/**
 * Load JSON data from server
 */
async function loadData(filename) {
    try {
        const resp = await fetch(`./data/${filename}`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        return await resp.json();
    } catch (error) {
        console.error(`Failed to load ${filename}:`, error);
        return {};
    }
}

/**
 * Filter data by date range (in days from today)
 */
function filterDataByDays(data, days) {
    if (days === Infinity) return data;

    // For "Ngày" (day) filter with daily data: return last 180 points
    // For "Tuần" (week): return last 144 weeks * 7 = 1008 days
    // For "Tháng" (month): return last 60 months * 30 = 1800 days

    // If we have very few points (monthly data), show proportionally more
    if (data.length < 50) {
        // For monthly/quarterly data, show last N*2 points (more coverage)
        const pointsToShow = Math.max(24, Math.floor(data.length * 0.4));
        return data.slice(-pointsToShow);
    }

    // For daily data, calculate date cutoff
    const today = new Date();
    const cutoffDate = new Date(today.getTime() - days * 24 * 60 * 60 * 1000);
    const cutoffStr = cutoffDate.toISOString().split('T')[0];

    const filtered = data.filter(item => item.date >= cutoffStr);

    // Ensure we show at least some data even for sparse datasets
    if (filtered.length === 0 && data.length > 0) {
        return data.slice(-Math.max(12, Math.floor(data.length * 0.3)));
    }

    return filtered;
}

/**
 * Filter data by number of points (for simpler filtering)
 */
function filterDataByPoints(data, points) {
    if (points === Infinity) return data;
    return data.slice(-points);
}

/**
 * Create professional Chart.js chart
 */
function createChart(canvasId, datasets, yLabel) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas ${canvasId} not found`);
        return null;
    }

    try {
        // Destroy existing chart if any
        if (charts[canvasId]) {
            charts[canvasId].destroy();
        }

        // Extract dates from first dataset
        const labels = datasets.length > 0
            ? datasets[0].data.map((_, i) => datasets[0].dates[i])
            : [];

        // Remove dates from datasets (Chart.js doesn't need them in the data array)
        const cleanDatasets = datasets.map(ds => {
            const { dates, ...rest } = ds;
            return rest;
        });

        charts[canvasId] = new Chart(canvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: cleanDatasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 15,
                            font: { size: 11 },
                            color: 'rgba(248, 250, 252, 0.8)'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.9)',
                        padding: 12,
                        titleFont: { size: 12 },
                        bodyFont: { size: 11 },
                        borderColor: 'rgba(255,255,255,0.2)',
                        borderWidth: 1,
                        displayColors: true,
                        callbacks: {
                            title: (ctx) => ctx[0]?.label || '',
                            label: (ctx) => {
                                let str = ctx.dataset.label + ': ' + ctx.parsed.y.toFixed(2);
                                if (ctx.dataset.unit) str += ' ' + ctx.dataset.unit;
                                return str;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        title: { display: true, text: yLabel, font: { size: 11 } },
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: 'rgba(248, 250, 252, 0.6)' }
                    },
                    x: {
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: 'rgba(248, 250, 252, 0.6)' }
                    }
                }
            }
        });

        return charts[canvasId];
    } catch (error) {
        console.error(`Chart error for ${canvasId}:`, error);
        return null;
    }
}

/**
 * Prepare dataset with date information preserved
 */
function prepareDataset(label, data, color, unit) {
    if (!data || data.length === 0) return null;

    return {
        label: label,
        data: data.map(d => d.value),
        dates: data.map(d => d.date),
        borderColor: color,
        backgroundColor: color + '15',
        borderWidth: 2.5,
        fill: false,
        tension: 0.3,
        pointRadius: 0.5,
        pointHoverRadius: 5,
        unit: unit
    };
}

/**
 * Initialize Interest Rates Chart
 */
async function initInterestRates() {
    const data = await loadData('interest_rates.json');
    const datasets = [];
    const seriesMap = [
        { key: 'fed_funds', label: 'Fed Funds', color: COLORS.fed },
        { key: 'boj_rate', label: 'BOJ Rate', color: COLORS.boj },
        { key: 'boe_rate', label: 'BOE Bank Rate', color: COLORS.boe },
        { key: 'nhnn_refi_rate', label: 'NHNN Refi Rate', color: COLORS.nhnn }
    ];

    for (const series of seriesMap) {
        if (data[series.key]?.data?.length > 0) {
            const ds = prepareDataset(
                data[series.key].label,
                data[series.key].data,
                series.color,
                data[series.key].unit
            );
            if (ds) datasets.push(ds);
        }
    }

    chartsData.interest = datasets;
    if (datasets.length > 0) {
        createChart('interestRatesChart', datasets, '% per annum');
    }
}

/**
 * Initialize Exchange Rates Chart
 */
async function initExchangeRates() {
    const data = await loadData('exchange_rates.json');
    const datasets = [];
    const seriesMap = [
        { key: 'nhnn_central', label: 'NHNN Central Rate', color: '#06b6d4' },
        { key: 'vcb_sell', label: 'Vietcombank Sell', color: COLORS.vietcombank },
        { key: 'free_market_sell', label: 'Black Market', color: COLORS.blackmarket },
        { key: 'sbv_sell', label: 'SBV Rate', color: '#a855f7' }
    ];

    for (const series of seriesMap) {
        if (data[series.key]?.data?.length > 0) {
            const ds = prepareDataset(
                data[series.key].label || series.label,
                data[series.key].data,
                series.color,
                data[series.key].unit || 'VND/USD'
            );
            if (ds) datasets.push(ds);
        }
    }

    chartsData.exchange = datasets;
    if (datasets.length > 0) {
        createChart('exchangeRatesChart', datasets, 'VND per USD');
    }
}

/**
 * Initialize Gold Prices Charts
 */
async function initGoldPrices() {
    const data = await loadData('gold_prices.json');

    // SJC Gold
    if (data.sjc_gold?.data?.length > 0) {
        const datasets = [prepareDataset(
            data.sjc_gold.label,
            data.sjc_gold.data,
            COLORS.sjc,
            data.sjc_gold.unit
        )];
        chartsData.sjc = datasets;
        createChart('sjcGoldChart', datasets, 'Million VND per tael');
    }

    // World Gold
    if (data.world_gold?.data?.length > 0) {
        const datasets = [prepareDataset(
            data.world_gold.label,
            data.world_gold.data,
            COLORS.worldgold,
            data.world_gold.unit
        )];
        chartsData.worldGold = datasets;
        createChart('worldGoldChart', datasets, 'USD per troy oz');
    }
}

/**
 * Initialize Fuel Prices Charts
 */
async function initFuelPrices() {
    const data = await loadData('fuel_prices.json');

    // RON95-III
    if (data.ron95_iii?.data?.length > 0) {
        const datasets = [prepareDataset(
            data.ron95_iii.label,
            data.ron95_iii.data,
            COLORS.ron95,
            data.ron95_iii.unit
        )];
        chartsData.ron95 = datasets;
        createChart('ron95Chart', datasets, 'VND per liter');
    }

    // Brent Crude
    if (data.brent_crude?.data?.length > 0) {
        const datasets = [prepareDataset(
            data.brent_crude.label,
            data.brent_crude.data,
            COLORS.brent,
            data.brent_crude.unit
        )];
        chartsData.brent = datasets;
        createChart('brentChart', datasets, 'USD per barrel');
    }
}

/**
 * Update chart by filtering data
 */
function updateChartByPeriod(chartKey, period) {
    const rawDatasets = chartsData[chartKey];
    if (!rawDatasets) return;

    const days = PERIODS[period] || PERIODS.month;

    const filteredDatasets = rawDatasets.map(ds => {
        // Get original data with dates
        const originalData = ds.dates.map((date, i) => ({
            date: date,
            value: ds.data[i]
        }));

        // Filter by days
        const filtered = filterDataByDays(originalData, days);

        return {
            ...ds,
            data: filtered.map(d => d.value),
            dates: filtered.map(d => d.date)
        };
    });

    const yLabels = {
        interest: '% per annum',
        exchange: 'VND per USD',
        sjc: 'Million VND per tael',
        worldGold: 'USD per troy oz',
        ron95: 'VND per liter',
        brent: 'USD per barrel'
    };

    const canvasIds = {
        interest: 'interestRatesChart',
        exchange: 'exchangeRatesChart',
        sjc: 'sjcGoldChart',
        worldGold: 'worldGoldChart',
        ron95: 'ron95Chart',
        brent: 'brentChart'
    };

    createChart(canvasIds[chartKey], filteredDatasets, yLabels[chartKey]);
}

/**
 * Setup time filter button handlers
 */
function setupTimeFilters() {
    document.querySelectorAll('.time-filter button').forEach(button => {
        button.addEventListener('click', function() {
            const filterGroup = this.parentElement;
            const chartName = filterGroup.getAttribute('data-chart');
            const period = this.getAttribute('data-period');

            // Update active button
            filterGroup.querySelectorAll('button').forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            // Update chart
            updateChartByPeriod(chartName, period);
        });
    });
}

/**
 * Update timestamp
 */
function updateTimestamp() {
    const now = new Date();
    const timeStr = now.toLocaleString('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    const lastUpdateEl = document.getElementById('lastUpdate');
    if (lastUpdateEl) lastUpdateEl.textContent = timeStr;
}

/**
 * Initialize dashboard
 */
async function initDashboard() {
    console.log('[Dashboard] Starting initialization...');
    updateTimestamp();

    try {
        console.log('[Dashboard] Loading interest rates...');
        await initInterestRates();

        console.log('[Dashboard] Loading exchange rates...');
        await initExchangeRates();

        console.log('[Dashboard] Loading gold prices...');
        await initGoldPrices();

        console.log('[Dashboard] Loading fuel prices...');
        await initFuelPrices();

        console.log('[Dashboard] Setting up time filters...');
        setupTimeFilters();

        console.log('[Dashboard] Dashboard ready!');
        const loadedCount = Object.keys(chartsData).length;
        console.log(`[Dashboard] ${loadedCount} chart groups initialized`);
    } catch (error) {
        console.error('[Dashboard] Initialization error:', error);
    }
}

/**
 * Run on page load
 */
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
} else {
    initDashboard();
}
