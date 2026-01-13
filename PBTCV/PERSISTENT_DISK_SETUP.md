# Render Persistent Disk Setup Guide

## 🎯 Goal
Add persistent storage to save your database across deployments.

**Cost:** $0.25/GB/month (~₹20/month for 1GB)  
**Setup Time:** 5 minutes  
**Result:** Data persists forever! ✅

---

## Step 1: Add Persistent Disk in Render

1. **Log in to Render Dashboard**: https://dashboard.render.com

2. **Go to your Web Service**: Click on `family-budget-tracker`

3. **Click "Disks"** in the left sidebar

4. **Click "Create Disk"** button

5. **Configure the disk:**
   - **Name**: `database-storage`
   - **Mount Path**: `/data`
   - **Size**: `1` GB (minimum, perfect for family budget data)

6. **Click "Create"**

7. **Wait 1-2 minutes** for disk to be created and attached

---

## Step 2: Deploy Updated Code

The code has been updated to automatically use the persistent disk!

Just push to GitHub:

```bash
cd PBTCV
git add multi_user_database.py
git commit -m "Add persistent disk support for data persistence"
git push
```

Render will auto-deploy in 1-2 minutes.

---

## Step 3: Verify It's Working

1. **Open your app** after deployment

2. **Check logs** in Render dashboard:
   - You should see: `📁 Using persistent disk storage at /data`
   - NOT: `📁 Using local storage`

3. **Create admin account** and add members

4. **Redeploy** (push any small change to trigger deployment)

5. **Check if data persists** - your admin account should still be there! ✅

---

## What Happens Now?

✅ **Database saved at:** `/data/family_budget.db`  
✅ **Survives deployments:** Yes!  
✅ **Survives restarts:** Yes!  
✅ **Auto-backups:** Render backs up disk daily  
✅ **Cost:** $0.25/month (₹20/month)  

---

## Troubleshooting

**Disk not showing up?**
- Wait 2-3 minutes after creation
- Refresh Render dashboard
- Check "Disks" tab shows "Active"

**Still seeing "local storage" in logs?**
- Verify mount path is exactly `/data`
- Try manual deploy/restart
- Check disk is attached to correct service

**Data still resetting?**
- Confirm disk is created and active
- Check logs for "Using persistent disk storage"
- Contact Render support if issue persists

---

## Cost Breakdown

- **Free tier:** 750 hours/month (enough for 24/7)
- **Persistent disk:** $0.25/GB/month
- **Total:** ~₹20/month

**Worth it?** Absolutely! Your family's financial data is safe forever.

---

Your data persistence is now complete! 🎉
