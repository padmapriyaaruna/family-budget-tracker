# PostgreSQL Migration Guide for Render

## Step 1: Create PostgreSQL Database on Render

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → Select "**PostgreSQL**"
3. **Configure:**
   - Name: `family-budget-db`
   - Database: `family_budget`
   - User: (auto-generated)
   - Region: Same as your web service
   - Plan: **Free**
4. **Click "Create Database"**
5. **Wait 2-3 minutes** for creation

## Step 2: Connect Database to Web Service

1. **Go to your Web Service** (`family-budget-tracker`)
2. **Click "Environment"** tab (left sidebar)
3. **Add Environment Variable:**
   - Key: `DATABASE_URL`
   - Value: **(get from PostgreSQL database page)**
   
   To get the value:
   - Go to your PostgreSQL database
   - Find "**Internal Database URL**" or "**External Database URL**"
   - Copy the entire connection string (starts with `postgres://` or `postgresql://`)
   - Paste as value

4. **Save Changes**

## Step 3: Deploy Updated Code

The code has been updated to:
- ✅ Auto-detect PostgreSQL via `DATABASE_URL`
- ✅ Use PostgreSQL in production
- ✅ Use SQLite for local development  
- ✅ Same app code works for both!

Simply push the changes:
```bash
git add .
git commit -m "Add PostgreSQL support for data persistence"
git push
```

Render will auto-deploy with PostgreSQL!

## Step 4: Verify

1. **Wait for deployment** (2-3 minutes)
2. **Open your app**
3. **Create admin account** - this time it will be saved in PostgreSQL!
4. **Add members** - data persists!
5. **Try redeploying** - data still there! ✅

## What Happens Now

- **Production (Render)**: Uses PostgreSQL → Data persists forever
- **Local Development**: Uses SQLite → Easy testing
- **No code changes needed** - auto-detects!

## Troubleshooting

**"Can't connect to database"**
- Check DATABASE_URL is correctly set
- Verify PostgreSQL database is running
- Check both are in same region

**"Table doesn't exist"**
- Normal on first run - tables are created automatically
- Just create admin account again

**Still losing data?**
- Verify DATABASE_URL environment variable is set
- Check deployment logs for "🐘 Using PostgreSQL database"
- If you see "📁 Using SQLite", DATABASE_URL isn't set correctly

---

**After Setup**: Your data will persist across all deployments! 🎉
