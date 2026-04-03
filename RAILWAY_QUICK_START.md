# ⚡ Railway Quick Start - 5 Minutes to Live Deployment

Deploy your Deforestation Dashboard **live on Railway in 5 minutes**!

## What You'll Get

✅ Live API endpoint: `https://YOUR_APP.railway.app`
✅ Automatic HTTPS/SSL
✅ Automatic deployments on push
✅ 24/7 uptime
✅ Free tier available ($5/month credit)

## Prerequisites (2 minutes)

1. **GitHub Account** (free at https://github.com)
2. **Railway Account** (free at https://railway.app, login with GitHub)

## 5-Minute Deployment

### Step 1: Initialize Git Repository (1 minute)

```powershell
cd C:\Users\aliscia\deforestation-dashboard

# Initialize git
git init
git config user.email "your@email.com"
git config user.name "Your Name"

# Add all files
git add .

# Commit
git commit -m "Initial commit: Deforestation Dashboard"
```

### Step 2: Create GitHub Repository (1 minute)

1. Go to https://github.com/new
2. Repository name: `deforestation-dashboard`
3. Click "Create repository"
4. Copy the HTTPS URL (looks like: `https://github.com/YOUR_USER/deforestation-dashboard.git`)

### Step 3: Push Code to GitHub (1 minute)

```powershell
# Replace YOUR_USER with your GitHub username
git remote add origin https://github.com/YOUR_USER/deforestation-dashboard.git
git branch -M main
git push -u origin main

# Enter GitHub credentials when prompted
```

### Step 4: Deploy to Railway (2 minutes)

1. Go to https://railway.app
2. Click "Login" → "Login with GitHub" → Authorize
3. Click "New Project"
4. Click "Deploy from GitHub repo"
5. Search for: `deforestation-dashboard`
6. Click it to deploy

**That's it!** 🎉 Railway will:
- Automatically detect Python project
- Install dependencies from `requirements.txt`
- Run `Procfile` to start the app
- Deploy in ~2-3 minutes

### Step 5: Get Your Live URL (instant)

1. In Railway dashboard, click your project
2. Click "Deployments" (the green checkmark)
3. Copy the URL under "Railway Domain"
4. Example: `https://deforestation-dashboard-prod.railway.app`

## Test Your Deployment

```powershell
# Replace with your Railway URL
$url = "https://YOUR_RAILWAY_URL.railway.app"

# Health check (should return 200 OK)
curl "$url/api/health" | ConvertFrom-Json
```

Expected response:
```json
{
  "status": "ok",
  "message": "Deforestation Dashboard API is running"
}
```

## Using Your Live API

Now your API is live! You can:

### 1. Upload CSV Data
```powershell
$url = "https://YOUR_RAILWAY_URL.railway.app"
$file = "C:\path\to\data.csv"

curl -X POST -F "file=@$file" "$url/api/upload"
```

### 2. Train Models
```powershell
curl -X POST "$url/api/models/train"
```

### 3. Get Predictions
```powershell
curl "$url/api/predictions/random-forest"
```

### 4. View All Endpoints
```powershell
# Health check
GET  /api/health

# File upload
POST /api/upload

# Train models
POST /api/models/train

# Get predictions
GET  /api/predictions/random-forest
GET  /api/predictions/lstm-regression
GET  /api/predictions/lstm-classification

# Visualizations
GET  /api/visualizations/loss-trend
GET  /api/visualizations/top-municipalities

# Data export
GET  /api/export/predictions
GET  /api/data-summary
```

## Adding a Frontend

If you want a web interface (not just API):

### Option 1: Deploy Frontend Separately (Easiest)

Deploy to Vercel/Netlify and configure API URL:

```javascript
// frontend/static/js/app.js
const API_URL = 'https://YOUR_RAILWAY_URL.railway.app/api';
```

Then deploy frontend to:
- **Vercel** (https://vercel.com) - for Next.js/React
- **Netlify** (https://netlify.com) - for static sites
- **Railway** (second project) - for Node.js

### Option 2: Deploy Both on Railway

Create two Railway projects:
1. Backend (current)
2. Frontend (Node.js app)

## Making Updates

Your deployment **auto-updates**:

```powershell
# Make changes
Edit-Item backend/app.py

# Commit and push
git add .
git commit -m "Fix: improve model accuracy"
git push origin main

# Railway automatically redeploys!
# Check progress in Railway dashboard
```

## Monitoring Your App

### View Logs
1. Railway dashboard → Click project
2. Click "Deployments"
3. Scroll to see live logs

### Restart App
1. Railway dashboard → Click project
2. Click "Redeploy"

### View Metrics
1. Railway dashboard → "Metrics" tab
2. See CPU, memory, network usage

## Cost

**Free tier:** $5/month credit
- Typically covers this app usage
- After credits: pay-as-you-go

**Pricing:** ~$0.07/hour for small app
- Free tier = ~70 hours/month

## Troubleshooting

### Deploy fails with "502 Bad Gateway"

Check logs:
1. Railway dashboard → Logs tab
2. Look for error messages
3. Common: missing dependency in `requirements.txt`

**Solution:**
```powershell
# Test locally first
pip install -r requirements.txt
gunicorn --bind 0.0.0.0:5000 backend.app:app
```

### "ModuleNotFoundError: No module named X"

Add missing package to `requirements.txt`:
```
package-name==1.0.0
```

Then push:
```powershell
git add requirements.txt
git commit -m "Add missing dependency"
git push origin main
```

### API timeouts during model training

LSTM training is slow. Solutions:
1. Reduce `LSTM_EPOCHS` in `backend/config.py`
2. Upgrade to Railway paid tier
3. Use smaller dataset

## Environment Variables

Set environment variables in Railway:

1. Railway dashboard → Settings
2. Add variable: `DEBUG` = `False`
3. Add variable: `FLASK_ENV` = `production`

## Custom Domain

Add your own domain:

1. Railway dashboard → Settings
2. Click "Custom Domain"
3. Enter: `deforestation.yourdomain.com`
4. Update DNS records (Railway provides instructions)

## Next Steps

1. ✅ GitHub repository created
2. ✅ Code pushed to GitHub
3. ✅ Deployed to Railway
4. ✅ API live at `https://YOUR_URL.railway.app`

**Optional:**
5. Add custom domain
6. Deploy frontend
7. Add database (PostgreSQL)
8. Set up monitoring/alerts

## Important Files

Railway uses these files:
- ✅ `Procfile` - How to run (gunicorn)
- ✅ `requirements.txt` - Python packages
- ✅ `runtime.txt` - Python version
- ✅ `railway.toml` - Railway configuration

All already created! ✅

## API Documentation

Full API docs in: `README.md`

Common endpoints:
```
POST   /api/upload                          # Upload CSV
POST   /api/models/train                    # Train models
GET    /api/predictions/random-forest       # Get predictions
GET    /api/data-summary                    # Data info
```

## Support

- **Railway Docs:** https://docs.railway.app
- **Project Docs:** See `RAILWAY_DEPLOYMENT.md`
- **GitHub Issues:** Link in README

## Success Indicators

Your deployment is working if:

✅ Railway dashboard shows green checkmark
✅ `/api/health` returns `{"status": "ok"}`
✅ Can upload CSV files
✅ Can train models
✅ Can get predictions

## Summary

**You now have:**
- ✅ Live API: `https://YOUR_URL.railway.app`
- ✅ Automatic deployments
- ✅ 24/7 uptime
- ✅ Automatic HTTPS
- ✅ Performance monitoring
- ✅ Free tier with credits

**Deployment time:** ~5 minutes
**Cost:** Free tier or ~$10/month
**Effort:** Minimal!

---

**Congratulations! Your Deforestation Dashboard is live!** 🚀

For detailed information, see `RAILWAY_DEPLOYMENT.md`.
