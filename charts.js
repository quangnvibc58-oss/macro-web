/**
 * Chart.js initialization and data loading
 */

// Chart colors
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

// Chart instances
let charts = {};

/**
 * Create a chart
 */
function createChart(canvasId, label, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element not found: ${canvasId}`);
        return null;
    }

    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            intersect: false,
            mode: 'index'
        },
        plugins: {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    usePointStyle: true,
                    padding: 15,
                    font: {
                        size: 12
                    }
                }
            },
            tooltip: {
                enabled: true,
                backgroundColor: 'rgba(0,0,0,0.8)',
                padding: 12,
                titleFont: {
                    size: 13
                },
                bodyFont: {
                    size: 12
                },
                borderColor: 'rgba(255,255,255,0.1)',
                borderWidth: 1,
                displayColors: true,
                callbacks: {
                    title: function(context) {
                        if (context.length > 0) {
                            return new Date(context[0].label).toLocaleDateString('vi-VN', {
                                year: 'numeric',
                                month: '2-digit',
                                day: '2-digit'
                            });
                        }
                        return '';
                    },
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += context.parsed.y.toFixed(2);
                        }
                        if (context.dataset.unit) {
                            label += ' ' + context.dataset.unit;
                        }
                        return label;
                    }
                }
            },
            zoom: {
                zoom: {
                    wheel: {
                        enabled: true,
                        speed: 0.1,
                        modifierKey: 'ctrl'
                    },
                    pinch: {
                        enabled: true
                    },
                    mode: 'xy'
                },
                pan: {
                    enabled: true,
                    mode: 'xy',
                    modifierKey: 'shift'
                }
            }
        },
        scales: {
            x: {
                type: 'time',
                time: {
                    unit: 'month',
                    displayFormats: {
                        month: 'MMM YYYY',
                        day: 'DD/MM/YYYY'
                    }
                },
                title: {
                    display: false
                },
                grid: {
                    color: 'rgba(0,0,0,0.05)'
                }
            },
            y: {
                title: {
                    display: true,
                    text: options.yAxisLabel || 'Value'
                },
                grid: {
                    color: 'rgba(0,0,0,0.05)'
                }
            }
        }
    };

    const finalOptions = deepMerge(defaultOptions, options);

    const chart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: finalOptions,
        plugins: [
            Chart.Zoom
        ]
    });

    return chart;
}

/**
 * Deep merge objects
 */
function deepMerge(target, source) {
    for (let key in source) {
        if (source.hasOwnProperty(key)) {
            if (typeof source[key] === 'object' && source[key] !== null && !Array.isArray(source[key])) {
                if (!(key in target)) {
                    target[key] = {};
                }
                deepMerge(target[key], source[key]);
            } else {
                target[key] = source[key];
            }
        }
    }
    return target;
}

/**
 * Load data from JSON files
 */
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

/**
 * Format dataset for Chart.js
 */
function formatDataset(series, color) {
    return {
        label: series.label,
        data: series.data.map(item => ({
            x: item.date,
            y: item.value
        })),
        borderColor: color,
        backgroundColor: color + '1a',  // 10% opacity
        borderWidth: 2,
        fill: false,
        pointRadius: 2,
        pointHoverRadius: 6,
        tension: 0.4,
        unit: series.unit
    };
}

/**
 * Initialize Interest Rates Chart
 */
async function initInterestRatesChart() {
    const data = await loadData('interest_rates.json');
    if (Object.keys(data).length === 0) {
        document.getElementById('interestRatesSection').innerHTML += '<p class="error">No interest rate data available</p>';
        return;
    }

    const datasets = [];
    let colorIndex = 0;

    for (let key in data) {
        if (data[key].data && data[key].data.length > 0) {
            datasets.push(formatDataset(data[key], COLOR_ARRAY[colorIndex % COLOR_ARRAY.length]));
            colorIndex++;
        }
    }

    const chartData = {
        datasets: datasets
    };

    charts['interestRates'] = createChart(
        'interestRatesChart',
        'Interest Rates',
        chartData,
        {
            yAxisLabel: 'Percentage (% p.a.)',
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y.toFixed(3) + '%';
                        }
                    }
                }
            }
        }
    );
}

/**
 * Initialize Exchange Rates Chart
 */
async function initExchangeRatesChart() {
    const data = await loadData('exchange_rates.json');
    if (Object.keys(data).length === 0) {
        document.getElementById('exchangeRatesSection').innerHTML += '<p class="error">No exchange rate data available</p>';
        return;
    }

    const datasets = [];
    let colorIndex = 0;

    for (let key in data) {
        if (data[key].data && data[key].data.length > 0) {
            datasets.push(formatDataset(data[key], COLOR_ARRAY[colorIndex % COLOR_ARRAY.length]));
            colorIndex++;
        }
    }

    const chartData = {
        datasets: datasets
    };

    charts['exchangeRates'] = createChart(
        'exchangeRatesChart',
        'Exchange Rates',
        chartData,
        {
            yAxisLabel: 'VND per USD'
        }
    );
}

/**
 * Initialize Gold Prices Charts
 */
async function initGoldPricesCharts() {
    const data = await loadData('gold_prices.json');
    if (Object.keys(data).length === 0) {
        document.getElementById('goldPricesSection').innerHTML += '<p class="error">No gold price data available</p>';
        return;
    }

    // SJC Gold
    if (data.sjc_gold && data.sjc_gold.data && data.sjc_gold.data.length > 0) {
        const sjcDataset = formatDataset(data.sjc_gold, COLORS.yellow);
        charts['sjcGold'] = createChart(
            'sjcGoldChart',
            'SJC Gold',
            { datasets: [sjcDataset] },
            {
                yAxisLabel: 'Million VND per tael'
            }
        );
    }

    // World Gold
    if (data.world_gold && data.world_gold.data && data.world_gold.data.length > 0) {
        const worldGoldDataset = formatDataset(data.world_gold, COLORS.green);
        charts['worldGold'] = createChart(
            'worldGoldChart',
            'World Gold Spot',
            { datasets: [worldGoldDataset] },
            {
                yAxisLabel: 'USD per oz'
            }
        );
    }
}

/**
 * Initialize Fuel Prices Charts
 */
async function initFuelPricesCharts() {
    const data = await loadData('fuel_prices.json');
    if (Object.keys(data).length === 0) {
        document.getElementById('fuelPricesSection').innerHTML += '<p class="error">No fuel price data available</p>';
        return;
    }

    // RON95-III
    if (data.ron95_iii && data.ron95_iii.data && data.ron95_iii.data.length > 0) {
        const ron95Dataset = formatDataset(data.ron95_iii, COLORS.red);
        charts['ron95'] = createChart(
            'ron95Chart',
            'RON95-III',
            { datasets: [ron95Dataset] },
            {
                yAxisLabel: 'VND per liter'
            }
        );
    }

    // Brent Crude
    if (data.brent_crude && data.brent_crude.data && data.brent_crude.data.length > 0) {
        const brentDataset = formatDataset(data.brent_crude, COLORS.purple);
        charts['brent'] = createChart(
            'brentChart',
            'Brent Crude Oil',
            { datasets: [brentDataset] },
            {
                yAxisLabel: 'USD per barrel'
            }
        );
    }
}

/**
 * Update last update timestamp
 */
function updateTimestamp() {
    const now = new Date();
    const timeString = now.toLocaleString('vi-VN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('lastUpdate').textContent = timeString;
    document.getElementById('footerTime').textContent = timeString;
}

/**
 * Initialize all charts
 */
async function initAllCharts() {
    console.log('Initializing charts...');

    updateTimestamp();

    await initInterestRatesChart();
    await initExchangeRatesChart();
    await initGoldPricesCharts();
    await initFuelPricesCharts();

    console.log('Charts initialized');
}

/**
 * Document ready
 */
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAllCharts);
} else {
    initAllCharts();
}

/**
 * Reset zoom on buttons
 */
window.resetZoom = function(chartName) {
    if (charts[chartName]) {
        charts[chartName].resetZoom();
    }
};
