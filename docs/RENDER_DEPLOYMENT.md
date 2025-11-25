# 🚀 Complete Render Deployment Guide

## Overview

Deploy your AI Peer Matcher backend to Render.com (Free tier available).

**Why Render?**
- ✅ Better Python/ML support than Vercel
- ✅ No timeout limits for model loading
- ✅ Free tier with 750 hours/month
- ✅ Automatic HTTPS
- ✅ Easy database integration

---

## 📋 Prerequisites

- GitHub account with your code pushed
- Render account (free signup at https://render.com)

---

## 🎯 Step-by-Step Deployment

### Step 1: Create Render Account

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (recommended) or email
4. Verify your email

### Step 2: Connect Your GitHub Repository

1. Once logged in, click "New +" in the top right
2. Select "Web Service"
3. Click "Connect GitHub" if not already connected
4. Authorize Render to access your repositories
5. Find and select your repository: `AI-Peer-Matcher`

### Step 3: Configure Your Web Service

Fill in the following settings:

**Basic Settings:**
- **Name**: `ai-peer-matcher-backend` (or your choice)
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: Leave blank (or use `.` for root)
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

**Instance Type:**
- Select **Free** (512 MB RAM, good enough for this app)

### Step 4: Environment Variables (if needed)

Click "Advanced" and add environment variables:

- **Key**: `PYTHON_VERSION`
- **Value**: `3.11.0`

(This ensures a compatible Python version)

### Step 5: Create Web Service

1. Review your settings
2. Click "Create Web Service"
3. Render will start building your app

### Step 6: Monitor the Build

- Watch the deployment logs in real-time
- First deployment takes 5-10 minutes (downloading ML models)
- Look for "Application startup complete" message

### Step 7: Get Your Backend URL

Once deployed, Render provides a URL like:
```
https://ai-peer-matcher-backend.onrender.com
```

Copy this URL!

---

## 🔧 Post-Deployment Configuration

### Update Frontend Configuration

1. Open `frontend/config.js`
2. Replace the placeholder URL:

```javascript
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://ai-peer-matcher-backend.onrender.com'; // Your Render URL
```

3. Save and commit:
```bash
git add frontend/config.js
git commit -m "Update API URL for Render deployment"
git push
```

### Update CORS Settings

1. Edit `backend/main.py`
2. Update allowed origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-url.vercel.app",  # Add after frontend deployment
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. Commit and push:
```bash
git add backend/main.py
git commit -m "Update CORS for production"
git push
```

Render will automatically redeploy.

---

## 🎨 Deploy Frontend to Vercel

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Deploy Frontend

```bash
cd frontend
vercel login
vercel --prod
```

Follow prompts:
- Project name: `ai-peer-matcher`
- Select your account
- Confirm settings

### Step 3: Update CORS with Frontend URL

After frontend deployment, update `backend/main.py` with the new Vercel URL and push again.

---

## 📊 Populate Database

Update `demo/populate_demo.py`:

```python
API_BASE = "https://ai-peer-matcher-backend.onrender.com"
```

Then run:

```bash
python demo/populate_demo.py
```

This will create 100 student profiles on your live backend!

---

## ✅ Verification Checklist

Test your deployment:

### Backend Health Check

Visit in browser:
```
https://ai-peer-matcher-backend.onrender.com/
```

Should return:
```json
{
  "status": "online",
  "message": "AI-Powered Peer Learning Matcher API",
  "total_profiles": 100
}
```

### Frontend Access

Visit your Vercel URL:
```
https://ai-peer-matcher.vercel.app
```

### Full Flow Test

1. Create a test profile through the UI
2. Check if matches are displayed
3. Verify match scores

---

## 🚨 Troubleshooting

### Build Fails with "pydantic-core" Error

**Solution**: Already fixed in `requirements.txt` using `>=` versions

### "Cold Start" - First Request is Slow

**Issue**: Render free tier puts apps to sleep after 15 min of inactivity

**Solutions**:
1. First request after sleep takes ~30 seconds (normal)
2. Use a service like [UptimeRobot](https://uptimerobot.com) to ping every 14 minutes (keeps it awake)
3. Upgrade to paid tier ($7/month) for always-on

### Backend Times Out

**Check**: Ensure Start Command is correct:
```
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### "Module not found" Error

**Check**: `requirements.txt` is in the root directory (not in backend/)

### Frontend Can't Connect

**Check**:
1. Frontend `config.js` has correct Render URL
2. Backend CORS includes frontend URL
3. Both use HTTPS

---

## 🔄 Updating Your Deployment

### Backend Updates

Just push to GitHub:
```bash
git add .
git commit -m "Update backend"
git push
```

Render auto-deploys on every push to `main` branch!

### Frontend Updates

If using Vercel, it also auto-deploys on push.

Or manually:
```bash
cd frontend
vercel --prod
```

---

## 💡 Pro Tips

### 1. View Logs

In Render dashboard:
- Click your service
- Go to "Logs" tab
- See real-time application logs

### 2. Environment Variables

Add secrets in Render dashboard:
- Settings → Environment
- Add variables (e.g., API keys)
- They won't be in your code!

### 3. Custom Domain

Render free tier supports custom domains:
- Settings → Custom Domain
- Add your domain
- Update DNS records

### 4. Health Check Endpoint

Render checks your `/` endpoint. Keep it simple!

### 5. Monitor Usage

Dashboard shows:
- CPU usage
- Memory usage
- Request count
- Deployment history

---

## 📁 Final Render-Specific Files

Your project should have:

```
peer matcher/
├── requirements.txt          # ✅ Fixed versions
├── Procfile                  # Optional (Render auto-detects)
├── backend/
│   ├── main.py              # ✅ With production CORS
│   ├── models.py
│   ├── matcher.py
│   └── requirements.txt     # Can remove (use root one)
└── frontend/
    ├── config.js            # ✅ With Render URL
    └── ...
```

---

## 🎉 Success!

Your app is now live!

- ✅ Backend: https://ai-peer-matcher-backend.onrender.com
- ✅ Frontend: https://ai-peer-matcher.vercel.app
- ✅ Database: 100 student profiles
- ✅ Auto-deployment on git push

---

## 📚 Additional Resources

- [Render Docs](https://render.com/docs)
- [Python on Render](https://render.com/docs/deploy-fastapi)
- [Render Status](https://status.render.com/)

---

**Need help?** Check the troubleshooting section or Render's documentation!
