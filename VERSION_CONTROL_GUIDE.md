# Version Control & Rollback Guide

## Current Version: 1.0 ✅

**Status:** Stable working version with all PostgreSQL features functional

**Tag:** `v1.0`  
**Commit:** `2dae008` (latest)

---

## Rolling Back to Version 1.0

### Option 1: Rollback Local Code (Keep Testing Changes)

```bash
# View all tags
git tag

# Create a new branch from v1.0 (recommended)
git checkout -b rollback-v1.0 v1.0

# Or directly checkout v1.0 (detached HEAD state)
git checkout v1.0
```

### Option 2: Hard Reset to v1.0 (Discard All Changes)

⚠️ **WARNING:** This will DELETE all uncommitted changes!

```bash
# Reset to v1.0 and discard everything after
git reset --hard v1.0

# Force push to GitHub (if needed)
git push origin main --force
```

### Option 3: Revert to v1.0 While Keeping History

```bash
# Create a new commit that undoes changes back to v1.0
git revert --no-commit v1.0..HEAD
git commit -m "Revert to version 1.0"
git push origin main
```

---

## Deploying v1.0 on Render

After rolling back locally:

1. **Push to GitHub** (if using Option 1 or 3):
   ```bash
   git push origin main
   ```

2. **Render will auto-deploy** the v1.0 code

**Manual Deploy:**
- Go to Render Dashboard → Your service
- Click "Manual Deploy" → Select `v1.0` tag or commit `2dae008`

---

## Checking Current Version

```bash
# Show current commit
git log -1 --oneline

# Show all tags
git tag -l

# Show tag details
git show v1.0
```

---

## Future Development Workflow

### Safe Development Process:

1. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and test**

3. **If it works - merge to main:**
   ```bash
   git checkout main
   git merge feature/your-feature-name
   git push origin main
   ```

4. **If something breaks - rollback to v1.0** using methods above

5. **Create new version tag when stable:**
   ```bash
   git tag -a v1.1 -m "Description of changes"
   git push origin v1.1
   ```

---

## Database Rollback

**Important:** Git only controls code, not database.

If you need to restore database state:
1. **Neon PostgreSQL** has automatic backups
2. Go to **Neon Dashboard** → Your database → **Restore** tab
3. Select restore point from when v1.0 was working

---

## Quick Reference

| Action | Command |
|--------|---------|
| Create new tag | `git tag -a v1.1 -m "message"` |
| Push tag | `git push origin v1.1` |
| List tags | `git tag -l` |
| Checkout tag | `git checkout v1.0` |
| Delete tag locally | `git tag -d v1.0` |
| Delete tag remote | `git push origin --delete v1.0` |

---

## Your v1.0 Includes

✅ PostgreSQL migration complete  
✅ All authentication working  
✅ Income/Expense/Allocation CRUD  
✅ Member management  
✅ Super admin & family admin features  
✅ Stable database connections  
✅ No SQL syntax errors
