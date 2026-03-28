/**
 * Vietnam Macro Dashboard - Full Version
 * Advanced Chart.js with multiple indicators
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

let charts = {};

// Load JSON data
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

// Create professional chart
function createChart(canvasId, title, datasets, yLabel) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas ${canvasId} not found`);
        return null;
    }

    try {
        return new Chart(canvas, {
            type: 'line',
            data: { datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: { usePointStyle: true, padding: 15, font: { size: 11 } }
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
                        grid: { color: 'rgba(0,0,0,0.05)' }
                    },
                    x: { grid: { color: 'rgba(0,0,0,0.05)' } }
                }
            }
        });
    } catch (error) {
        console.error(`Chart error for ${canvasId}:`, error);
        return null;
    }
}

// Initialize Interest Rates
async function initInterestRates() {
    const data = await loadData('interest_rates.json');
    const datasets = [];
    const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b'];
    let idx = 0;

    for (let key in data) {
        if (data[key].data?.length > 0) {
            const last100 = data[key].data.slice(-100);
            datasets.push({
                label: data[key].label,
                data: last100.map(d => d.value),
                borderColor: colors[idx],
                backgroundColor: colors[idx] + '15',
                borderWidth: 2.5,
                fill: false,
                tension: 0.3,
                pointRadius: 1.5,
                pointHoverRadius: 5,
                unit: data[key].unit
            });
            idx++;
        }
    }

    if (datasets.length > 0) {
        charts.interest = createChart('interestRatesChart', 'Interest Rates', datasets, '% per annum');
    }
}

// Initialize Exchange Rates
async function initExchangeRates() {
    const data = await loadData('exchange_rates.json');
    const datasets = [];
    const colors = ['#06b6d4', '#8b5cf6', '#ec4899'];
    let idx = 0;

    for (let key in data) {
        if (data[key].data?.length > 0) {
            datasets.push({
                label: data[key].label,
                data: data[key].data.map(d => d.value),
                borderColor: colors[idx],
                backgroundColor: colors[idx] + '15',
                borderWidth: 2.5,
                fill: false,
                tension: 0.3,
                pointRadius: 1,
                pointHoverRadius: 5,
                unit: data[key].unit
            });
            idx++;
        }
    }

    if (datasets.length > 0) {
        charts.exchange = createChart('exchangeRatesChart', 'Exchange Rates', datasets, 'VND per USD');
    }
}

// Initialize Gold Prices
async function initGoldPrices() {
    const data = await loadData('gold_prices.json');

    // SJC Gold
    if (data.sjc_gold?.data?.length > 0) {
        const last50 = data.sjc_gold.data.slice(-50);
        charts.sjcGold = createChart('sjcGoldChart', 'SJC Gold', [{
            label: data.sjc_gold.label,
            data: last50.map(d => d.value),
            borderColor: '#eab308',
            backgroundColor: '#eab30815',
            borderWidth: 2.5,
            fill: false,
            tension: 0.3,
            unit: data.sjc_gold.unit
        }], 'Million VND per tael');
    }

    // World Gold
    if (data.world_gold?.data?.length > 0) {
        const last50 = data.world_gold.data.slice(-50);
        charts.worldGold = createChart('worldGoldChart', 'World Gold', [{
            label: data.world_gold.label,
            data: last50.map(d => d.value),
            borderColor: '#06b6d4',
            backgroundColor: '#06b6d415',
            borderWidth: 2.5,
            fill: false,
            tension: 0.3,
            unit: data.world_gold.unit
        }], 'USD per troy oz');
    }
}

// Initialize Fuel Prices
async function initFuelPrices() {
    const data = await loadData('fuel_prices.json');

    // RON95-III
    if (data.ron95_iii?.data?.length > 0) {
        const last50 = data.ron95_iii.data.slice(-50);
        charts.ron95 = createChart('ron95Chart', 'RON95-III', [{
            label: data.ron95_iii.label,
            data: last50.map(d => d.value),
            borderColor: '#f97316',
            backgroundColor: '#f9731615',
            borderWidth: 2.5,
            fill: false,
            tension: 0.3,
            unit: data.ron95_iii.unit
        }], 'VND per liter');
    }

    // Brent Crude
    if (data.brent_crude?.data?.length > 0) {
        const last100 = data.brent_crude.data.slice(-100);
        charts.brent = createChart('brentChart', 'Brent Crude', [{
            label: data.brent_crude.label,
            data: last100.map(d => d.value),
            borderColor: '#6366f1',
            backgroundColor: '#6366f115',
            borderWidth: 2.5,
            fill: false,
            tension: 0.3,
            unit: data.brent_crude.unit
        }], 'USD per barrel');
    }
}

// Update timestamp
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
    document.getElementById('lastUpdate').textContent = timeStr;
    document.getElementById('footerTime').textContent = timeStr;
}

// Initialize all charts
async function init() {
    console.log('[Dashboard] Starting initialization...');
    updateTimestamp();

    console.log('[Dashboard] Loading interest rates...');
    await initInterestRates();

    console.log('[Dashboard] Loading exchange rates...');
    await initExchangeRates();

    console.log('[Dashboard] Loading gold prices...');
    await initGoldPrices();

    console.log('[Dashboard] Loading fuel prices...');
    await initFuelPrices();

    console.log('[Dashboard] Dashboard ready!');

    // Show status
    const loaded = Object.keys(charts).length;
    console.log(`[Dashboard] ${loaded} charts initialized`);
}

// Run on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
