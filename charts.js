/**
 * Simple Chart.js initialization and data loading
 */

const COLORS = {
    blue: '#3b82f6',
    red: '#ef4444',
    green: '#10b981',
    yellow: '#f59e0b',
    purple: '#8b5cf6',
    pink: '#ec4899',
    indigo: '#6366f1',
    cyan: '#06b6d4'
};

const COLOR_ARRAY = Object.values(COLORS);
let charts = {};

async function loadData(filename) {
    try {
        const response = await fetch(`./data/${filename}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error(`Error loading ${filename}:`, error);
        return {};
    }
}

function createSimpleChart(canvasId, datasets, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas not found: ${canvasId}`);
        return null;
    }

    try {
        const chart = new Chart(ctx, {
            type: 'line',
            data: { datasets: datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { intersect: false, mode: 'index' },
                plugins: {
                    legend: { display: true, position: 'top' },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        padding: 12,
                        titleFont: { size: 13 },
                        bodyFont: { size: 12 },
                        displayColors: true,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) label += ': ';
                                if (context.parsed.y !== null) {
                                    label += context.parsed.y.toFixed(2);
                                }
                                if (context.dataset.unit) {
                                    label += ' ' + context.dataset.unit;
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        title: {
                            display: true,
                            text: options.yAxisLabel || 'Value'
                        }
                    }
                },
                ...options
            }
        });
        return chart;
    } catch (error) {
        console.error(`Error creating chart ${canvasId}:`, error);
        return null;
    }
}

async function initInterestRatesChart() {
    const data = await loadData('interest_rates.json');
    console.log('Interest rates:', Object.keys(data));

    const datasets = [];
    let colorIndex = 0;

    for (let key in data) {
        if (data[key].data && data[key].data.length > 0) {
            const last50 = data[key].data.slice(-50);
            datasets.push({
                label: data[key].label,
                data: last50.map(d => d.value),
                borderColor: COLOR_ARRAY[colorIndex % COLOR_ARRAY.length],
                backgroundColor: COLOR_ARRAY[colorIndex % COLOR_ARRAY.length] + '1a',
                borderWidth: 2,
                fill: false,
                pointRadius: 1,
                tension: 0.4,
                unit: data[key].unit
            });
            colorIndex++;
        }
    }

    if (datasets.length > 0) {
        charts.interestRates = createSimpleChart('interestRatesChart', datasets, {
            yAxisLabel: '% p.a.'
        });
    }
}

async function initExchangeRatesChart() {
    const data = await loadData('exchange_rates.json');
    console.log('Exchange rates:', Object.keys(data));

    const datasets = [];
    let colorIndex = 0;

    for (let key in data) {
        if (data[key].data && data[key].data.length > 0) {
            datasets.push({
                label: data[key].label,
                data: data[key].data.map(d => d.value),
                borderColor: COLOR_ARRAY[colorIndex % COLOR_ARRAY.length],
                backgroundColor: COLOR_ARRAY[colorIndex % COLOR_ARRAY.length] + '1a',
                borderWidth: 2,
                fill: false,
                pointRadius: 1,
                tension: 0.4,
                unit: data[key].unit
            });
            colorIndex++;
        }
    }

    if (datasets.length > 0) {
        charts.exchangeRates = createSimpleChart('exchangeRatesChart', datasets, {
            yAxisLabel: 'VND/USD'
        });
    }
}

async function initGoldPricesCharts() {
    const data = await loadData('gold_prices.json');

    // SJC Gold
    if (data.sjc_gold && data.sjc_gold.data && data.sjc_gold.data.length > 0) {
        const last50 = data.sjc_gold.data.slice(-50);
        charts.sjcGold = createSimpleChart('sjcGoldChart', [{
            label: data.sjc_gold.label,
            data: last50.map(d => d.value),
            borderColor: COLORS.yellow,
            backgroundColor: COLORS.yellow + '1a',
            borderWidth: 2,
            fill: false,
            tension: 0.4,
            unit: data.sjc_gold.unit
        }], { yAxisLabel: 'Million VND/tael' });
    }

    // World Gold
    if (data.world_gold && data.world_gold.data && data.world_gold.data.length > 0) {
        const last50 = data.world_gold.data.slice(-50);
        charts.worldGold = createSimpleChart('worldGoldChart', [{
            label: data.world_gold.label,
            data: last50.map(d => d.value),
            borderColor: COLORS.green,
            backgroundColor: COLORS.green + '1a',
            borderWidth: 2,
            fill: false,
            tension: 0.4,
            unit: data.world_gold.unit
        }], { yAxisLabel: 'USD/oz' });
    }
}

async function initFuelPricesCharts() {
    const data = await loadData('fuel_prices.json');

    // RON95
    if (data.ron95_iii && data.ron95_iii.data && data.ron95_iii.data.length > 0) {
        const last50 = data.ron95_iii.data.slice(-50);
        charts.ron95 = createSimpleChart('ron95Chart', [{
            label: data.ron95_iii.label,
            data: last50.map(d => d.value),
            borderColor: COLORS.red,
            backgroundColor: COLORS.red + '1a',
            borderWidth: 2,
            fill: false,
            tension: 0.4,
            unit: data.ron95_iii.unit
        }], { yAxisLabel: 'VND/liter' });
    }

    // Brent Crude
    if (data.brent_crude && data.brent_crude.data && data.brent_crude.data.length > 0) {
        const last200 = data.brent_crude.data.slice(-200);
        charts.brent = createSimpleChart('brentChart', [{
            label: data.brent_crude.label,
            data: last200.map(d => d.value),
            borderColor: COLORS.purple,
            backgroundColor: COLORS.purple + '1a',
            borderWidth: 2,
            fill: false,
            tension: 0.4,
            unit: data.brent_crude.unit
        }], { yAxisLabel: '$/barrel' });
    }
}

function updateTimestamp() {
    const now = new Date();
    const timeString = now.toLocaleString('vi-VN');
    document.getElementById('lastUpdate').textContent = timeString;
    document.getElementById('footerTime').textContent = timeString;
}

async function initAllCharts() {
    console.log('Initializing dashboard...');
    updateTimestamp();

    await initInterestRatesChart();
    await initExchangeRatesChart();
    await initGoldPricesCharts();
    await initFuelPricesCharts();

    console.log('Dashboard ready!');
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAllCharts);
} else {
    initAllCharts();
}
