# Deploy to Render - Complete Guide

## 🚀 Why Render?
- ✅ **Free tier**: 750 hours/month (enough for 24/7)
- ✅ **No rate limits** like Streamlit Cloud
- ✅ **Auto-deploy** from GitHub
- ✅ **Permanent URLs**
- ✅ **Better for production**

---

## 📋 Prerequisites
- ✅ GitHub repository (you have it!)
- ✅ Render account (free)

---

## Step-by-Step Deployment

### 1. Sign Up for Render
1. Go to **https://render.com**
2. Click "**Get Started**"
3. Sign up with **GitHub** (easiest)
4. Authorize Render to access your repositories

### 2. Create New Web Service
1. Click "**New +**" button (top right)
2. Select "**Web Service**"
3. Connect your repository:
   - Find `padmapriyaaruna/family-budget-tracker`
   - Click "**Connect**"

### 3. Configure Your Service

Fill in the form:

**Name**: `family-budget-tracker` (or any name you prefer)

**Region**: Choose closest to you (e.g., Singapore for India)

**Branch**: `main`

**Runtime**: `Python 3`

**Build Command**:
```bash
pip install -r requirements.txt
```

**Start Command**:
```bash
streamlit run family_expense_tracker.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```

**Instance Type**: `Free`

### 4. Environment Variables (Optional)
You can skip this for now. If needed later:
- Click "**Advanced**"
- Add environment variables

### 5. Deploy!
1. Click "**Create Web Service**"
2. Render will:
   - Clone your repo
   - Install dependencies
   - Start your app
3. Wait 3-5 minutes for first deployment

### 6. Get Your URL
- Your app will be at: `https://family-budget-tracker-xyz.onrender.com`
- URL is permanent!
- Share with your family

---

## ⚠️ Important Notes

### Free Tier Limitations
- **Spins down after 15 min of inactivity**
- **Takes 30-60 seconds to wake up** on first visit
- Good for family use, not high-traffic sites

### Database Persistence
- SQLite database will **reset on each deployment**
- For permanent data, consider:
  - PostgreSQL (Render offers free tier)
  - External database service

### Keeping App Awake (Optional)
To prevent spin-down:
- Upgrade to paid plan ($7/month)
- Or use a free uptime monitor like UptimeRobot

---

## 🔄 Updating Your App

Same as before - just push to GitHub:
```bash
git add .
git commit -m "Updated feature"
git push
```

Render auto-deploys within 2-3 minutes!

---

## 🆘 Troubleshooting

**"Application failed to respond"**
- Check if port configuration is correct
- Verify start command includes `--server.port=$PORT`

**"Build failed"**
- Check requirements.txt has all dependencies
- View build logs in Render dashboard

**Database keeps resetting**
- Normal behavior for free tier
- Migrate to PostgreSQL for persistence

---

## ✅ Advantages Over Streamlit Cloud
- No rate limit issues
- More generous free tier
- Better for production use
- Supports custom domains (paid plan)

---

Your app will be live at a permanent URL! 🎉

**Next**: Share the URL with your family and they can access from anywhere!
