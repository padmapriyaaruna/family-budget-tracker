# Version 2.1 Release Notes

**Release Date:** December 29, 2025  
**Tag:** v2.1  
**Status:** ✅ Stable

## 🎉 Major Features

### Landing Page Redesign
- **Complete redesign** from tabbed interface to modern landing page
- **4 role-based navigation buttons** for intuitive access
  - 🔱 Master (Superadmin)
  - 👨‍👩‍👧 Family Admin
  - 👤 Family Member
  - 🔑 Member Password Setup
- **Flexbox-based responsive header** with gradient background
- **Professional first impression** with polished UI

### Master Login Simplification
- **Password-only login** for superadmin (no username field)
- Username automatically set to `'superadmin'` in backend
- Streamlined authentication for system administrators

### UI/UX Enhancements
- **Beautiful gradient header** - Purple to blue gradient (135deg: #667eea to #764ba2)
- **Centered logo and title** using CSS flexbox
- **White text** for high contrast
- **Rounded bottom corners** on header bar
- **Box shadow** for depth and dimension
- **Hidden default Streamlit header** - No empty blue boxes
- **Improved back button visibility** with proper spacing

## 🔧 Technical Improvements

### Navigation System
- Session state-based page routing (`st.session_state.login_page`)
- Clean separation between landing page and login screens
- Back buttons on all login pages to return to landing

### CSS & Styling
- Flexbox implementation (`display: flex; align-items: center`)
- Responsive design with media queries for mobile devices
- Custom HTML/CSS for landing page header
- Maintained existing CSS for table styling

### Code Organization
- Separated login functions:
  - `show_landing_page()` - Main landing with buttons
  - `show_master_login()` - Password-only superadmin
  - `show_admin_login()` - Family admin email + password
  - `show_member_login()` - Member email + password
  - `show_password_setup()` - Token-based setup

## 📋 Changes from v2.0

### Added
- ✅ Landing page with 4 navigation buttons
- ✅ Flexbox header design
- ✅ Master password-only login
- ✅ Session state navigation routing
- ✅ Gradient header bar styling
- ✅ Back navigation buttons

### Modified
- ♻️ Replaced tabbed interface completely
- ♻️ Superadmin login simplified
- ♻️ Header styling overhauled

### Removed
- ❌ Tabbed login interface
- ❌ Username field from Master login
- ❌ Default Streamlit header/toolbar

## 🔄 Migration from v2.0

No database changes or data migration required. Simply:
1. Pull latest code
2. Redeploy application
3. New landing page will appear automatically

## 📦 Rollback Instructions

To rollback to v2.0 (Excel-like tables without landing page):
```bash
git checkout v2.0
git push origin main --force
```

To rollback to v1.0 (original stable baseline):
```bash
git checkout v1.0
git push origin main --force
```

## 🎨 Design Details

### Landing Page Header
- **Layout:** Horizontal flexbox with logo left, text right
- **Colors:** White text on purple gradient (#667eea to #764ba2)
- **Typography:** 2.2rem for title, 1rem for subtitle
- **Spacing:** 1.5rem padding, 1rem gap between elements
- **Effects:** Box shadow (0 4px 6px rgba(0,0,0,0.1))

### Button Styling
- **Width:** Full container width
- **Spacing:** Centered in middle column (1:2:1 ratio)
- **Labels:** Icon + descriptive text for each role

## 🐛 Bug Fixes

None - This is a pure feature/redesign release building on v2.0's stability.

## 🚀 What's Next (Future Versions)

Potential features for v3.0:
- User profile pictures/avatars
- Remember me functionality
- Password reset flow
- Multi-language support
- Dark mode toggle

---

**Developed by:** Antigravity AI  
**Repository:** https://github.com/padmapriyaaruna/family-budget-tracker  
**Previous Version:** v2.0 (Excel-like Inline Editing)  
**License:** MIT
