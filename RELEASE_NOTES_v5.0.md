# Release Notes - Version 5.0

**Release Date:** January 1, 2026  
**Release Name:** AI Chatbot Integration

## 🎉 Major New Feature: AI Budget Assistant

### Overview
Version 5.0 introduces an intelligent AI chatbot powered by Google Gemini 2.5 Flash that can answer questions about your budget data and help you use the application.

### Key Features

#### 🤖 AI-Powered Chatbot
- **Natural Language Queries:** Ask questions in plain English about your budget
  - "What is my total income?"
  - "How much did I spend on groceries?"
  - "How many members in my family?"
- **Smart Data Analysis:** Text-to-SQL engine converts questions to database queries
- **RAG System:** Retrieves answers from 22 documentation files for app usage help

#### 🔒 Security & Access Control
- **Role-Based Access:**
  - **Members:** Can only query their own data
  - **Admins:** Can query all family member data
  - **SuperAdmins:** Can query any household data
- **Read-Only Queries:** Chatbot cannot modify your data
- **SQL Injection Protection:** All queries validated before execution
- **Family Isolation:** Data restricted by household_id

#### 💬 User Interface
- **Location:** Main area expander (click to expand)
- **Chat History:** Maintains conversation context
- **Clear Chat:** Reset conversation anytime
- **Error Handling:** Graceful failures with helpful messages

### Technical Implementation

#### Components Added
1. **`chatbot_engine.py`** - Core AI logic
   - `LLMClient` - Google Gemini API wrapper
   - `DocumentRetriever` - RAG system for docs
   - `TextToSQLEngine` - Natural language to SQL
   - `ChatbotEngine` - Main orchestrator

2. **`chatbot_widget.py`** - UI components (deprecated)
3. **`chatbot_widget_simple.py`** - Simplified widget
4. **`chatbot_widget_debug.py`** - Debug version

5. **Database Integration:**
   - Added `MultiUserDB.execute_chatbot_query()` method
   - Safe query execution with validation

6. **Configuration:**
   - New settings in `config.py`
   - `GEMINI_API_KEY` environment variable

#### Dependencies
- **Added:** `google-generativeai>=0.3.0`
- **Requires:** Valid Gemini API Key from Google AI Studio

### Setup Instructions

#### 1. Get API Key
1. Visit https://makersuite.google.com/app/apikey
2. Click "Get API Key"
3. Copy your key

#### 2. Configure Environment
**On Render:**
1. Dashboard → Your Service → Environment
2. Add variable: `GEMINI_API_KEY`
3. Value: Your API key
4. Manual Deploy → Clear build cache & deploy

**Locally:**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

#### 3. Use the Chatbot
1. Login to the app
2. Look for "🤖 Budget Assistant Chatbot"
3. Click to expand
4. Ask your questions!

### Known Issues & Limitations

1. **Sidebar Issue:**
   - Chatbot appears in main area expander (not sidebar)
   - Sidebar visibility issue - workaround implemented

2. **Model Compatibility:**
   - Uses `gemini-2.5-flash` (2026 current model)
   - Older model names (1.5, Pro) not supported

3. **API Requirements:**
   - Requires internet connection
   - Free tier has rate limits
   - Some regions may have restrictions

### Breaking Changes
- None - fully backward compatible

### Migration Notes
If upgrading from v4.x:
1. Add `GEMINI_API_KEY` to environment variables
2. Redeploy with clean build cache
3. No database changes required

### Documentation
- `CHATBOT_SETUP_GUIDE.md` - Complete setup guide
- `CHATBOT_TROUBLESHOOTING.md` - Debug help
- `SETUP_API_KEY_RENDER.md` - Render configuration
- `walkthrough.md` - Implementation details

### Credits
- **AI Model:** Google Gemini 2.5 Flash
- **Framework:** Streamlit
- **Database:** PostgreSQL / SQLite

---

## Previous Versions

### v4.0 - Multi-User & Deployment
- PostgreSQL support
- Render deployment
- Family/household management

### v3.0 - Expense Subcategories
- Subcategory field added
- Enhanced categorization

### v2.1 - Super Admin Features
- Admin dashboard
- Member promotion
- Family management

### v2.0 - Launch Page Redesign
- New navigation UI
- Password setup flow

### v1.0 - Initial Release
- Basic budget tracking
- SQLite database
- Single user mode

---

**To rollback to v5.0 later:**
```bash
git checkout v5.0
git checkout -b rollback-to-v5
git push origin rollback-to-v5
```
