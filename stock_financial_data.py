#!/usr/bin/env python3
"""
Stock Financial Data Retrieval Script using AKShare

This script fetches the last 10 years of financial data for a given stock code,
including PE ratio, net revenue, net profit, and operating profit.

Usage:
    python stock_financial_data.py
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from tabulate import tabulate
import warnings
warnings.filterwarnings('ignore')


class StockFinancialAnalyzer:
    def __init__(self):
        self.years_back = 10
        
    def get_financial_statements(self, stock_code):
        try:
            # Convert stock code to the format required by AKShare (with market identifier)
            if stock_code.startswith('6'):
                symbol = f"SH{stock_code}"  # Shanghai Stock Exchange
            elif stock_code.startswith(('0', '3')):
                symbol = f"SZ{stock_code}"  # Shenzhen Stock Exchange
            else:
                symbol = f"SH{stock_code}"  # Default to Shanghai
            
            print(f"Fetching profit sheet data for {symbol}...")
            
            # Fetch profit statement data (利润表) using the working function
            profit_stmt = ak.stock_profit_sheet_by_report_em(symbol=symbol)
            
            if profit_stmt is None or profit_stmt.empty:
                print(f"No profit statement data found for stock {stock_code}")
                return pd.DataFrame()
                
            # Convert to DataFrame and clean data
            df = pd.DataFrame(profit_stmt)
            
            # Find date column (could be different names)
            date_columns = ['REPORT_DATE', 'report_date', 'REPORT_PERIOD', '报告期']
            date_col = None
            for col in date_columns:
                if col in df.columns:
                    date_col = col
                    break
            
            if date_col is None:
                print("Could not find date column in the data")
                return pd.DataFrame()

            # Ensure report_date is datetime
            df['report_date'] = pd.to_datetime(df[date_col])
            
            # Filter for last 10 years
            cutoff_date = datetime.now() - timedelta(days=365 * self.years_back)
            df = df[df['report_date'] >= cutoff_date]
            
            # Sort by date
            df = df.sort_values('report_date', ascending=False)
            
            return df
            
        except Exception as e:
            print(f"Error fetching financial statements for {stock_code}: {str(e)}")
            return pd.DataFrame()
    
    def get_comprehensive_financial_data(self, stock_code):
        """
        Get comprehensive financial data for the last 10 years.
        
        Args:
            stock_code (str): Stock code
            
        Returns:
            pd.DataFrame: Comprehensive financial data
        """
        print(f"Fetching financial data for stock: {stock_code}")
        
        # Get financial statements
        financial_data = self.get_financial_statements(stock_code)
        
        if financial_data.empty:
            print("No financial statement data available")
            return pd.DataFrame()
        
        # Select relevant columns with multiple possible names
        result_columns = ['report_date']
        
        # Map common column names to standardized names (based on AKShare East Money data)
        column_mapping = {
            # Revenue columns (东方财富利润表)
            'TOTAL_OPERATE_INCOME': 'net_revenue',
            '营业总收入': 'net_revenue',
            '营业收入': 'net_revenue',
            'total_operating_revenue': 'net_revenue',
            'operating_revenue': 'net_revenue',
            '总营收': 'net_revenue',
            
            # Net profit columns (东方财富利润表)
            'PARENT_NETPROFIT': 'net_profit',
            'NETPROFIT': 'net_profit',
            '净利润': 'net_profit',
            'net_profit': 'net_profit',
            '归属于母公司所有者的净利润': 'net_profit',
            '归母净利润': 'net_profit',
            
            # Operating profit columns (东方财富利润表)
            'OPERATE_PROFIT': 'operating_profit',
            '营业利润': 'operating_profit',
            'operating_profit': 'operating_profit',
            '经营利润': 'operating_profit'
        }
        
        # Find and rename columns
        found_columns = ['report_date']
        for old_name, new_name in column_mapping.items():
            if old_name in financial_data.columns:
                financial_data[new_name] = financial_data[old_name]
                if new_name not in found_columns:
                    found_columns.append(new_name)
        
        # Keep only found columns
        available_columns = [col for col in found_columns if col in financial_data.columns]
        if len(available_columns) > 1:  # More than just report_date
            result_df = financial_data[available_columns].copy()
        else:
            print("Could not find required financial columns")
            result_df = financial_data.copy()
        
        # Remove PE ratio column since it's not available
        if 'pe_ratio' in result_df.columns:
            result_df.drop('pe_ratio', axis=1, inplace=True)
        
        # Remove columns that have all NaN values
        result_df = result_df.dropna(axis=1, how='all')
        
        # Format numeric columns
        numeric_columns = ['net_revenue', 'net_profit', 'operating_profit']
        for col in numeric_columns:
            if col in result_df.columns:
                result_df[col] = pd.to_numeric(result_df[col], errors='coerce')
        
        # Remove rows where all financial metrics are NaN
        financial_cols = [col for col in numeric_columns if col in result_df.columns]
        if financial_cols:
            result_df = result_df.dropna(subset=financial_cols, how='all')
        
        # Sort by date (most recent first)
        result_df = result_df.sort_values('report_date', ascending=False)
        
        return result_df
    
    def format_financial_data(self, df):
        """
        Format the financial data for better display.
        
        Args:
            df (pd.DataFrame): Raw financial data
            
        Returns:
            pd.DataFrame: Formatted financial data
        """
        if df.empty:
            return df
        
        formatted_df = df.copy()
        
        # Format date
        formatted_df['report_date'] = formatted_df['report_date'].dt.strftime('%Y-%m-%d')
        
        # Format financial figures (convert to millions/billions if needed)
        financial_cols = ['net_revenue', 'net_profit', 'operating_profit']
        
        for col in financial_cols:
            if col in formatted_df.columns:
                # Convert to numeric and format
                formatted_df[col] = pd.to_numeric(formatted_df[col], errors='coerce')
                # Format large numbers
                formatted_df[col] = formatted_df[col].apply(
                    lambda x: f"{x/1e8:.2f}亿" if pd.notna(x) and abs(x) >= 1e8 
                    else f"{x/1e4:.2f}万" if pd.notna(x) and abs(x) >= 1e4
                    else f"{x:.2f}" if pd.notna(x) else "N/A"
                )
        
        # Format PE ratio
        if 'pe_ratio' in formatted_df.columns:
            formatted_df['pe_ratio'] = formatted_df['pe_ratio'].apply(
                lambda x: f"{x:.2f}" if pd.notna(x) else "N/A"
            )
        
        return formatted_df
    
    def separate_annual_and_halfyear_data(self, df):
        """
        Separate data into annual reports and half-year reports.
        
        Args:
            df (pd.DataFrame): Financial data
            
        Returns:
            tuple: (annual_data, halfyear_data)
        """
        if df.empty:
            return pd.DataFrame(), pd.DataFrame()
        
        # Add month column for filtering
        df_copy = df.copy()
        df_copy['month'] = df_copy['report_date'].dt.month
        
        # Annual reports (December 31st - month 12)
        annual_data = df_copy[df_copy['month'] == 12].copy()
        
        # Half-year reports (June 30th - month 6)
        halfyear_data = df_copy[df_copy['month'] == 6].copy()
        
        # Remove the temporary month column
        annual_data.drop('month', axis=1, inplace=True)
        halfyear_data.drop('month', axis=1, inplace=True)
        
        return annual_data, halfyear_data
    
    def calculate_yoy_growth(self, df):
        """
        Calculate Year-over-Year growth rates for financial metrics.
        
        Args:
            df (pd.DataFrame): Financial data sorted by date (newest first)
            
        Returns:
            pd.DataFrame: Data with YoY growth rate columns added
        """
        if df.empty or len(df) < 2:
            return df
        
        # Sort by date (oldest first) for calculation
        df_sorted = df.sort_values('report_date', ascending=True).copy()
        
        # Calculate YoY growth rates
        metrics = ['net_revenue', 'net_profit', 'operating_profit']
        
        for metric in metrics:
            if metric in df_sorted.columns:
                # Calculate YoY growth rate
                df_sorted[f'{metric}_yoy_growth'] = df_sorted[metric].pct_change() * 100
        
        # Sort back to newest first
        df_sorted = df_sorted.sort_values('report_date', ascending=False)
        
        return df_sorted
    
    def create_financial_table(self, df, table_title):
        """
        Create a formatted financial table with YoY growth rates.
        
        Args:
            df (pd.DataFrame): Financial data
            table_title (str): Title for the table
        """
        if df.empty:
            print(f"\n❌ {table_title}: 无数据")
            return
        
        print(f"\n📊 {table_title}")
        print("-" * 100)
        
        # Prepare table data
        table_data = []
        
        for _, row in df.iterrows():
            formatted_row = [
                row['report_date'].strftime('%Y-%m-%d'),
                self._format_large_number(row.get('net_revenue', 0)),
                self._format_large_number(row.get('net_profit', 0)),
                self._format_large_number(row.get('operating_profit', 0)),
                f"{row.get('net_revenue_yoy_growth', 0):+.1f}%" if pd.notna(row.get('net_revenue_yoy_growth')) else "N/A",
                f"{row.get('net_profit_yoy_growth', 0):+.1f}%" if pd.notna(row.get('net_profit_yoy_growth')) else "N/A",
                f"{row.get('operating_profit_yoy_growth', 0):+.1f}%" if pd.notna(row.get('operating_profit_yoy_growth')) else "N/A"
            ]
            table_data.append(formatted_row)
        
        headers = [
            '报告日期', 
            '营业收入', 
            '净利润', 
            '营业利润',
            '营业收入增长率',
            '净利润增长率', 
            '营业利润增长率'
        ]
        
        print(tabulate(table_data, headers=headers, tablefmt='grid', stralign='center'))
    
    def create_data_visualization(self, df, stock_code):
        """
        Create comprehensive table visualizations of the financial data.
        
        Args:
            df (pd.DataFrame): Financial data
            stock_code (str): Stock code
        """
        if df.empty:
            print("❌ No data to visualize")
            return
        
        print(f"\n{'='*80}")
        print(f"📊 {stock_code} 财务数据分析报告")
        print(f"{'='*80}")
        
        # Separate data into annual and half-year reports
        annual_data, halfyear_data = self.separate_annual_and_halfyear_data(df)
        
        # Calculate YoY growth rates for both datasets
        if not annual_data.empty:
            annual_data_with_growth = self.calculate_yoy_growth(annual_data)
            self.create_financial_table(annual_data_with_growth, "年度财务数据表 (Annual Financial Data)")
        
        if not halfyear_data.empty:
            halfyear_data_with_growth = self.calculate_yoy_growth(halfyear_data)
            self.create_financial_table(halfyear_data_with_growth, "半年度财务数据表 (Half-Year Financial Data)")
        
        # Add summary if both datasets have data
        if not annual_data.empty or not halfyear_data.empty:
            self._create_data_summary(annual_data, halfyear_data, stock_code)
    
    def _create_data_summary(self, annual_data, halfyear_data, stock_code):
        """Create a summary comparison between annual and half-year data."""
        print(f"\n📋 数据汇总 (Data Summary)")
        print("-" * 80)
        
        summary_data = []
        
        if not annual_data.empty:
            latest_annual = annual_data.iloc[0]
            summary_data.append([
                "最新年报",
                latest_annual['report_date'].strftime('%Y-%m-%d'),
                self._format_large_number(latest_annual.get('net_revenue', 0)),
                self._format_large_number(latest_annual.get('net_profit', 0)),
                self._format_large_number(latest_annual.get('operating_profit', 0)),
                f"年报数据覆盖: {len(annual_data)} 年"
            ])
        
        if not halfyear_data.empty:
            latest_halfyear = halfyear_data.iloc[0]
            summary_data.append([
                "最新半年报",
                latest_halfyear['report_date'].strftime('%Y-%m-%d'),
                self._format_large_number(latest_halfyear.get('net_revenue', 0)),
                self._format_large_number(latest_halfyear.get('net_profit', 0)),
                self._format_large_number(latest_halfyear.get('operating_profit', 0)),
                f"半年报数据覆盖: {len(halfyear_data)} 期"
            ])
        
        if summary_data:
            headers = ['报告类型', '最新日期', '营业收入', '净利润', '营业利润', '数据覆盖']
            print(tabulate(summary_data, headers=headers, tablefmt='grid', stralign='center'))
    
    def _format_large_number(self, value):
        """Format large numbers for better readability."""
        if pd.isna(value) or value == 0:
            return "0"
        
        abs_value = abs(value)
        if abs_value >= 1e8:  # 亿
            return f"{value/1e8:.1f}亿"
        elif abs_value >= 1e4:  # 万
            return f"{value/1e4:.1f}万"
        else:
            return f"{value:.2f}"



def main():
    """Main function to demonstrate usage."""
    analyzer = StockFinancialAnalyzer()
    
    # Example usage - you can change this stock code
    stock_code = input("请输入股票代码 (例如: 600519): ").strip()
    
    if not stock_code:
        stock_code = "600519"  # Default to Kweichow Moutai
        print(f"使用默认股票代码: {stock_code}")
    
    print(f"\n正在获取股票 {stock_code} 近10年财务数据...")
    
    # Get comprehensive financial data
    financial_data = analyzer.get_comprehensive_financial_data(stock_code)
    
    if not financial_data.empty:
        print(f"\n✅ 成功获取到 {len(financial_data)} 条财务数据记录")
        
        # Save raw data to CSV (after removing empty columns)
        output_file = f"stock_{stock_code}_financial_data.csv"
        financial_data.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 原始数据已保存到: {output_file}")
        
        # Create comprehensive table visualization
        analyzer.create_data_visualization(financial_data, stock_code)
        
        # Basic analysis
        if not financial_data.empty and len(financial_data) > 1:
            print(f"\n📊 基本分析:")
            
            # Revenue analysis
            if 'net_revenue' in financial_data.columns:
                revenue_data = pd.to_numeric(financial_data['net_revenue'], errors='coerce').dropna()
                if len(revenue_data) > 1:
                    latest_revenue = revenue_data.iloc[0]
                    earliest_revenue = revenue_data.iloc[-1]
                    if earliest_revenue != 0:
                        growth_rate = ((latest_revenue - earliest_revenue) / earliest_revenue) * 100
                        print(f"• 营业收入增长率: {growth_rate:.2f}%")
            
            # Profit analysis
            if 'net_profit' in financial_data.columns:
                profit_data = pd.to_numeric(financial_data['net_profit'], errors='coerce').dropna()
                if len(profit_data) > 1:
                    latest_profit = profit_data.iloc[0]
                    earliest_profit = profit_data.iloc[-1]
                    if earliest_profit != 0:
                        profit_growth = ((latest_profit - earliest_profit) / earliest_profit) * 100
                        print(f"• 净利润增长率: {profit_growth:.2f}%")
            
            # PE ratio analysis
            if 'pe_ratio' in financial_data.columns:
                pe_data = pd.to_numeric(financial_data['pe_ratio'], errors='coerce').dropna()
                if len(pe_data) > 0:
                    avg_pe = pe_data.mean()
                    print(f"• 平均市盈率: {avg_pe:.2f}")
    
    else:
        print(f"❌ 未能获取到股票 {stock_code} 的财务数据")
        print("请检查股票代码是否正确，或稍后重试")


if __name__ == "__main__":
    main()
