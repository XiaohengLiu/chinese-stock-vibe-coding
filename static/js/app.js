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

// Navigation Elements
const navTabs = document.querySelectorAll('.nav-tab');
const tabPanels = document.querySelectorAll('.tab-panel');

// News Elements
const newsContent = document.getElementById('newsContent');
const newsLoading = document.getElementById('newsLoading');
const newsError = document.getElementById('newsError');

// Starred Elements
const starredContent = document.getElementById('starredContent');
const starredCount = document.getElementById('starredCount');

// User ID for database operations (in a real app, this would come from authentication)
const USER_ID = 'default_user';

// In-memory cache for starred stocks (synced with database)
let starredStocks = [];

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
    
    // Initialize navigation
    initNavigation();
    
    // Initialize starred stocks from database first, then load pre-fetched data
    initializeAppData();
});

// Initialize app data in correct order
async function initializeAppData() {
    // Load starred stocks first
    await loadStarredStocks();
    
    // Then load and display pre-fetched data
    await loadPrefetchedData();
}

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
    // Add star button to summary section
    addStarButton(data.stock_code);
    
    // Display summary
    displaySummary(data.summary);
    
    // Display annual table
    displayDataTable(data.annual_data, annualTable, '年度');
    
    // Display halfyear table
    displayDataTable(data.halfyear_data, halfyearTable, '半年度');
    
    // Show results
    results.classList.remove('hidden');
    
    // Update highlighting to show current stock
    highlightStarredStocksInGrid();
    
    // Smooth scroll to results
    results.scrollIntoView({ behavior: 'smooth' });
}

function addStarButton(stockCode) {
    // Remove existing star button
    const existingBtn = document.querySelector('.star-btn');
    if (existingBtn) {
        existingBtn.remove();
    }
    
    // Create star button
    const starBtn = document.createElement('button');
    starBtn.id = 'starButton';
    starBtn.dataset.stockCode = stockCode;
    starBtn.className = `star-btn ${isStarred(stockCode) ? 'starred' : ''}`;
    starBtn.innerHTML = `
        <i class="fas fa-star"></i> 
        ${isStarred(stockCode) ? '已关注' : '关注'}
    `;
    starBtn.onclick = async () => {
        // Show loading state
        starBtn.disabled = true;
        starBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 处理中...';
        
        // Toggle star in database
        await toggleStar(stockCode, getStockName(stockCode));
        
        // Re-enable button and update state
        starBtn.disabled = false;
        updateStarButton(stockCode);
    };
    
    // Add to summary section
    const summarySection = document.querySelector('.summary-section h2');
    if (summarySection) {
        summarySection.appendChild(starBtn);
    }
}

function updateStarButton(stockCode) {
    const starBtn = document.getElementById('starButton');
    if (starBtn) {
        const starred = isStarred(stockCode);
        starBtn.className = `star-btn ${starred ? 'starred' : ''}`;
        starBtn.innerHTML = `
            <i class="fas fa-star"></i> 
            ${starred ? '已关注' : '关注'}
        `;
    }
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

// Navigation Functions
function initNavigation() {
    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.getAttribute('data-tab');
            switchTab(targetTab);
        });
    });
}

function switchTab(targetTab) {
    // Update active tab
    navTabs.forEach(tab => {
        tab.classList.remove('active');
        if (tab.getAttribute('data-tab') === targetTab) {
            tab.classList.add('active');
        }
    });
    
    // Update active panel
    tabPanels.forEach(panel => {
        panel.classList.remove('active');
        if (panel.id === targetTab + 'Panel') {
            panel.classList.add('active');
        }
    });
    
    // Load content for specific tabs
    if (targetTab === 'news') {
        loadNews();
    } else if (targetTab === 'starred') {
        renderStarredStocks();
    }
}

