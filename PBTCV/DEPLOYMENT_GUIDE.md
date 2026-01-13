# Deploy Family Budget Tracker to Streamlit Cloud

## 🌐 Why Streamlit Cloud?
- ✅ **Free** hosting
- ✅ **24/7** availability
- ✅ **No server** maintenance
- ✅ Accessible from **anywhere**
- ✅ **Auto-updates** when you push changes

---

## 📋 Prerequisites

1. **GitHub Account** (free)
   - Sign up at: https://github.com

2. **Git Installed** (check with `git --version`)
   - If not installed: https://git-scm.com/downloads

3. **Streamlit Cloud Account** (free)
   - Sign up at: https://streamlit.io/cloud

---

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Your Project

Already done! Your project is ready in:
`PBTCV`

### Step 2: Initialize Git Repository

Open terminal in your project folder and run:

```bash
cd PBTCV
git init
git add .
git commit -m "Initial commit - Family Budget Tracker"
```

### Step 3: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `family-budget-tracker`
3. Description: "Multi-user family expense tracker"
4. Keep it **Private** (recommended for family data)
5. Click "Create repository"

### Step 4: Push to GitHub

GitHub will show you commands. Run:

```bash
git remote add origin https://github.com/YOUR_USERNAME/family-budget-tracker.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

### Step 5: Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "**New app**"
3. Connect your GitHub account (if not already)
4. Select:
   - **Repository**: `family-budget-tracker`
   - **Branch**: `main`
   - **Main file path**: `family_expense_tracker.py`
5. Click "**Deploy!**"

### Step 6: Wait for Deployment

- Takes 2-5 minutes
- Streamlit Cloud will build and deploy
- You'll get a URL like: `https://your-app.streamlit.app`

### Step 7: Share with Family

Send them:
- **App URL**: `https://your-app.streamlit.app`
- **Instructions**: Use the password setup tab
- **Invite tokens**: From admin panel

---

## ⚠️ Important Notes

### Data Persistence

**Issue**: Streamlit Cloud may reset your SQLite database periodically.

**Solutions**:

**Option A: Accept Resets** (Simple)
- Good for testing
- Recreate accounts when reset happens
- Not ideal for long-term use

**Option B: Use External Database** (Better)
- Migrate to PostgreSQL (free tier on Supabase/Railway)
- Data persists permanently
- Requires code modification

**Option C: Download Database Regularly**
- Export data manually
- Backup locally
- Re-upload when needed

### Privacy Considerations

**Public vs Private Repo**:
- **Private**: Recommended - code visible only to you
- **Public**: Anyone can see code, but NOT your data

**Database Security**:
- Database file (`family_budget.db`) is NOT public
- Passwords are hashed
- Data stays private even on cloud

---

## 🔧 Troubleshooting

**"Requirements not found" error:**
- Make sure `requirements.txt` is in root folder
- Should contain: `streamlit`, `pandas`, `plotly`

**"Module not found" error:**
- Add missing packages to `requirements.txt`
- Redeploy

**"File not found" error:**
- Check `family_expense_tracker.py` is in root
- Verify `multi_user_database.py` is present
- Check `config.py` exists

**Database resets:**
- Normal behavior on Streamlit Cloud
- Consider external database for persistence

---

## 🎯 After Deployment

### Your app will be at:
`https://YOUR-APP-NAME.streamlit.app`

### Features:
- ✅ Accessible 24/7
- ✅ Works on mobile & desktop
- ✅ No need to keep computer on
- ✅ Auto-updates when you push to GitHub
- ✅ Free HTTPS (secure)

### To Update Your App:
```bash
# Make changes to code
git add .
git commit -m "Updated feature X"
git push
# Streamlit Cloud auto-deploys!
```

---

## 📞 Need Help?

**Stuck on Git?** 
- Tutorial: https://docs.github.com/en/get-started/quickstart/hello-world

**Streamlit Cloud issues?**
- Docs: https://docs.streamlit.io/streamlit-community-cloud

**Want external database?**
- I can help migrate to PostgreSQL

---

## ✅ Quick Checklist

- [ ] GitHub account created
- [ ] Git installed
- [ ] Repository initialized
- [ ] Code pushed to GitHub
- [ ] Streamlit Cloud account created
- [ ] App deployed
- [ ] URL shared with family
- [ ] Tested on mobile

---

Enjoy your 24/7 accessible family budget tracker! 🎉
