# Budget Tracker Suite

This repository contains two versions of budget tracking applications:

## 📊 Projects

### 1. [Personal Budget Tracker - Commercial Version](./Personal_Budget_Tracker_Commercial_Version/)

Full-featured family budget tracker with multi-user support, mobile apps, and cloud deployment options.

**Features:**
- Multi-user family budget management
- Super Admin dashboard
- Income, Allocation, and Expense tracking
- Mobile apps (React Native)
- PostgreSQL/SQLite database support
- Cloud deployment ready (Render, Streamlit Cloud, Hugging Face)
- AI Chatbot integration

**Quick Start:**
```powershell
cd Personal_Budget_Tracker_Commercial_Version
pip install -r requirements.txt
streamlit run family_expense_tracker.py
```

📖 [View Full Documentation](./Personal_Budget_Tracker_Commercial_Version/README.md)

---

### 2. [Personal Budget Tracker - Offline Version](./Personal_Budget_Tracker_Offline/)

Simplified offline expense tracker for personal use.

**Features:**
- Single-user expense tracking
- Offline-first (SQLite)
- Income and expense management
- Simple dashboard
- Optional Google Sheets sync

**Quick Start:**
```powershell
cd Personal_Budget_Tracker_Offline
pip install -r requirements.txt
streamlit run expense_tracker.py
```

📖 [View Documentation](./Personal_Budget_Tracker_Offline/README.md)

---

## 🚀 Getting Started

1. **Clone the repository**
   ```powershell
   git clone https://github.com/padmapriyaaruna/family-budget-tracker.git
   cd family-budget-tracker
   ```

2. **Choose your version** and navigate to its directory

3. **Install dependencies** using the `requirements.txt` in that directory

4. **Run the application** following the Quick Start guide above

## 📝 Version History

- **v5.0+**: Reorganized into Commercial and Offline versions
- **v2.1**: Added subcategories and mobile deployment
- **v2.0**: PostgreSQL migration and multi-user features
- **v1.0**: Initial release with SQLite

## 🤝 Contributing

For questions or issues, please open an issue on GitHub.

## 📄 License

See individual project directories for licensing information.
