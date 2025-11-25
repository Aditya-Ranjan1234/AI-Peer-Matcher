# 🚀 Vercel Deployment Guide - AI Peer Matching Matcher

## 📋 Overview

This guide walks you through deploying both the backend (FastAPI) and frontend (HTML/CSS/JS) to Vercel.

**Important Note:** Vercel has limitations with Python deployments. The backend may work better on Railway or Heroku. However, I'll provide both deployment options.

---

## ⚠️ Important: Vercel Limitations for Python

Vercel's Python support has some constraints:
- **Function timeout**: 10 seconds (hobby tier)
- **Cold starts**: Model loading takes time
- **Memory limits**: May struggle with NLP models

### Recommended Alternative: Railway

For the backend, **Railway** is better suited:
- No timeout issues
- Better for long-running processes
- Free tier available
- Easier Python deployment

---

## 🔧 Files Created for Deployment

### Already Created:
1. ✅ `vercel.json` - Vercel configuration (root)
2. ✅ `requirements.txt` - Python dependencies (root)
3. ✅ `frontend/config.js` - API endpoint configuration

---

## 🎯 Option 1: Deploy Backend to Railway (Recommended)

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

### Step 2: Login to Railway

```bash
railway login
```

### Step 3: Deploy Backend

```bash
cd "d:/5th Sem/peer matcher"
railway init
railway up
```

### Step 4: Get Backend URL

After deployment, Railway will provide a URL like:
```
https://your-app.up.railway.app
```

### Step 5: Update Frontend Config

Edit `frontend/config.js`:
```javascript
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://your-app.up.railway.app'; // Replace with your Railway URL
```

---

## 🎯 Option 2: Deploy Both to Vercel

### Backend Deployment to Vercel

#### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

#### Step 2: Login to Vercel

```bash
vercel login
```

#### Step 3: Deploy Backend

```bash
cd "d:/5th Sem/peer matcher"
vercel --prod
```

Follow the prompts:
- **Set up and deploy**: Y
- **Which scope**: Select your account
- **Link to existing project**: N
- **Project name**: ai-peer-matcher-api (or your choice)
- **Directory**: . (current directory)


#### Step 4: Note the Deployment URL

Vercel will provide a URL like:
```
https://ai-peer-matcher-api.vercel.app
```

---

### Frontend Deployment to Vercel

#### Step 1: Update API URL in config.js

Edit `frontend/config.js` and replace the URL:
```javascript
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : 'https://ai-peer-matcher-api.vercel.app'; // Your backend URL
```

#### Step 2: Create vercel.json for Frontend

Create `frontend/vercel.json`:
```json
{
  "version": 2
}
```

#### Step 3: Deploy Frontend

```bash
cd frontend
vercel --prod
```

Follow the prompts:
- **Set up and deploy**: Y
- **Which scope**: Select your account
- **Link to existing project**: N
- **Project name**: ai-peer-matcher (or your choice)
- **Directory**: . (current directory)

#### Step 4: Access Your App

Vercel will provide a URL like:
```
https://ai-peer-matcher.vercel.app
```

---

## 🔐 Post-Deployment Configuration

### Update CORS in Backend

Edit `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-peer-matcher.vercel.app",  # Your frontend URL
        "http://localhost:3000",  # For local testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy backend:
```bash
vercel --prod
```

---

## 📊 Database Initialization

Your 100-student database (`demo_profiles.json`) won't automatically populate. You have two options:

### Option 1: API-based Population (Recommended)

1. Keep `demo/populate_demo.py`
2. Run it pointing to your deployed backend:

```python
# Edit demo/populate_demo.py
API_BASE = "https://your-backend-url.vercel.app"
```

Then run:
```bash
python demo/populate_demo.py
```

### Option 2: Persistent Database (Better for Production)

Add a database like:
- **Supabase** (PostgreSQL, free tier)
- **MongoDB Atlas** (free tier)
- **PlanetScale** (MySQL, free tier)

This ensures profiles persist across deployments.

---

## ✅ Verification Checklist

After deployment:

- [ ] Backend URL is accessible (test with `/` endpoint)
- [ ] Frontend loads correctly
- [ ] Frontend config.js has correct backend URL
- [ ] CORS is configured with frontend URL
- [ ] Can create a test profile through the UI
- [ ] Matches are returned successfully
- [ ] Database has been populated (optional)

---

## 🧪 Testing Deployed App

### Test Backend Directly

```bash
curl https://your-backend-url.vercel.app/
```

Should return:
```json
{
  "status": "online",
  "message": "AI-Powered Peer Learning Matcher API",
  "total_profiles": 0
}
```

### Test Profile Creation

```bash
curl -X POST https://your-backend-url.vercel.app/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test001",
    "name": "Test User",
    "strengths": "Mathematics, Physics",
    "weaknesses": "Literature, Writing",
    "preferences": "Evenings",
    "description": "Test profile"
  }'
```

---

## 🚨 Troubleshooting

### Backend Times Out on Vercel

**Problem**: Sentence Transformers model takes too long to load

**Solution**: Use Railway instead, which has no timeout limits

### Frontend Can't Connect to Backend

**Check**:
1. `frontend/config.js` has correct backend URL
2. Backend CORS includes frontend URL
3. Both using HTTPS (or both HTTP for local)

### "Module not found" errors

**Solution**: Ensure `requirements.txt` is in the root directory

### Cold Start Issues

**Solution**:
- Use Railway for backend (no cold starts)
- Or implement a simple "ping" endpoint that keeps the function warm

---

## 📁 Final Project Structure

```
peer matcher/
├── vercel.json              # Backend Vercel config
├── requirements.txt         # Python dependencies
├── Procfile                 # Railway/Heroku config
├── demo_profiles.json       # Student database
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── matcher.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   ├── config.js           # API URL configuration
│   └── vercel.json         # Frontend Vercel config (optional)
├── docs/
└── demo/
```

---

## 🎉 Success!

If everything works:
- ✅ Frontend is live on Vercel
- ✅ Backend is live on Railway/Vercel
- ✅ Students can create profiles
- ✅ Matching algorithm works
- ✅ Database is populated

---

## 📚 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

**Questions?** Check the troubleshooting section or the main README.md
