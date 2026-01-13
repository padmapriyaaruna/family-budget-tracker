# How to Find Supabase Connection Pooler URL

## 🎯 Quick Guide - Step by Step

### Step 1: Go to Supabase Dashboard
1. Open your browser and go to: **https://supabase.com/dashboard**
2. Sign in if needed
3. You should see your project(s) listed

### Step 2: Open Your Project
1. Click on your project name (e.g., "family-budget-db")
2. This opens your project dashboard

### Step 3: Navigate to Database Settings
1. Look at the **left sidebar**
2. Scroll down to the bottom
3. Click the **⚙️ Settings** icon (or "Project Settings")
4. In the settings menu that opens, click **"Database"**

### Step 4: Find Connection Pooling Section

On the Database settings page, you'll see several sections. **Scroll down** past:
- ✅ Connection parameters
- ✅ Connection string (Direct connection - **DON'T use this one!**)

Keep scrolling until you find:

#### **🎯 Connection Pooling** section

This section will have:
- A toggle to "Enable connection pooling" (should be ON)
- A dropdown for **Mode** - select **"Transaction"**
- A **Connection string** that looks like:

```
postgresql://postgres.awpxetcrxvegsaenutzf:[YOUR-PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
```

**Notice the differences from direct connection:**
- Has `.pooler.supabase.com` in the host
- Port is **6543** (not 5432)
- Includes region info (e.g., `aws-0-ap-south-1`)

### Step 5: Copy the Connection Pooling String

1. Make sure **Mode** is set to **"Transaction"**
2. Click the **📋 Copy** button next to the connection string
3. Or manually copy the entire string

---

## 🔍 Can't Find "Connection Pooling"?

If you don't see a "Connection Pooling" section on the Database settings page:

### Option A: Use Supavisor Pooler (Newer Supabase Projects)

Your connection pooler URL follows this format:
```
postgresql://postgres.PROJECT_REF:[PASSWORD]@aws-0-REGION.pooler.supabase.com:6543/postgres
```

**To construct it manually:**

1. Take your current DATABASE_URL:
   ```
   postgresql://postgres:[PASSWORD]@db.awpxetcrxvegsaenutzf.supabase.co:5432/postgres
   ```

2. Identify your project ref: `awpxetcrxvegsaenutzf` (the part after `db.` and before `.supabase.co`)

3. Identify your region from Supabase project settings (e.g., `ap-south-1` for Mumbai)

4. Construct the pooler URL:
   ```
   postgresql://postgres.awpxetcrxvegsaenutzf:[PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
   ```

### Option B: Try Port 6543 on Direct Host

Some Supabase configurations support pooling on port 6543 of the direct host:

```
postgresql://postgres:[PASSWORD]@db.awpxetcrxvegsaenutzf.supabase.co:6543/postgres
```

---

## ⚠️ Common Issues

**"I only see one connection string"**
- That's the direct connection (port 5432)
- Keep scrolling down for "Connection Pooling" section
- Or manually construct the pooler URL as shown above

**"Connection pooling is not enabled"**
- Click the toggle to enable it
- Select "Transaction" mode from dropdown
- The connection string will appear

**"Still getting network errors"**
- Make sure you copied the POOLER URL (port 6543), not direct URL (port 5432)
- Verify the password is correct in the URL
- Check that there are no extra spaces when pasting

---

## ✅ Next Steps

Once you have the **Connection Pooling URL**:

1. **Go to Render Dashboard**: https://dashboard.render.com
2. Click your service: `family-budget-tracker`
3. Click **"Environment"** tab
4. Find **`DATABASE_URL`** variable
5. Click **Edit** (pencil icon)
6. **Replace** the value with your **Pooler URL**
7. Click **"Save Changes"**
8. Wait for automatic redeploy (2-3 minutes)
9. Check logs for "✅ Connected to PostgreSQL"

---

## 🆘 Still Stuck?

If you still can't find it, share what you see in your Supabase Database settings page (just describe the section headings you see), and I'll help you locate it!

**Alternative**: Share your current DATABASE_URL format (you can hide the password with `***`), and I can tell you exactly how to convert it to the pooler URL.
