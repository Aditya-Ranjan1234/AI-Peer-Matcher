# 🎨 Complete Vercel Frontend Deployment Guide

## ✅ Backend Status: WORKING!

Your backend is live at: **https://ai-peer-matcher.onrender.com**

- ✅ Status: Online
- ✅ API responding correctly
- ✅ Ready to accept frontend connections

---

## 📋 Prerequisites

- Vercel account (free signup at https://vercel.com)
- GitHub with your code pushed
- Node.js installed (for Vercel CLI)

---

## 🚀 Method 1: Deploy via Vercel Website (Easiest)

### Step 1: Create Vercel Account

1. Go to https://vercel.com
2. Click "Sign Up"
3. Choose "Continue with GitHub" (recommended)
4. Authorize Vercel to access your GitHub

### Step 2: Import Your Project

1. After login, click "Add New..." → "Project"
2. Click "Import Git Repository"
3. Find and select: `Aditya-Ranjan1234/AI-Peer-Matcher`
4. Click "Import"

### Step 3: Configure Project

**Framework Preset:**
- Select: "Other" (since it's vanilla HTML/CSS/JS)

**Root Directory:**
- Click "Edit" next to Root Directory
- Enter: `frontend`
- Click "Continue"

**Build & Output Settings:**
- Build Command: Leave empty (no build needed)
- Output Directory: Leave as `.` (current directory)
- Install Command: Leave empty

### Step 4: Environment Variables

Skip this section (no env vars needed for frontend)

### Step 5: Deploy!

1. Click "Deploy"
2. Wait 30-60 seconds
3. You'll see "Congratulations!" when done

### Step 6: Get Your URL

Vercel provides a URL like:
```
https://ai-peer-matcher-<random>.vercel.app
```

Click "Visit" to see your live frontend!

---

## 🚀 Method 2: Deploy via Vercel CLI (Advanced)

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Login

```bash
vercel login
```

Enter your email and verify.

### Step 3: Navigate to Frontend

```bash
cd "d:/5th Sem/peer matcher/frontend"
```

### Step 4: Deploy

```bash
vercel --prod
```

**Answer the prompts:**

```
? Set up and deploy "~/frontend"? [Y/n] Y
? Which scope? → Select your account
? Link to existing project? [y/N] N
? What's your project's name? ai-peer-matcher
? In which directory is your code located? ./ 
```

### Step 5: Wait for Deployment

Vercel will:
- Upload your files
- Deploy to production
- Give you a URL

---

## 🔧 Post-Deployment Configuration

### Update Backend CORS

Your frontend URL needs to be added to backend CORS.

1. Edit `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ai-peer-matcher-<your-id>.vercel.app",  # Your Vercel URL
        "https://ai-peer-matcher.vercel.app",  # If you set custom domain
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. Commit and push:

```bash
git add backend/main.py
git commit -m "Add frontend URL to CORS"
git push
```

Render will auto-deploy the backend update!

---

## 📊 Populate Database

Now that both frontend and backend are live, populate with 100 students:

### Step 1: Update populate script

The API URL is already set to your Render backend in `demo/populate_demo.py`

### Step 2: Run it

```bash
cd "d:/5th Sem/peer matcher"
.\venv\Scripts\Activate.ps1
python demo/populate_demo.py
```

This creates 100 random student profiles on your live backend!

---

## ✅ Verification Checklist

### Test Backend

Visit: https://ai-peer-matcher.onrender.com/

Should show:
```json
{
  "status": "online",
  "message": "AI-Powered Peer Learning Matcher API",
  "total_profiles": 100
}
```

### Test Frontend

Visit your Vercel URL and:

1. ✅ Page loads with no errors
2. ✅ Form is visible and styled correctly
3. ✅ Create a test profile:
   - ID: `test001`
   - Name: `Test User`
   - Select some strengths (e.g., Mathematics, Physics)
   - Select some weaknesses (e.g., Literature, Writing)
   - Click "Create Profile & Find Matches"

4. ✅ Matches appear with:
   - Match cards displayed
   - Match scores shown (percentage)
   - Complementary skills highlighted

### Check Browser Console

Press F12 → Console tab:
- ✅ No errors
- ✅ See "API is online and ready" message

---

## 🎯 Custom Domain (Optional)

### Add Your Own Domain

1. In Vercel dashboard, go to your project
2. Click "Settings" → "Domains"
3. Add your custom domain (e.g., `peermatcher.yourdomain.com`)
4. Follow Vercel's DNS instructions
5. Update backend CORS with new domain

---

## 🔄 Auto-Deployment Setup

Good news: **Already configured!**

Vercel automatically redeploys when you push to GitHub:

```bash
# Make changes to frontend
git add frontend/
git commit -m "Update UI"
git push
```

Vercel detects the push and redeploys automatically!

---

## 🚨 Troubleshooting

### Frontend Shows "Backend API not running"

**Check:**
1. `frontend/config.js` has correct Render URL ✅ (already updated)
2. Backend CORS includes your Vercel URL
3. Both use HTTPS

**Fix:**
Add your Vercel URL to `backend/main.py` CORS and push.

### CORS Error in Browser Console

**Error:** `Access to fetch blocked by CORS policy`

**Solution:**
```python
# In backend/main.py, add your Vercel URL to allow_origins
allow_origins=[
    "https://your-frontend.vercel.app",  # Add this
    ...
]
```

### "Failed to fetch" Error

**Check:**
1. Backend is online: https://ai-peer-matcher.onrender.com/
2. Render free tier: First request after inactivity takes 30s

**Solution:** Wait and retry, or keep backend awake with UptimeRobot

### Vercel Build Fails

**Issue:** Vercel trying to build when no build is needed

**Solution:**
- Set Build Command to empty
- Set Root Directory to `frontend`

---

## 📱 Testing on Mobile

Your Vercel URL works on mobile too!

1. Open your Vercel URL on phone
2. Test creating a profile
3. Check matches work

---

## 💡 Pro Tips

### 1. Preview Deployments

Every git push creates a preview:
- Main branch → Production
- Other branches → Preview URLs
- Test before going live!

### 2. Environment Variables

Add in Vercel dashboard:
- Settings → Environment Variables
- Useful for API keys (if needed later)

### 3. Analytics

Vercel provides free analytics:
- Dashboard → Analytics
- See visitor stats, page views, etc.

### 4. Custom 404 Page

Create `frontend/404.html` for custom error page

### 5. Performance Monitoring

Vercel shows:
- Load times
- Core Web Vitals
- Performance score

---

## 📁 Final File Structure

```
peer matcher/
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   ├── config.js          # ✅ Updated with Render URL
│   └── vercel.json
├── backend/
│   └── main.py           # ⚠️ Update CORS with Vercel URL
└── ...
```

---

## 🎉 Success Criteria

Your deployment is complete when:

1. ✅ Backend responds: https://ai-peer-matcher.onrender.com/
2. ✅ Frontend loads: https://your-app.vercel.app
3. ✅ Can create profiles through UI
4. ✅ Matches display correctly
5. ✅ Database has 100 profiles
6. ✅ No CORS errors in console

---

## 🔗 Your Live URLs

**Backend**: https://ai-peer-matcher.onrender.com ✅

**Frontend**: `https://ai-peer-matcher-<your-id>.vercel.app`

(You'll get this after deployment)

---

## 📚 Next Steps

1. Deploy frontend using Method 1 or 2 above
2. Update backend CORS with frontend URL
3. Populate database with `python demo/populate_demo.py`
4. Test full flow
5. Share your live project! 🚀

---

## 📖 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel CLI Docs](https://vercel.com/docs/cli)
- [Custom Domains Guide](https://vercel.com/docs/concepts/projects/custom-domains)

---

**Ready to deploy?** Follow Method 1 above for the easiest experience!
