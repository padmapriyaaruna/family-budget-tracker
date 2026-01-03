# 💰 Personal Expense Tracker - Offline First

A Python-based personal expense tracker that **works completely offline** using SQLite. Track your income, fixed allocations, and daily expenses in INR (₹) with automatic balance calculations.

## ✨ Features

- ✅ **100% Offline** - No internet required, all data stored locally  
- ✅ **SQLite Database** - Fast, reliable local storage  
- ✅ **Income Tracking** - Log income with date, source, and amount  
- ✅ **Budget Allocations** - Create categories and track spending  
- ✅ **Expense Logging** - Auto-updates allocation balances  
- ✅ **Visual Dashboard** - Charts and analytics  
- ✅ **Mobile Responsive** - Works on phone and laptop browsers  

## 🚀 Quick Start

### 1. Install Dependencies
```bash
py -m pip install streamlit pandas plotly
```

### 2. Run the App
```bash
py -m streamlit run expense_tracker.py
```

### 3. Open in Browser
The app will automatically open at: **http://localhost:8501**

That's it! No Google Sheets setup needed!

## 📱 How to Use

### On Your Laptop
1. Run the command: `py -m streamlit run expense_tracker.py`
2. Open browser to `http://localhost:8501`
3. Add income, allocations, and expenses

### On Your Mobile (Same WiFi)
1. Keep the app running on your laptop
2. On mobile browser, go to: **http://YOUR-LAPTOP-IP:8501**
   - Find your laptop's IP from the terminal output (Network URL)
   - Example: `http://10.0.0.4:8501`
3. Use the app on mobile!

### Data Storage
- All data is saved in `expense_tracker.db` file
- This file is created automatically
- Your data persists between sessions
- **Backup tip**: Copy this file to backup your data

## 📊 Features Breakdown

### Dashboard Tab
- View total income, allocated, spent, and remaining liquidity
- Visual pie chart of allocations
- Bar chart comparing spent vs. allocated
- Recent expenses table

### Income Tab
- Add income entries (Date, Source, Amount)
- View total liquidity
- See complete income history

### Allocations Tab
- Create budget categories (Stock, MF, House, Travel, etc.)
- Set allocated amounts
- Edit existing allocations
- Delete categories
- **Auto-calculation**: Balance = Allocated - Spent

### Expenses Tab
- Log daily expenses
- Select category from dropdown
- Add amount and comment
- **Auto-magic**: Allocation balance updates instantly!
- View expense history
- Category-wise breakdown chart

## 💾 Data Syncing Between Devices

Currently, the app uses **local SQLite** on each device. To sync between laptop and mobile:

### Option 1: Shared Network Access (Easiest)
- Run the app on your laptop
- Access from mobile using Network URL (same WiFi required)
- Both devices see the same data because they're accessing the same app instance

### Option 2: Manual File Sync
- Copy the `expense_tracker.db` file between devices
- Use Google Drive, USB, or any file transfer method
- Replace the db file on the other device

### Option 3: Cloud Sync (Future Enhancement)
- Google Sheets sync can be added later
- Would allow automatic sync when online
- Not required for basic usage

## 🛠️ Project Structure

```
AntiGravity_Projects/
├── expense_tracker.py      # Main Streamlit application
├── database.py            # SQLite database layer
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── expense_tracker.db    # Your data (auto-created)
└── README.md            # This file
```

## 🔧 Troubleshooting

### App won't start
- Make sure you installed dependencies: `py -m pip install streamlit pandas plotly`
- Check if the port 8501 is available
- Try: `py -m streamlit run expense_tracker.py --server.port 8502`

### Can't access from mobile
- Ensure mobile and laptop are on the same WiFi network
- Use the Network URL shown in terminal (not localhost)
- Check if firewall is blocking the port

### Data not saving
- Check if `expense_tracker.db` file exists in project folder
- Ensure you have write permissions in the directory
- Look for error messages in the terminal

### Reset all data
- Close the app
- Delete `expense_tracker.db` file
- Restart the app (creates fresh database)

## 💡 Tips

- **Mobile Access**: Bookmark the Network URL on your phone for quick access
- **Backup**: Regularly copy `expense_tracker.db` to a safe location
- **Categories**: Start with 3-4 main categories, add more as needed
- **Comments**: Use descriptive comments for expenses to track where money goes
- **Daily Logging**: Add expenses daily for accurate tracking

## ⚙️ Configuration

Edit `config.py` to customize:
- `DATABASE_PATH` - Location of SQLite database file
- `CURRENCY_SYMBOL` - Currency symbol (default: ₹)
- `DATE_FORMAT` - Date format for entries

## 🔐 Privacy

- All data stored locally on your device  
- No cloud uploads required  
- No tracking or analytics  
- You have full control of your data  

## 📈 Future Enhancements

- [ ] Google Sheets sync (optional)
- [ ] Export to Excel/CSV
- [ ] Monthly reports
- [ ] Budget alerts
- [ ] Multi-currency support
- [ ] Dark/Light theme toggle

---

**Built with ❤️ using Python, Streamlit, and SQLite**

For questions, check the troubleshooting section above!
