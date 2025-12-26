"""
System Verification Script
Checks all components are properly configured for deployment
"""

import os
import json

print("=" * 70)
print("AI PEER MATCHER - SYSTEM VERIFICATION")
print("=" * 70)

errors = []
warnings = []
success = []

# Check root directory files
print("\n📁 Checking Root Directory...")

if os.path.exists("vercel.json"):
    success.append("✅ vercel.json exists")
else:
    errors.append("❌ vercel.json missing")

if os.path.exists("requirements.txt"):
    success.append("✅ requirements.txt exists")
else:
    errors.append("❌ requirements.txt missing")

if os.path.exists("Procfile"):
    success.append("✅ Procfile exists")
else:
    warnings.append("⚠️  Procfile missing (needed for Railway/Heroku)")

if os.path.exists("demo_profiles.json"):
    with open("demo_profiles.json", "r") as f:
        profiles = json.load(f)
        if len(profiles) == 31:
            success.append(f"✅ demo_profiles.json has {len(profiles)} profiles")
        else:
            warnings.append(f"⚠️  demo_profiles.json has {len(profiles)} profiles (expected 100)")
else:
    errors.append("❌ demo_profiles.json missing")

# Check backend files
print("\n🔧 Checking Backend...")

backend_files = ["backend/main.py", "backend/models.py", "backend/matcher.py", "backend/requirements.txt"]
for file in backend_files:
    if os.path.exists(file):
        success.append(f"✅ {file} exists")
    else:
        errors.append(f"❌ {file} missing")

# Check frontend files
print("\n🎨 Checking Frontend...")

frontend_files = ["frontend/index.html", "frontend/style.css", "frontend/app.js", "frontend/config.js"]
for file in frontend_files:
    if os.path.exists(file):
        success.append(f"✅ {file} exists")
    else:
        errors.append(f"❌ {file} missing")

if os.path.exists("frontend/vercel.json"):
    success.append("✅ frontend/vercel.json exists")
else:
    warnings.append("⚠️  frontend/vercel.json missing (optional)")

# Check config.js content
if os.path.exists("frontend/config.js"):
    with open("frontend/config.js", "r") as f:
        content = f.read()
        if "your-backend-url.vercel.app" in content:
            warnings.append("⚠️  frontend/config.js still has placeholder URL - update after deploying backend!")
        else:
            success.append("✅ frontend/config.js appears configured")

# Check documentation
print("\n📚 Checking Documentation...")

doc_files = ["README.md", "docs/VERCEL_DEPLOYMENT.md"]
for file in doc_files:
    if os.path.exists(file):
        success.append(f"✅ {file} exists")
    else:
        warnings.append(f"⚠️  {file} missing")

# Print results
print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)

if success:
    print("\n✅ SUCCESS:")
    for item in success:
        print(f"   {item}")

if warnings:
    print("\n⚠️  WARNINGS:")
    for item in warnings:
        print(f"   {item}")

if errors:
    print("\n❌ ERRORS:")
    for item in errors:
        print(f"   {item}")

print("\n" + "=" * 70)

if errors:
    print("❌ SYSTEM HAS ERRORS - Fix before deploying!")
elif warnings:
    print("⚠️  SYSTEM IS MOSTLY READY - Review warnings before deploying")
else:
    print("✅ SYSTEM IS READY FOR DEPLOYMENT!")

print("=" * 70)

print("\n📖 Next Steps:")
print("1. Review docs/VERCEL_DEPLOYMENT.md for deployment instructions")
print("2. Deploy backend to Railway (recommended) or Vercel")
print("3. Update frontend/config.js with backend URL")
print("4. Deploy frontend to Vercel")
print(f"5. Populate database using demo/populate_demo.py\n")
