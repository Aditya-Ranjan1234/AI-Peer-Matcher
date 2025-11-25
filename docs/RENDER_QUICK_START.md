# 🚀 Quick Start: Render Deployment

## Problem Fixed ✅

**Issue**: Pydantic-core build error (Rust compilation failed)

**Solution**: Updated `requirements.txt` to use flexible versions (`>=`) instead of pinned versions

---

## Deployment Steps (Quick Reference)

### 1. Go to Render
Visit: https://render.com → Sign up/Login with GitHub

### 2. Create New Web Service
- Click "New +" → "Web Service"
- Select your repository: `AI-Peer-Matcher`

### 3. Configure Settings

```
Name: ai-peer-matcher-backend
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
Instance: Free
```

### 4. Deploy!
Click "Create Web Service" → Wait 5-10 minutes

### 5. Get Your URL
Copy the URL: `https://ai-peer-matcher-backend.onrender.com`

### 6. Update Frontend
Edit `frontend/config.js`:
```javascript
: 'https://ai-peer-matcher-backend.onrender.com';
```

### 7. Deploy Frontend to Vercel
```bash
cd frontend
vercel --prod
```

### 8. Update CORS
Add frontend URL to `backend/main.py` and push

### 9. Populate Database
Edit `demo/populate_demo.py` with your Render URL, then:
```bash
python demo/populate_demo.py
```

---

## Complete Guide

See `docs/RENDER_DEPLOYMENT.md` for detailed step-by-step instructions!

---

## What Changed in requirements.txt

**Before** (caused errors):
```
pydantic==2.6.4
pydantic-core==2.20.1
```

**After** (works):
```
pydantic>=2.5.0
```

This lets pip choose compatible prebuilt wheels instead of building from source.

---

**Ready to deploy!** Push to GitHub and follow the steps above!
