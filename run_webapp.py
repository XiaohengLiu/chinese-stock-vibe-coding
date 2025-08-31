#!/usr/bin/env python3
"""
Simple script to run the stock analysis web application
"""

import os
import sys

def main():
    """Run the Flask web application."""
    
    print("🚀 启动中国股票财务数据分析网站...")
    print("=" * 50)
    
    # Check if we're in virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  建议在虚拟环境中运行:")
        print("   source stock_env/bin/activate")
        print("   python run_webapp.py")
        print()
    
    try:
        from app import app
        
        print("✅ 应用启动成功!")
        print("📱 网站地址: http://localhost:8080")
        print("📱 或访问: http://127.0.0.1:8080")
        print()
        print("💡 使用说明:")
        print("   1. 在浏览器中打开上述地址")
        print("   2. 输入6位股票代码 (例如: 600519)")
        print("   3. 点击'获取数据'按钮")
        print("   4. 查看年度和半年度财务数据表格")
        print()
        print("🛑 按 Ctrl+C 停止服务器")
        print("=" * 50)
        
        # Run the Flask app
        app.run(host='0.0.0.0', port=8080, debug=False)
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装所有依赖:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
