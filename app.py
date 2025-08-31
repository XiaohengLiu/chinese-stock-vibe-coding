#!/usr/bin/env python3
"""
Flask Web Application for Stock Financial Data Analysis
"""

from flask import Flask, render_template, request, jsonify, flash
import pandas as pd
import json
from stock_financial_data import StockFinancialAnalyzer
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'chinese-stock-analysis-secret-key-2024'  # Production secret

class WebStockAnalyzer:
    """Web wrapper for the stock financial analyzer."""
    
    def __init__(self):
        self.analyzer = StockFinancialAnalyzer()
    
    def get_stock_data(self, stock_code):
        """
        Get stock data formatted for web display.
        
        Args:
            stock_code (str): Stock code
            
        Returns:
            dict: Formatted data for web display
        """
        try:
            # Get financial data
            financial_data = self.analyzer.get_comprehensive_financial_data(stock_code)
            
            if financial_data.empty:
                return {"error": f"未能获取到股票 {stock_code} 的数据，请检查股票代码是否正确"}
            
            # Separate annual and half-year data
            annual_data, halfyear_data = self.analyzer.separate_annual_and_halfyear_data(financial_data)
            
            # Calculate YoY growth rates
            annual_with_growth = self.analyzer.calculate_yoy_growth(annual_data) if not annual_data.empty else pd.DataFrame()
            halfyear_with_growth = self.analyzer.calculate_yoy_growth(halfyear_data) if not halfyear_data.empty else pd.DataFrame()
            
            # Format data for web display
            result = {
                "stock_code": stock_code,
                "annual_data": self._format_data_for_web(annual_with_growth, "annual"),
                "halfyear_data": self._format_data_for_web(halfyear_with_growth, "halfyear"),
                "summary": self._create_summary(annual_data, halfyear_data)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting stock data for {stock_code}: {str(e)}")
            logger.error(traceback.format_exc())
            return {"error": f"获取数据时发生错误: {str(e)}"}
    
    def _format_data_for_web(self, df, data_type):
        """Format dataframe for web table display."""
        if df.empty:
            return {"headers": [], "rows": [], "message": f"无{data_type}数据"}
        
        # Define headers
        headers = [
            {"key": "report_date", "label": "报告日期"},
            {"key": "net_revenue", "label": "营业收入"},
            {"key": "net_profit", "label": "净利润"},
            {"key": "operating_profit", "label": "营业利润"},
            {"key": "net_revenue_growth", "label": "营业收入增长率"},
            {"key": "net_profit_growth", "label": "净利润增长率"},
            {"key": "operating_profit_growth", "label": "营业利润增长率"}
        ]
        
        # Format rows
        rows = []
        for _, row in df.iterrows():
            formatted_row = {
                "report_date": row['report_date'].strftime('%Y-%m-%d'),
                "net_revenue": self._format_large_number(row.get('net_revenue', 0)),
                "net_profit": self._format_large_number(row.get('net_profit', 0)),
                "operating_profit": self._format_large_number(row.get('operating_profit', 0)),
                "net_revenue_growth": self._format_growth_rate(row.get('net_revenue_yoy_growth')),
                "net_profit_growth": self._format_growth_rate(row.get('net_profit_yoy_growth')),
                "operating_profit_growth": self._format_growth_rate(row.get('operating_profit_yoy_growth'))
            }
            rows.append(formatted_row)
        
        return {"headers": headers, "rows": rows}
    
    def _format_large_number(self, value):
        """Format large numbers for display."""
        if pd.isna(value) or value == 0:
            return "0"
        
        abs_value = abs(value)
        if abs_value >= 1e8:  # 亿
            return f"{value/1e8:.1f}亿"
        elif abs_value >= 1e4:  # 万
            return f"{value/1e4:.1f}万"
        else:
            return f"{value:.2f}"
    
    def _format_growth_rate(self, value):
        """Format growth rate for display."""
        if pd.isna(value):
            return "N/A"
        return f"{value:+.1f}%"
    
    def _create_summary(self, annual_data, halfyear_data):
        """Create summary information."""
        summary = []
        
        if not annual_data.empty:
            latest_annual = annual_data.iloc[0]
            summary.append({
                "type": "最新年报",
                "date": latest_annual['report_date'].strftime('%Y-%m-%d'),
                "net_revenue": self._format_large_number(latest_annual.get('net_revenue', 0)),
                "net_profit": self._format_large_number(latest_annual.get('net_profit', 0)),
                "operating_profit": self._format_large_number(latest_annual.get('operating_profit', 0)),
                "coverage": f"{len(annual_data)} 年"
            })
        
        if not halfyear_data.empty:
            latest_halfyear = halfyear_data.iloc[0]
            summary.append({
                "type": "最新半年报",
                "date": latest_halfyear['report_date'].strftime('%Y-%m-%d'),
                "net_revenue": self._format_large_number(latest_halfyear.get('net_revenue', 0)),
                "net_profit": self._format_large_number(latest_halfyear.get('net_profit', 0)),
                "operating_profit": self._format_large_number(latest_halfyear.get('operating_profit', 0)),
                "coverage": f"{len(halfyear_data)} 期"
            })
        
        return summary

# Initialize the analyzer
web_analyzer = WebStockAnalyzer()

@app.route('/')
def index():
    """Main page with stock input form."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_stock():
    """Analyze stock data and return results."""
    try:
        data = request.get_json()
        stock_code = data.get('stock_code', '').strip()
        
        if not stock_code:
            return jsonify({"error": "请输入股票代码"}), 400
        
        # Get stock data
        result = web_analyzer.get_stock_data(stock_code)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in analyze_stock: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "服务器内部错误"}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # Production configuration
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
