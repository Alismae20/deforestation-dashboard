# 🚀 Railway Deployment Guide

Deploy your Deforestation Detection Dashboard to Railway in minutes!

## What is Railway?

Railway is a modern platform for deploying web applications. It's:
- ✅ Easy to use (GitHub integration)
- ✅ Fast deployment
- ✅ Free tier available ($5/month credit)
- ✅ Automatic scaling
- ✅ Built-in monitoring

## Prerequisites

1. **GitHub Account** - Railway uses GitHub for deployment
   - Create account at https://github.com
   - Push your code to a GitHub repository

2. **Railway Account** - Free to create
   - Sign up at https://railway.app
   - Link your GitHub account

## Step-by-Step Deployment

### Step 1: Prepare Your Project for Railway

The following files are already created:
- ✅ `Procfile` - Tells Railway how to run the app
- ✅ `railway.toml` - Railway configuration
- ✅ `runtime.txt` - Python version specification
- ✅ `requirements-railway.txt` - Production dependencies

### Step 2: Push Code to GitHub

1. **Create GitHub repository:**
   ```powershell
   cd C:\Users\aliscia\deforestation-dashboard
   git init
   git add .
   git commit -m "Initial commit: Deforestation Dashboard"
   ```

2. **Create repo on GitHub:**
   - Go to https://github.com/new
   - Name: `deforestation-dashboard`
   - Description: "Deforestation detection with LSTM and Random Forest"
   - Click "Create repository"

3. **Push to GitHub:**
   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/deforestation-dashboard.git
   git branch -M main
   git push -u origin main
   ```

### Step 3: Deploy to Railway

1. **Login to Railway:**
   - Go to https://railway.app
   - Click "Login"
   - Choose "Login with GitHub"
   - Authorize Railway

2. **Create New Project:**
   - Click "New Project"
   - Click "Deploy from GitHub repo"
   - Find & select `deforestation-dashboard`

3. **Configure Environment:**
   - Click the environment
   - Add variables (optional):
     ```
     FLASK_ENV=production
     DEBUG=False
     ```

4. **Deploy:**
   - Railway automatically deploys
   - Watch the logs
   - Once green ✅, it's live!

5. **Get Your URL:**
   - Click your deployment
   - Find "Deployments" → Live URL
   - Example: `https://deforestation-dashboard.railway.app`

### Step 4: Test Your Deployment

```powershell
# Health check
curl https://YOUR_RAILWAY_URL/api/health

# Upload CSV
$file = Get-Item "C:\path\to\data.csv"
curl -X POST -F "file=@$file" `
  https://YOUR_RAILWAY_URL/api/upload
```

## Using Your Live Dashboard

### Option 1: API Only (No Frontend)
Access the API directly:
```
https://YOUR_RAILWAY_URL/api/health
https://YOUR_RAILWAY_URL/api/upload (POST)
https://YOUR_RAILWAY_URL/api/models/train (POST)
https://YOUR_RAILWAY_URL/api/predictions/random-forest (GET)
```

### Option 2: With Frontend (Recommended)

The frontend needs to be served separately. Options:

**A) Deploy Frontend to Vercel/Netlify (EASIEST)**

1. Copy frontend files to new directory:
   ```powershell
   mkdir deforestation-frontend
   cp frontend/templates/index.html deforestation-frontend/
   cp frontend/static deforestation-frontend/
   ```

2. Create `vercel.json`:
   ```json
   {
     "rewrites": [
       { "source": "/(.*)", "destination": "/index.html" }
     ]
   }
   ```

3. Deploy to Vercel (https://vercel.com)

4. Update API URL in frontend:
   - Edit `frontend/static/js/app.js`
   - Change: `const API_URL = 'http://localhost:5000/api';`
   - To: `const API_URL = 'https://YOUR_RAILWAY_URL/api';`

**B) Deploy Both on Railway**

Create separate Railway projects:
1. Backend on Railway (current)
2. Frontend as separate Node.js app

## Railway Project Structure

```
deforestation-dashboard/
├── Procfile                  ← Tells Railway how to run backend
├── railway.toml             ← Railway configuration
├── runtime.txt              ← Python version
├── requirements.txt         ← Python dependencies
├── backend/
│   ├── app.py              ← Main Flask app
│   ├── config.py           ← Configuration
│   ├── models/             ← ML models
│   └── utils/              ← Data processing
├── frontend/               ← Static files (optional)
│   ├── templates/
│   └── static/
└── .git/                   ← Git repository
```

## Environment Variables on Railway

Set these in Railway dashboard under "Variables":

```
FLASK_ENV=production
DEBUG=False
PYTHONUNBUFFERED=1
UPLOAD_FOLDER=/tmp/uploads
```

## Important Notes

### File Upload Limitations

Railway has ephemeral storage - uploaded files are deleted when app restarts.

**Solution:** Use persistent storage (Railway PostgreSQL):

```python
# In app.py - save to database instead of filesystem
import json

