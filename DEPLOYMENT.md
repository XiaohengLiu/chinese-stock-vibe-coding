# 🚀 Deployment Guide

## Quick Deploy Options

### 🏆 Option 1: Render (Recommended)

1. **Sign up for Render** (free): https://render.com
2. **Connect GitHub**: Link your GitHub account
3. **Create Web Service**:
   - Repository: `XiaohengLiu/chinese-stock-vibe-coding`
   - Branch: `main`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Plan: Free
4. **Deploy**: Click "Create Web Service"
5. **Your URL**: `https://your-app-name.onrender.com`

### 🥈 Option 2: Railway

1. **Sign up for Railway**: https://railway.app
2. **Deploy from GitHub**:
   - Connect GitHub account
   - Select repository: `chinese-stock-vibe-coding`
   - Railway auto-detects Python and deploys
3. **Your URL**: `https://your-app-name.up.railway.app`

### 🥉 Option 3: Vercel

1. **Sign up for Vercel**: https://vercel.com
2. **Import Project**: From GitHub
3. **Configure**:
   - Framework: Other
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: (leave empty)
4. **Deploy**: Automatic

## 📁 Deployment Files Created

- `render.yaml` - Render configuration
- `Procfile` - Process configuration
- `runtime.txt` - Python version specification
- `requirements.txt` - Dependencies (already exists)

## 🌐 Expected URLs

After deployment, your app will be available at:
- **Render**: `https://chinese-stock-analysis.onrender.com`
- **Railway**: `https://chinese-stock-vibe-coding.up.railway.app`
- **Vercel**: `https://chinese-stock-vibe-coding.vercel.app`

## 🔧 Environment Variables (if needed)

For production, you might want to set:
- `FLASK_ENV=production`
- `PYTHONPATH=/app`

## 📊 Features Available Online

Once deployed, users worldwide can:
- ✅ Enter Chinese stock codes (600519, 000858, etc.)
- ✅ View annual financial data tables
- ✅ View half-year financial data tables
- ✅ See YoY growth rates with color coding
- ✅ Access from any device (mobile, tablet, desktop)
- ✅ Use the app 24/7 (with some cold start delay on free tiers)

## 🔍 Monitoring

- **Health Check**: `https://your-url/health`
- **Logs**: Available in platform dashboards
- **Performance**: Monitor response times

## 🚨 Limitations on Free Tiers

- **Render**: Sleeps after 15 min inactivity (~30s wake time)
- **Railway**: $5 monthly credit limit
- **Vercel**: Serverless functions (10s timeout)

## 💡 Pro Tips

1. **Custom Domain**: Most platforms allow free custom domains
2. **Analytics**: Add Google Analytics if needed
3. **Caching**: Consider adding caching for better performance
4. **Monitoring**: Set up uptime monitoring with UptimeRobot

## 🔄 Auto-Deployment

All platforms support auto-deployment:
- Push to GitHub → Automatic deployment
- Real-time logs and build status
- Rollback capabilities
