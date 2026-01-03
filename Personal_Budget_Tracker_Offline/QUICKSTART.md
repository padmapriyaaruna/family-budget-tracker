# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Set Up Google Sheets (One-time setup)
1. **Create Google Cloud Project**: [console.cloud.google.com](https://console.cloud.google.com)
2. **Enable Google Sheets API**: Search in API Library and enable it
3. **Create Service Account**: APIs & Services → Credentials → Create Service Account
4. **Download JSON**: Create key for service account, download as `credentials.json`
5. **Create Google Sheet**: Name it `Expense_Tracker`
6. **Share Sheet**: Share with service account email (from JSON) as Editor

### Step 3: Run the App
```bash
streamlit run expense_tracker.py
```

✅ That's it! The app will open at http://localhost:8501

## 📱 Access from Mobile

### Option 1: Same WiFi Network
- Find your computer's IP address
- On mobile, open: `http://YOUR-IP:8501`

### Option 2: Deploy to Cloud (Recommended)
- Push code to GitHub
- Deploy on [share.streamlit.io](https://share.streamlit.io) (free)
- Access from anywhere via URL

## 🔧 Troubleshooting

**Can't connect to Google Sheets?**
- Check `credentials.json` is in the project folder
- Verify Google Sheet is shared with service account email
- Make sure Sheets API is enabled

**Module not found?**
```bash
pip install -r requirements.txt
```

For detailed instructions, see [README.md](README.md)