@app.route('/api/upload', methods=['POST'])
def upload_file():
    # Instead of saving to disk:
    # os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    # file.save(filepath)
    
    # Save to memory/database:
    csv_content = file.read().decode('utf-8')
    # Parse and process directly
```

### Model Training Performance

Railway free tier has limited resources. For large datasets:
- Reduce batch size in `backend/config.py`
- Reduce LSTM epochs
- Or use Railway paid tier

### Cost Estimation

**Railway Pricing:**
- Free: $5/month credit
- Pay as you go: After credits used
- Typical usage: $0-10/month for this app

## Monitoring & Debugging

### View Logs
1. Go to Railway dashboard
2. Click your project
3. Select "Deployments"
4. View logs in real-time

### Common Issues

**Issue: "502 Bad Gateway"**
- Check backend logs
- Verify Procfile is correct
- Restart deployment

**Issue: "ModuleNotFoundError"**
- Check requirements.txt has all packages
- Verify `pip install -r requirements.txt` works locally

**Issue: "Port already in use"**
- Railway assigns PORT automatically
- Procfile should use `$PORT` variable

### Restart Deployment

Click "Redeploy" in Railway dashboard

## Update Your Live App

To make changes and deploy:

```powershell
# Make changes to code
cd C:\Users\aliscia\deforestation-dashboard

# Commit and push
git add .
git commit -m "Update: describe changes"
git push origin main

# Railway automatically redeploys!
```

## Using Railway PostgreSQL (Optional)

For persistent storage instead of file uploads:

1. **Add Database:**
   - Railway dashboard → Add service
   - Choose PostgreSQL

2. **Connection string:**
   - Railway provides automatically
   - Available as `DATABASE_URL` env variable

3. **Update app.py:**
   ```python
   from sqlalchemy import create_engine
   engine = create_engine(os.environ.get('DATABASE_URL'))
   
   # Store CSV data in database instead of files
   df.to_sql('uploads', engine, if_exists='append')
   ```

## Custom Domain

1. Go to Railway project settings
2. Add custom domain: `deforestation.yourdomain.com`
3. Update DNS records (Railway provides instructions)

## Scaling Your App

As usage grows:

1. **Increase dyno size:**
   - Railway dashboard → Settings
   - Choose higher tier

2. **Add caching:**
   - Use Redis for model predictions
   - Cache frequently accessed data

3. **Optimize code:**
   - Profile bottlenecks
   - Optimize LSTM training

## Production Checklist

✅ Code pushed to GitHub
✅ `Procfile` configured correctly
✅ `requirements.txt` has all dependencies
✅ Environment variables set in Railway
✅ Tests passed locally before pushing
✅ No hardcoded secrets (use env variables)
✅ Error handling implemented
✅ Logs being monitored
✅ Backups of important data

## Next Steps

1. Create GitHub repository
2. Push code: `git push origin main`
3. Connect Railway to GitHub
4. Deploy!
5. Test with: `curl https://YOUR_URL/api/health`

## Support & Resources

- **Railway Docs:** https://docs.railway.app
- **GitHub Actions:** https://github.com/features/actions
- **Flask Production:** https://flask.palletsprojects.com/deployment/
- **Project Docs:** See START_HERE.md

## Quick Reference

| Task | Command |
|------|---------|
| Initialize Git | `git init` |
| Add all files | `git add .` |
| Commit | `git commit -m "message"` |
| Push to GitHub | `git push origin main` |
| View Railway logs | Railway dashboard → Logs |
| Restart deployment | Railway dashboard → Redeploy |
| Scale up | Railway dashboard → Resources |

## Example Railway Project URL

After deployment, your app will be live at:
```
https://deforestation-dashboard-prod.railway.app
```

## Troubleshooting Deploy Fails

1. **Check Procfile syntax:**
   ```
   web: cd backend && gunicorn --bind 0.0.0.0:$PORT app:app
   ```

2. **Verify requirements.txt:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Test locally:**
   ```powershell
   gunicorn --bind 0.0.0.0:5000 backend.app:app
   ```

4. **Check Railway logs** for specific errors

## Conclusion

Your Deforestation Dashboard is now **production-ready** and can be deployed to Railway in minutes!

For any issues, check Railway documentation or the project's START_HERE.md file.

Happy deploying! 🚀
