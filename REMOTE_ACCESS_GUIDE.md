# Remote Access Setup Guide

## ✅ Password Setup Page Added!

The app now has a **3rd tab** called "🔑 Setup Password (Members)" where invited members can:
1. Paste their invite token
2. Set their own password
3. Then login normally

---

## 🌐 Remote Access Options

### Option 1: Same WiFi Network (Easiest)
If your family members are on the **same WiFi** as you:

**Share this link:** `http://10.0.0.4:8505`

This works for anyone connected to your home WiFi.

---

### Option 2: Remote Access via ngrok (Internet Access)

For family members **NOT on your WiFi** (different locations), use ngrok:

#### Step 1: Install ngrok
```bash
py -m pip install pyngrok
```

#### Step 2: Sign up for ngrok (Free)
1. Go to https://ngrok.com/
2. Sign up for a free account
3. Get your auth token from the dashboard

#### Step 3: Set up ngrok auth token
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

#### Step 4: Create tunnel (in a NEW terminal)
```bash
ngrok http 8505
```

This will give you a **public URL** like:
```
https://abc123.ngrok.io
```

#### Step 5: Share the ngrok URL
Send the `https://abc123.ngrok.io` link to your family members - they can access from anywhere!

---

## 📋 Complete Member Onboarding Process

### For Admin:
1. Add member in "Manage Members" tab
2. **Copy the invite token** from the success message
3. Share with member:
   - **Link**: `http://10.0.0.4:8505` (same WiFi) OR `https://abc123.ngrok.io` (remote)
   - **Invite Token**: The long string from step 2
   - **Email**: The email you entered

### For Member:
1. Open the shared link
2. Go to "🔑 Setup Password (Members)" tab
3. Paste invite token
4. Set password (min 6 characters)
5. Click "Set Password"
6. Go to "🔐 Login" tab
7. Login with email + new password

---

## 🔒 Security Notes

- ngrok free tier URLs change each time you restart
- For permanent URLs, upgrade to ngrok paid plan
- ngrok tunnels expire after 2 hours on free tier
- Always use strong passwords (6+ characters)

---

## 🆘 Troubleshooting

**"Link not working" from different location:**
- Make sure you're using the ngrok URL, not localhost
- Verify ngrok tunnel is still running
- Check if your application is still running

**"Invite token invalid":**
- Make sure token was copied completely
- Token is case-sensitive
- Each token can only be used once

**ngrok command not found:**
- Run: `py -m pip install pyngrok`
- Then try again

---

## Quick Commands Reference

```bash
# Start the app (Terminal 1)
cd Personal_Budget_Tracker_Commercial_Version
py -m streamlit run family_expense_tracker.py

# Start ngrok tunnel (Terminal 2 - for remote access)
ngrok http 8505
```

---

Enjoy your **multi-user family budget tracker** with remote access! 🎉
