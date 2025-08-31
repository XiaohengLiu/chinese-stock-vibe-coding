// Stock Analysis Web App JavaScript

// DOM Elements
const stockCodeInput = document.getElementById('stockCode');
const analyzeBtn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const results = document.getElementById('results');
const summaryTable = document.getElementById('summaryTable');
const annualTable = document.getElementById('annualTable');
const halfyearTable = document.getElementById('halfyearTable');

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    stockCodeInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            analyzeStock();
        }
    });
    
    // Only allow numbers in stock code input
    stockCodeInput.addEventListener('input', function(e) {
        e.target.value = e.target.value.replace(/[^0-9]/g, '');
    });
    
    // Load pre-fetched data on page load
    loadPrefetchedData();
});

// Set stock code from examples
function setStockCode(code) {
    stockCodeInput.value = code;
    stockCodeInput.focus();
}

// Load pre-fetched data
async function loadPrefetchedData() {
    try {
        const response = await fetch('/prefetched');
        const prefetchedData = await response.json();
        
        if (Object.keys(prefetchedData).length > 0) {
            // Find a stock with data to display
            const stockCode = Object.keys(prefetchedData)[0];
            const data = prefetchedData[stockCode];
            
            // Set the stock code in the input
            stockCodeInput.value = stockCode;
            
            // Display the pre-fetched data
            displayResults(data);
            
            // Add a note about pre-loaded data
            const noteElement = document.createElement('div');
            noteElement.className = 'prefetch-note';
            noteElement.innerHTML = `
                <i class="fas fa-info-circle"></i> 
                已为您预加载 ${stockCode} 的数据，您也可以输入其他股票代码查询
            `;
            
            // Insert note before results
            results.parentNode.insertBefore(noteElement, results);
        }
    } catch (error) {
        console.log('Pre-fetched data not available:', error);
        // Silently fail - this is not critical
    }
}

// Main analysis function
async function analyzeStock() {
    const stockCode = stockCodeInput.value.trim();
    
    if (!stockCode) {
        showError('请输入股票代码');
        return;
    }
    
    if (stockCode.length !== 6) {
        showError('股票代码必须是6位数字');
        return;
    }
    
    // Show loading state
    showLoading();
    hideError();
    hideResults();
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ stock_code: stockCode })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || '请求失败');
        }
        
        // Display results
        displayResults(data);
        
    } catch (err) {
        console.error('Error:', err);
        showError(err.message || '获取数据失败，请稍后重试');
    } finally {
        hideLoading();
    }
}

// Display functions
function showLoading() {
    loading.classList.remove('hidden');
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 获取中...';
}

function hideLoading() {
    loading.classList.add('hidden');
    analyzeBtn.disabled = false;
    analyzeBtn.innerHTML = '<i class="fas fa-search"></i> 获取数据';
}

function showError(message) {
    error.textContent = message;
    error.classList.remove('hidden');
}

function hideError() {
    error.classList.add('hidden');
}

function hideResults() {
    results.classList.add('hidden');
}

function displayResults(data) {
    // Display summary
    displaySummary(data.summary);
    
    // Display annual table
    displayDataTable(data.annual_data, annualTable, '年度');
    
    // Display halfyear table
    displayDataTable(data.halfyear_data, halfyearTable, '半年度');
    
    // Show results
    results.classList.remove('hidden');
    
    // Smooth scroll to results
    results.scrollIntoView({ behavior: 'smooth' });
}

function displaySummary(summaryData) {
    if (!summaryData || summaryData.length === 0) {
        summaryTable.innerHTML = '<div class="no-data">无汇总数据</div>';
        return;
    }
    
    const summaryHtml = summaryData.map(item => `
        <div class="summary-item">
            <h3>${item.type}</h3>
            <div class="summary-details">
                <span><strong>日期:</strong> ${item.date}</span>
                <span><strong>营业收入:</strong> ${item.net_revenue}</span>
                <span><strong>净利润:</strong> ${item.net_profit}</span>
                <span><strong>营业利润:</strong> ${item.operating_profit}</span>
                <span><strong>覆盖:</strong> ${item.coverage}</span>
            </div>
        </div>
    `).join('');
    
    summaryTable.innerHTML = summaryHtml;
}

function displayDataTable(tableData, container, tableType) {
    if (!tableData || !tableData.rows || tableData.rows.length === 0) {
        container.innerHTML = `<div class="no-data">无${tableType}数据</div>`;
        return;
    }
    
    // Create table HTML
    const table = document.createElement('table');
    table.className = 'data-table';
    
    // Create header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    tableData.headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header.label;
        headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create body
    const tbody = document.createElement('tbody');
    
    tableData.rows.forEach(row => {
        const tr = document.createElement('tr');
        
        tableData.headers.forEach(header => {
            const td = document.createElement('td');
            const value = row[header.key];
            
            // Apply styling for growth rates
            if (header.key.includes('growth')) {
                td.className = getGrowthClass(value);
            }
            
            td.textContent = value;
            tr.appendChild(td);
        });
        
        tbody.appendChild(tr);
    });
    
    table.appendChild(tbody);
    container.innerHTML = '';
    container.appendChild(table);
}

function getGrowthClass(value) {
    if (value === 'N/A') {
        return 'growth-neutral';
    }
    
    const numericValue = parseFloat(value.replace('%', '').replace('+', ''));
    
    if (numericValue > 0) {
        return 'growth-positive';
    } else if (numericValue < 0) {
        return 'growth-negative';
    } else {
        return 'growth-neutral';
    }
}

// Utility functions
function formatNumber(num) {
    if (typeof num !== 'number') return num;
    
    if (num >= 1e8) {
        return (num / 1e8).toFixed(1) + '亿';
    } else if (num >= 1e4) {
        return (num / 1e4).toFixed(1) + '万';
    } else {
        return num.toFixed(2);
    }
}

function formatGrowthRate(rate) {
    if (rate === null || rate === undefined || isNaN(rate)) {
        return 'N/A';
    }
    return (rate >= 0 ? '+' : '') + rate.toFixed(1) + '%';
}

// Add some visual feedback
document.addEventListener('DOMContentLoaded', function() {
    // Add ripple effect to buttons
    analyzeBtn.addEventListener('click', function(e) {
        const ripple = document.createElement('div');
        ripple.className = 'ripple';
        this.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    });
});

// CSS for ripple effect (injected via JavaScript)
const style = document.createElement('style');
style.textContent = `
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    button {
        position: relative;
        overflow: hidden;
    }
`;
document.head.appendChild(style);
