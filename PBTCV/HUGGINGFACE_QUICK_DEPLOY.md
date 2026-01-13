# Updated Hugging Face Deployment (Using Docker)

## ✅ Quick Steps

### 1. Select SDK: **Docker**

### 2. Create Space
- Space name: `family-budget-tracker`  
- License: MIT
- SDK: **Docker**
- Click "Create Space"

### 3. Upload Files

Upload these files to your Space (click "Files" → "Add file" → "Upload files"):
- `Dockerfile` (created - see your project folder)
- `family_expense_tracker.py`
- `multi_user_database.py`
- `config.py`
- `requirements.txt`

### 4. Commit & Deploy
- Click "Commit changes to main"
- Wait 3-5 minutes for build
- Your app will be live!

## 🔗 Your URL
`https://huggingface.co/spaces/YOUR_USERNAME/family-budget-tracker`

---

**Alternative: Push Dockerfile to GitHub then import**

```bash
cd PBTCV
git add Dockerfile
git commit -m "Add Dockerfile for Hugging Face"
git push
```

Then in Hugging Face:
- Settings → Import from GitHub repository

Much easier! 🚀
