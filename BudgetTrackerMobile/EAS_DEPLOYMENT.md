# EAS Update Setup Guide (Modern Expo Deployment)

## 🎯 Goal
Deploy your app using EAS (Expo Application Services) - the modern replacement for `expo publish`

---

## ✅ **One-Time Setup**

### Step 1: Install EAS CLI
```bash
npm install -g eas-cli
```

### Step 2: Login
```bash
cd BudgetTrackerMobile
eas login
```
Enter your Expo account credentials (create one at expo.dev if needed)

### Step 3: Configure EAS
```bash
# Configure updates
eas update:configure

# Configure builds
eas build:configure
```

When prompted:
- Platform: **All** (Android + iOS)
- Accept the default `eas.json` configuration

---

## 📱 **Deployment Options**

### **Option 1: Development Build (RECOMMENDED)**

This creates an APK that can receive over-the-air updates!

#### Initial Build (One-time):
```bash
# Build development APK
eas build --profile development --platform android
```

This takes 10-15 minutes. You'll get a download link for the APK.

#### Share APK:
1. Download the APK from the link
2. Share with users via Google Drive/WhatsApp/Email
3. Users install it once

#### Push Updates (Unlimited times):
```bash
# Make your code changes
# Then push update:
eas update --branch development --message "Added new features"
```

✅ **Users get the update automatically** next time they open the app!

---

### **Option 2: Preview Build (For Testing)**

```bash
# Build preview APK
eas build --profile preview --platform android
```

Then update:
```bash
eas update --branch production --message "Bug fixes"
```

---

## 🔄 **Typical Update Workflow**

```bash
# 1. Make code changes
# Edit files in BudgetTrackerMobile/src/...

# 2. Test locally
npx expo start

# 3. Push update to cloud
eas update --branch development --message "Your update description"

# 4. Users automatically get it!
# No action needed from users
```

---

## 💰 **Cost Breakdown**

**FREE Tier:**
- 30 builds per month
- Unlimited updates
- Perfect for development

**Paid ($29/month):**
- Unlimited builds
- Faster build times
- Priority support

**For you:** Start with FREE tier!

---

## 📊 **Comparison: Old vs New**

| Feature | Old (expo publish) | New (EAS) |
|---------|-------------------|-----------|
| Command | `expo publish` | `eas update` |
| User Access | Expo Go only | Real APK |
| Updates | Automatic | Automatic |
| Cost | Free | Free tier available |
| Professional | No | Yes |

---

## 🚀 **Quick Start (15 Minutes)**

```bash
# 1. Install EAS
npm install -g eas-cli

# 2. Navigate to project
cd BudgetTrackerMobile

# 3. Login
eas login

# 4. Configure
eas build:configure
eas update:configure

# 5. Build development APK (First time - 15 min)
eas build --profile development --platform android

# 6. Download APK and share with users

# 7. Later, push updates (30 seconds)
eas update --branch development --message "New features"
```

---

## 🎁 **Alternative: Expo Go (Quick Demo)**

If you just want to demo quickly without building:

1. Start dev server:
   ```bash
   npx expo start
   ```

2. Users scan QR code with Expo Go app

**Limitation:** You need to keep laptop running OR build a proper APK

---

## 🆘 **Troubleshooting**

**"eas: command not found"**
```bash
npm install -g eas-cli
```

**"Not authorized"**
```bash
eas login
# Enter your expo.dev credentials
```

**"Build failed"**
- Check app.json has "owner" field
- Make sure dependencies are installed
- Try: `npm install` then rebuild

---

## 📞 **Recommended Approach**

**For Development/Testing:**
```bash
# One-time build
eas build --profile development --platform android

# Unlimited updates
eas update --branch development
```

**For Production/Clients:**
```bash
# Production build
eas build --profile production --platform android

# Updates
eas update --branch production
```

---

## 💡 **Summary**

✅ **FREE** for up to 30 builds/month  
✅ **Unlimited updates** for free  
✅ **Real APK** that users install  
✅ **Over-the-air updates** - users auto-update  
✅ **No laptop needed** after initial build  

**Next Steps:**
1. Run the Quick Start commands above
2. Build your development APK (one-time, 15 min)
3. Share APK with users
4. Update anytime with `eas update`!
