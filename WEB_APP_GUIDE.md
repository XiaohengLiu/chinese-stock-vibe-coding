# 🌐 中国股票财务数据分析网站

## 📋 项目概述

这是一个基于Flask的Web应用，提供用户友好的界面来分析中国股票的财务数据。用户可以通过输入股票代码，获取近10年的年度和半年度财务报告，包括营业收入、净利润、营业利润及其年同比增长率。

## 🚀 快速开始

### 1. 启动网站

```bash
# 确保在虚拟环境中
source stock_env/bin/activate

# 方法1: 使用便捷脚本
python run_webapp.py

# 方法2: 直接运行Flask应用
python app.py
```

### 2. 访问网站

打开浏览器，访问: http://localhost:5000

## 📱 功能特性

### ✨ 用户界面特性
- **现代化设计**: 渐变背景、卡片式布局、响应式设计
- **直观操作**: 单一输入框 + 一键获取数据
- **实时反馈**: 加载动画、错误提示、成功状态
- **移动友好**: 完全响应式，支持手机和平板访问

### 📊 数据展示特性
- **双表格展示**: 年度财务数据表 + 半年度财务数据表
- **完整指标**: 报告日期、营业收入、净利润、营业利润
- **增长率分析**: 自动计算年同比增长率，彩色标识正负增长
- **数据汇总**: 最新报告摘要和数据覆盖范围
- **智能格式化**: 大数字自动格式化为亿/万单位

### 🎨 视觉设计特性
- **颜色编码**: 
  - 正增长 = 绿色
  - 负增长 = 红色
  - 无数据 = 灰色
- **表格美化**: 
  - 斑马纹行
  - 悬停效果
  - 粘性表头
  - 阴影边框

## 🏗️ 技术架构

### 后端 (Flask)
```
app.py                 # 主应用文件
├── WebStockAnalyzer   # Web数据分析器类
├── /analyze           # API端点 - 分析股票数据
├── /health           # 健康检查端点
└── /                 # 主页路由
```

### 前端 (HTML/CSS/JS)
```
templates/
└── index.html        # 主页模板

static/
├── css/
│   └── style.css     # 样式文件
└── js/
    └── app.js        # 前端逻辑
```

### 数据流程
1. **用户输入** → 股票代码验证
2. **前端请求** → POST /analyze API
3. **后端处理** → 调用股票分析器
4. **数据处理** → 分离年度/半年度数据
5. **增长计算** → YoY增长率计算
6. **格式化** → Web友好的数据格式
7. **前端展示** → 动态生成表格

## 📁 文件结构

```
China_Stock/
├── app.py                    # Flask主应用
├── run_webapp.py            # 启动脚本
├── stock_financial_data.py  # 核心数据分析模块
├── requirements.txt         # 依赖列表
├── templates/
│   └── index.html          # 网页模板
├── static/
│   ├── css/
│   │   └── style.css       # 样式文件
│   └── js/
│       └── app.js          # 前端JavaScript
└── stock_env/              # 虚拟环境
```

## 🔧 API接口文档

### POST /analyze
分析指定股票的财务数据

**请求体:**
```json
{
  "stock_code": "600519"
}
```

**成功响应:**
```json
{
  "stock_code": "600519",
  "annual_data": {
    "headers": [...],
    "rows": [...]
  },
  "halfyear_data": {
    "headers": [...],
    "rows": [...]
  },
  "summary": [...]
}
```

**错误响应:**
```json
{
  "error": "错误信息"
}
```

### GET /health
健康检查接口

**响应:**
```json
{
  "status": "healthy"
}
```

## 🎯 支持的股票代码

输入6位数字股票代码，系统会自动识别交易所:
- **6开头**: 上海证券交易所 (SH)
- **0或3开头**: 深圳证券交易所 (SZ)

**示例股票:**
- `600519` - 贵州茅台
- `000858` - 五粮液  
- `600036` - 招商银行
- `000001` - 平安银行

## 🚀 部署说明

### 开发环境
```bash
python run_webapp.py
# 访问: http://localhost:5000
```

### 生产环境 (使用Gunicorn)
```bash
# 启动服务器
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 后台运行
nohup gunicorn -w 4 -b 0.0.0.0:5000 app:app > app.log 2>&1 &
```

### Docker部署 (可选)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 🔍 故障排除

### 常见问题

1. **模块导入错误**
   ```bash
   # 确保虚拟环境已激活
   source stock_env/bin/activate
   pip install -r requirements.txt
   ```

2. **股票数据获取失败**
   - 检查网络连接
   - 验证股票代码格式 (6位数字)
   - 稍后重试 (可能是数据源临时不可用)

3. **页面无法访问**
   - 确认服务器已启动
   - 检查端口5000是否被占用
   - 尝试访问 http://127.0.0.1:5000

### 日志查看
```bash
# 查看Flask应用日志
python app.py  # 开发模式会显示详细日志

# 查看Gunicorn日志
tail -f app.log
```

## 🔒 安全注意事项

1. **生产环境配置**:
   - 修改 `app.secret_key`
   - 设置 `debug=False`
   - 使用反向代理 (Nginx)
   - 配置HTTPS

2. **输入验证**:
   - 股票代码格式验证
   - 请求频率限制
   - 输入长度限制

## 📈 性能优化

1. **缓存机制**: 可以添加Redis缓存常用股票数据
2. **异步处理**: 使用Celery处理耗时的数据获取
3. **CDN**: 静态资源使用CDN加速
4. **数据库**: 将历史数据存储到数据库中

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📜 许可证

本项目仅供学习和研究使用，数据来源于AKShare，投资有风险，请谨慎决策。
