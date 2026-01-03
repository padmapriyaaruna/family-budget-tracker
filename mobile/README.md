# Family Budget Tracker - Mobile App

React Native mobile application for the Family Budget Tracker system.

## Overview

This is the mobile companion app for the Family Budget Tracker web application. It provides iOS and Android native apps that connect to the same backend API and PostgreSQL database.

## Tech Stack

- **Framework**: React Native 0.73
- **Navigation**: React Navigation 6
- **State Management**: React Context API
- **API Client**: Axios
- **Storage**: AsyncStorage
- **Icons**: React Native Vector Icons
- **Charts**: React Native Charts Wrapper

## Project Structure

```
mobile/
├── android/                 # Android native code
├── ios/                     # iOS native code
├── src/
│   ├── components/         # Reusable UI components
│   ├── screens/           # App screens
│   │   ├── LoginScreen.js
│   │   ├── IncomeScreen.js
│   │   ├── AllocationsScreen.js
│   │   ├── ExpensesScreen.js
│   │   ├── ReviewScreen.js
│   │   └── ChatbotScreen.js
│   ├── navigation/        # Navigation configuration
│   │   └── Navigation.js
│   ├── services/          # API and business logic
│   │   └── api.js
│   ├── utils/             # Helper functions
│   └── assets/            # Images, fonts, etc.
├── App.js                 # Root component
└── package.json           # Dependencies

```

## Prerequisites

- Node.js >= 18
- React Native CLI
- Android Studio (for Android development)
- Xcode (for iOS development, macOS only)

## Installation

### 1. Install Dependencies

```bash
cd mobile
npm install
```

### 2. iOS Setup (macOS only)

```bash
cd ios
pod install
cd ..
```

### 3. Configure API URL

Edit `src/services/api.js` and update the API_BASE_URL:

```javascript
const API_BASE_URL = __DEV__ 
  ? 'http://YOUR_LOCAL_IP:8000'  // Development
  : 'https://your-api-url.com';  // Production
```

## Running the App

### Android

```bash
npm run android
```

### iOS

```bash
npm run ios
```

### Start Metro Bundler

```bash
npm start
```

## Backend API Setup

The mobile app requires a REST API backend. You'll need to create API endpoints that mirror the database operations in `multi_user_database.py`.

### Option 1: FastAPI Backend

Create `backend/api.py` in the parent directory:

```python
from fastapi import FastAPI, Depends, HTTPException
from multi_user_database import MultiUserDB

app = FastAPI()
db = MultiUserDB()

@app.post("/auth/login")
async def login(email: str, password: str):
    user = db.authenticate_user(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"user": user, "token": "generate_jwt_token_here"}

# Add more endpoints...
```

Run with:
```bash
pip install fastapi uvicorn
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Flask Backend

Similar approach using Flask/Flask-RESTful.

## Development Guide

### Creating a New Screen

1. Create file in `src/screens/YourScreen.js`
2. Add navigation route in `src/navigation/Navigation.js`
3. Connect to API in `src/services/api.js`

### API Integration

All API calls are centralized in `src/services/api.js`. Use the provided methods:

```javascript
import {incomeAPI} from './services/api';

// In your component
const fetchIncome = async () => {
  try {
    const response = await incomeAPI.getIncome(userId, year, month);
    setIncomeData(response.data);
  } catch (error) {
    console.error('Error fetching income:', error);
  }
};
```

## Features

- [ ] User authentication (login, password setup)
- [ ] Income management
- [ ] Budget allocations
- [ ] Expense tracking with subcategories
- [ ] Financial review dashboard
- [ ] AI chatbot integration
- [ ] Charts and visualizations
- [ ] Offline mode with sync
- [ ] Push notifications for budget alerts

## Shared with Web App

Both mobile and web apps use:
- Same PostgreSQL database
- Same authentication system
- Same business logic (via API)
- Same AI chatbot engine

## Testing

```bash
npm test
```

## Building for Production

### Android

```bash
cd android
./gradlew assembleRelease
```

Output: `android/app/build/outputs/apk/release/app-release.apk`

### iOS

1. Open `ios/FamilyBudgetTracker.xcworkspace` in Xcode
2. Select Product > Archive
3. Follow App Store submission process

## Troubleshooting

### Metro Bundler Issues

```bash
npm start -- --reset-cache
```

### Android Build Errors

```bash
cd android
./gradlew clean
cd ..
```

### iOS Pod Issues

```bash
cd ios
pod deintegrate
pod install
cd ..
```

## Contributing

1. Create a feature branch
2. Make changes
3. Test on both iOS and Android
4. Submit pull request

## License

Same as parent project

## Support

For issues, see the main project README or create an issue on GitHub.

---

**Note**: This mobile app is currently in initial setup phase. Screens and features will be implemented incrementally.