// News Functions
async function loadNews() {
    if (newsContent.querySelector('.news-item')) {
        return; // News already loaded
    }
    
    showNewsLoading();
    try {
        // Mock news data - in production, you'd fetch from a real news API
        const mockNews = [
            {
                title: "A股三大指数收盘涨跌不一，创业板指涨0.8%",
                summary: "今日A股市场整体表现平稳，沪深两市成交量较昨日有所放大。科技股和新能源板块领涨...",
                time: "2小时前",
                source: "财经新闻"
            },
            {
                title: "央行发布金融稳定报告，强调防范系统性风险",
                summary: "中国人民银行今日发布《中国金融稳定报告（2024）》，重点关注房地产、地方政府债务等领域风险...",
                time: "4小时前",
                source: "央行官网"
            },
            {
                title: "科创板公司三季报披露完毕，整体业绩向好",
                summary: "截至目前，科创板所有上市公司均已完成三季报披露。数据显示，整体营收和净利润同比均实现增长...",
                time: "6小时前",
                source: "上交所"
            },
            {
                title: "外资持续加仓A股，看好中国经济长期前景",
                summary: "最新数据显示，境外资金通过沪深股通渠道持续流入A股市场，单日净买入额创近期新高...",
                time: "8小时前",
                source: "证券时报"
            },
            {
                title: "新能源汽车产业链投资机会凸显",
                summary: "随着政策支持力度加大和技术不断进步，新能源汽车产业链上下游企业迎来新的发展机遇...",
                time: "昨天",
                source: "投资快报"
            }
        ];
        
        displayNews(mockNews);
        hideNewsLoading();
    } catch (error) {
        console.error('Error loading news:', error);
        showNewsError('获取新闻失败，请稍后重试');
        hideNewsLoading();
    }
}

function displayNews(newsData) {
    const newsHtml = newsData.map(item => `
        <div class="news-item">
            <div class="news-title">${item.title}</div>
            <div class="news-meta">
                <span>${item.source}</span>
                <span>${item.time}</span>
            </div>
            <div class="news-summary">${item.summary}</div>
        </div>
    `).join('');
    
    newsContent.innerHTML = newsHtml;
}

function refreshNews() {
    newsContent.innerHTML = '<div class="news-placeholder"><i class="fas fa-newspaper"></i><p>点击刷新获取最新财经新闻</p></div>';
    loadNews();
}

function showNewsLoading() {
    newsLoading.classList.remove('hidden');
    newsError.classList.add('hidden');
}

function hideNewsLoading() {
    newsLoading.classList.add('hidden');
}

function showNewsError(message) {
    newsError.textContent = message;
    newsError.classList.remove('hidden');
}

// Database API Functions
async function loadStarredStocks() {
    try {
        const response = await fetch(`/starred?user_id=${USER_ID}`);
        const data = await response.json();
        
        if (response.ok) {
            starredStocks = data.starred_stocks || [];
            updateStarredCount();
            renderStarredStocks();
            highlightStarredStocksInGrid();
        } else {
            console.error('Error loading starred stocks:', data.error);
        }
    } catch (error) {
        console.error('Error loading starred stocks:', error);
        // Fallback to localStorage for offline mode
        starredStocks = JSON.parse(localStorage.getItem('starredStocks') || '[]');
        updateStarredCount();
        renderStarredStocks();
        highlightStarredStocksInGrid();
    }
}

async function addStarredStock(stockCode, stockName) {
    try {
        const response = await fetch('/starred', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                stock_code: stockCode,
                stock_name: stockName || getStockName(stockCode),
                user_id: USER_ID
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Reload starred stocks from server
            await loadStarredStocks();
            return true;
        } else {
            console.error('Error adding starred stock:', data.error);
            return false;
        }
    } catch (error) {
        console.error('Error adding starred stock:', error);
        return false;
    }
}

