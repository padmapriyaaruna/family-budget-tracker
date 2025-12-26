# Family Budget Tracker - Multi-User Version

## 🎉 What's New

This is the **Commercial Multi-User Version** of the Personal Expense Tracker, designed for families where multiple members track their finances.

### Key Features
- 👨‍👩‍👧‍👦 **Multi-user support** - Admin + family members
- 🔐 **Secure authentication** - Password-protected accounts
- 👑 **Admin dashboard** - View entire family's finances
- 🔒 **Data privacy** - Members see only their own data
- 💰 **Individual tracking** - Each member manages their own budget
- 📊 **Family overview** - Consolidated household financial reports

## 🚀 Quick Start

### 1. Install Dependencies
```bash
py -m pip install streamlit pandas plotly
```

### 2. Launch the Application
```bash
py -m streamlit run family_expense_tracker.py
```

### 3. Create Admin Account
1. Go to the "Create Admin Account" tab
2. Enter your household name and details
3. Create your admin account

### 4. Login
Use your email and password to log in

### 5. Add Family Members (Admin Only)
1. Go to "Manage Members" tab
2. Add family members with their email and relationship
3. Share the generated invite token with them

## 📖 User Roles

### Admin
- View entire household financial summary
- Add/remove family members
- Generate invite links for new members
- Track their own personal expenses
- See member-wise breakdown of income/expenses

### Members
-  Track personal income and expenses
- Create budget allocations
- Log daily expenses
- View personal financial dashboard
- **Cannot** see other members' data

## 💡 How It Works

### For Admins

1. **Family Overview Tab**
   - See total household income, expenses, and savings
   - View member-wise financial breakdown
   - Visualize family contributions

2. **Manage Members Tab**
   - Add new family members
   - View all household members
   - Generate invite tokens

3. **My Expenses Tab**
   - Track your personal finances
   - Same features as member dashboard

### For Members

1. **Dashboard**: Overview of personal finances
2. **Income**: Track salary, bonuses, etc.
3. **Allocations**: Set budget categories (Groceries, Rent, etc.)
4. **Expenses**: Log daily spending

## 🔐 Security Features

- Password hashing (SHA-256)
- Session-based authentication
- Role-based access control
- User activation/deactivation
- Invite token system

## 📁 Database Structure

- **households**: Family groupings
- **users**: Admin + member accounts
- **income**: Per-user income tracking
- **allocations**: Per-user budget categories
- **expenses**: Per-user expense logging
- **monthly_settlements**: Per-user month closures

## 🛠️ Technical Stack

- **Frontend**: Streamlit
- **Database**: SQLite (offline-first)
- **Visualization**: Plotly
- **Authentication**: Password hashing with SHA-256

## ⚠️ Important Notes

1. **Invite System**: Currently generates tokens for members to set passwords. For production use, integrate email sending via SMTP.

2. **Password Security**: Uses SHA-256 hashing. For production, consider bcrypt or Argon2.

3. **Data Isolation**: Members cannot access other members' financial data. Only admins have full visibility.

4. **Offline First**: All data stored locally in SQLite. No internet required.

## 🔄 Workflow Example

1. **John (Admin)** creates household "Smith Family"
2. **John** adds wife **Sarah** with email sarah@example.com
3. System generates invite token: `abc123xyz...`
4. **John** shares token with **Sarah**
5. **Sarah** uses token to set password (future feature)
6. **Sarah** logs in and tracks her expenses
7. **John** views family overview showing both their finances

## 📊 Admin Dashboard Features

- Family financial summary
- Member-wise income/expense tracking
- Visual charts showing contributions
 - Add/manage family members

- Personal expense tracking

## 🔜 Future Enhancements

-  Email invitation system
- Password reset functionality
- Export family reports to PDF/Excel
- Monthly settlement for members
- Budget goals and alerts
- Category sharing between members
- Mobile-responsive design improvements

## 🆘 Troubleshooting

**Can't login?**
- Verify email and password are correct
- Ensure account was created successfully

**Member can't access?**
- Verify invite token was shared correctly
- Check member hasn't been deactivated

**Data not showing?**
- Click refresh or reload the page
- Ensure you're logged into correct account

## 📝 Files

- `family_expense_tracker.py` - Main application
- `multi_user_database.py` - Database layer
- `config.py` - Configuration settings
- `family_budget.db` - SQLite database (auto-created)

## 🎯 Perfect For

- Families tracking joint finances
- Couples managing household budget
- Parents teaching kids financial responsibility
- Multi-income households
- Shared living situations

---

**Developed by**: AntiGravity AI  
**Version**: 1.0 (Multi-User Commercial)  
**License**: Personal Use
