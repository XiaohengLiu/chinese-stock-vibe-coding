# China Stock Financial Data Analyzer

This project provides a Python script to fetch and analyze financial data for Chinese stocks using the AKShare library.

## Features

- Fetches last 10 years of financial data for any Chinese stock
- Retrieves key financial metrics:
  - PE ratio (市盈率)
  - Net revenue (营业收入)
  - Net profit (净利润)
  - Operating profit (营业利润)
- **🆕 Beautiful table visualizations** with multiple views:
  - Recent financial data table
  - Year-over-year growth analysis
  - Summary statistics table
  - Quarterly vs annual comparison
- Provides data formatting and basic analysis
- Exports data to CSV format

## Installation

1. **Activate the virtual environment** (recommended):
```bash
source stock_env/bin/activate
```

2. **Install the required dependencies**:
```bash
pip install -r requirements.txt
```

*Note: If you don't have the virtual environment yet, create it first:*
```bash
python3 -m venv stock_env
source stock_env/bin/activate
pip install -r requirements.txt
```

## Usage

### Web Application (Recommended)

Start the web application:
```bash
python run_webapp.py
```

Then open your browser and visit: http://localhost:8080

### Command Line Usage

For direct command-line access:
```bash
python stock_financial_data.py
```

The script will prompt you to enter a stock code (e.g., 600519 for Kweichow Moutai).

### Programmatic Usage

You can also use the `StockFinancialAnalyzer` class in your own code:

```python
from stock_financial_data import StockFinancialAnalyzer

# Create analyzer instance
analyzer = StockFinancialAnalyzer()

# Get financial data for a stock
stock_code = "600519"  # Kweichow Moutai
financial_data = analyzer.get_comprehensive_financial_data(stock_code)

# Display the data using web-style visualization
analyzer.create_data_visualization(financial_data, stock_code)
```

## Stock Code Examples

- 600519 - 贵州茅台 (Kweichow Moutai)
- 000001 - 平安银行 (Ping An Bank)
- 000002 - 万科A (China Vanke)
- 600036 - 招商银行 (China Merchants Bank)
- 000858 - 五粮液 (Wuliangye)

## Data Sources

The script uses the AKShare library which aggregates data from multiple sources:
- Sina Finance
- East Money
- Baidu Finance
- And other financial data providers

## Output

The script provides:
1. **🆕 Beautiful table visualizations**:
   - Recent financial data in grid format
   - Year-over-year growth rate analysis
   - Summary statistics (min, max, average, variance)
   - Quarterly vs annual data comparison
2. **CSV export**: Raw data saved to `stock_{code}_financial_data.csv`
3. **Basic analysis**: Growth rates and trend analysis

### Sample Output:
```
📊 600519 财务数据可视化表格
================================================================================

📈 近期财务数据 (最近10期)
--------------------------------------------------------------------------------
+------------+---------+--------+---------+-------+
|    报告日期    |  营业收入   |  净利润   |  营业利润   |  市盈率  |
+============+=========+========+=========+=======+
| 2025-06-30 | 910.9亿  | 469.9亿 | 627.7亿  |  N/A  |
+------------+---------+--------+---------+-------+
| 2025-03-31 | 514.4亿  | 277.7亿 | 370.4亿  |  N/A  |
+------------+---------+--------+---------+-------+
...
```

## Error Handling

The script includes comprehensive error handling for:
- Invalid stock codes
- Network connectivity issues
- Missing data scenarios
- Data format inconsistencies

## Notes

- Data availability may vary depending on the stock and data source
- Some older stocks may have limited historical data
- PE ratio data might not be available for all reporting periods
- Financial figures are automatically formatted (万 for ten thousands, 亿 for hundreds of millions)

## Requirements

- Python 3.7+
- Internet connection for data fetching
- Valid Chinese stock codes (6-digit format)