async function removeStarredStock(stockCode) {
    try {
        const response = await fetch(`/starred/${stockCode}?user_id=${USER_ID}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Reload starred stocks from server
            await loadStarredStocks();
            return true;
        } else {
            console.error('Error removing starred stock:', data.error);
            return false;
        }
    } catch (error) {
        console.error('Error removing starred stock:', error);
        return false;
    }
}

async function clearAllStarredStocks() {
    try {
        const response = await fetch('/starred/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: USER_ID
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Reload starred stocks from server
            await loadStarredStocks();
            return true;
        } else {
            console.error('Error clearing starred stocks:', data.error);
            return false;
        }
    } catch (error) {
        console.error('Error clearing starred stocks:', error);
        return false;
    }
}

// Starred Stocks Functions
async function toggleStar(stockCode, stockName) {
    const isCurrentlyStarred = isStarred(stockCode);
    
    try {
        if (isCurrentlyStarred) {
            // Remove from starred
            const success = await removeStarredStock(stockCode);
            if (success) {
                console.log(`Successfully removed ${stockCode} from starred list`);
            }
        } else {
            // Add to starred
            const success = await addStarredStock(stockCode, stockName);
            if (success) {
                console.log(`Successfully added ${stockCode} to starred list`);
            }
        }
    } catch (error) {
        console.error('Error toggling star:', error);
    }
    
    // Update UI - this will happen after the database is updated
    updateStarButtons();
}

function isStarred(stockCode) {
    return starredStocks.some(stock => stock.code === stockCode);
}

function updateStarredCount() {
    starredCount.textContent = starredStocks.length;
}

function renderStarredStocks() {
    if (starredStocks.length === 0) {
        starredContent.innerHTML = `
            <div class="starred-placeholder">
                <i class="fas fa-star-o"></i>
                <p>暂无关注的股票</p>
                <p class="hint">在搜索结果中点击星标按钮来关注股票</p>
            </div>
        `;
        return;
    }
    
    const starredHtml = starredStocks.map(stock => `
        <div class="starred-stock">
            <div class="stock-info">
                <div class="stock-code">${stock.code}</div>
                <div class="stock-name">${stock.name}</div>
            </div>
            <div class="stock-actions">
                <button class="action-btn" onclick="analyzeStarredStock('${stock.code}')">
                    <i class="fas fa-chart-line"></i> 分析
                </button>
                <button class="action-btn unstar-btn" onclick="toggleStar('${stock.code}')">
                    <i class="fas fa-trash"></i> 移除
                </button>
            </div>
        </div>
    `).join('');
    
    starredContent.innerHTML = starredHtml;
}

function analyzeStarredStock(stockCode) {
    // Switch to search tab and analyze the stock
    switchTab('search');
    stockCodeInput.value = stockCode;
    analyzeStock();
}

async function clearAllStarred() {
    if (confirm('确定要清空所有关注的股票吗？')) {
        await clearAllStarredStocks();
    }
}

function getStockName(stockCode) {
    // Simple stock name mapping - in production, you'd fetch from API
    const stockNames = {
        '600519': '贵州茅台',
        '000858': '五粮液',
        '600036': '招商银行',
        '000001': '平安银行',
        '000951': '中国重汽',
        '000739': '普洛药业',
        '300750': '宁德时代',
        '002594': '比亚迪'
    };
    return stockNames[stockCode] || '未知股票';
}

function updateStarButtons() {
    // Update star button in search results if visible
    const starBtn = document.getElementById('starButton');
    if (starBtn && starBtn.dataset.stockCode) {
        updateStarButton(starBtn.dataset.stockCode);
    }
    
    // Update highlighting in stock grid
    highlightStarredStocksInGrid();
}

function highlightStarredStocksInGrid() {
    // Get all example stock code elements
    const stockElements = document.querySelectorAll('.example-code');
    const currentStockCode = stockCodeInput.value.trim();
    
    stockElements.forEach(element => {
        // Extract stock code from onclick attribute
        const onclickAttr = element.getAttribute('onclick');
        if (onclickAttr) {
            const match = onclickAttr.match(/setStockCode\('(\d+)'\)/);
            if (match) {
                const stockCode = match[1];
                
                // Remove existing classes first
                element.classList.remove('starred-stock-example', 'current-stock-example');
                
                // Remove existing icons
                const existingIcon = element.querySelector('.star-icon, .current-icon');
                if (existingIcon) {
                    existingIcon.remove();
                    // Remove the space before the icon
                    if (element.firstChild && element.firstChild.nodeType === Node.TEXT_NODE && element.firstChild.textContent === ' ') {
                        element.firstChild.remove();
                    }
                }
                
                // Check if this is the current stock being viewed
                if (stockCode === currentStockCode && results && !results.classList.contains('hidden')) {
                    element.classList.add('current-stock-example');
                    const currentIcon = document.createElement('i');
                    currentIcon.className = 'fas fa-eye current-icon';
                    element.prepend(currentIcon);
                    element.prepend(document.createTextNode(' '));
                }
                // Check if this stock is starred
                else if (isStarred(stockCode)) {
                    element.classList.add('starred-stock-example');
                    const starIcon = document.createElement('i');
                    starIcon.className = 'fas fa-star star-icon';
                    element.prepend(starIcon);
                    element.prepend(document.createTextNode(' '));
                }
            }
        }
    });
}

// Call highlight function when stock code input changes
function updateHighlighting() {
    highlightStarredStocksInGrid();
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
