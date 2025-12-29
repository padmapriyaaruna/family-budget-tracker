# 🎯 Fix Supabase Pooler Username Format

## ✅ Great Progress!
The error changed from "Network unreachable" to "Tenant or user not found" - this means the **connection is working**! We just need to fix the username format.

---

## The Issue

For Supabase connection pooler, the username format is **different** from direct connections:

❌ **Wrong (Direct connection format):**
```
postgresql://postgres:[PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
```

✅ **Correct (Pooler format):**
```
postgresql://postgres.PROJECT_REF:[PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
```

**Notice:** Username changes from `postgres` to `postgres.PROJECT_REF`

---

## 🔧 How to Fix Your DATABASE_URL

### Step 1: Find Your Project Reference ID

Your project ref is visible in the error - it's the part that identifies your project.

From your original direct connection URL:
```
postgresql://postgres:[PASSWORD]@db.awpxetcrxvegsaenutzf.supabase.co:5432/postgres
                                      ^^^^^^^^^^^^^^^^^^^
                                      This is your PROJECT_REF
```

In your case: `awpxetcrxvegsaenutzf`

### Step 2: Update Your DATABASE_URL

Your **correct pooler DATABASE_URL** should be:

```
postgresql://postgres.awpxetcrxvegsaenutzf:[YOUR_PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
```

**Key changes:**
- Username: `postgres` → `postgres.awpxetcrxvegsaenutzf`
- Host: `aws-0-ap-south-1.pooler.supabase.com`
- Port: `6543`

### Step 3: Update in Render

1. Go to **Render Dashboard**: https://dashboard.render.com
2. Click your service
3. Go to **Environment** tab
4. Edit **`DATABASE_URL`**
5. Paste the corrected URL with format: `postgres.awpxetcrxvegsaenutzf`
6. **Save Changes**
7. Wait for automatic redeploy

---

## 📋 Quick Checklist

- [ ] Username includes project ref: `postgres.PROJECT_REF`
- [ ] Host is pooler: `aws-0-ap-south-1.pooler.supabase.com`
- [ ] Port is 6543
- [ ] Password is correct (no spaces)
- [ ] Database name is `postgres`

---

## ⚡ Alternative: Get It From Supabase Directly

If you want to get the exact string from Supabase:

1. Go to **Supabase Dashboard** → Your Project
2. **Settings** → **Database**
3. Scroll to **"Connection Pooling"** section
4. Make sure **Mode** is set to **"Transaction"**
5. The connection string shown there has the **correct username format**
6. Just copy it directly!

---

## 🆘 Still Having Issues?

Share your DATABASE_URL format (hide password with `***`), and I'll verify it's correct!

Expected format:
```
postgresql://postgres.awpxetcrxvegsaenutzf:***@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
```
