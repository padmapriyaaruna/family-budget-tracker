# AI Chatbot Setup Guide

## Overview

The Family Budget Tracker now includes an AI-powered chatbot assistant that helps users with:
- **General Q&A**: How to use features, navigate the app
- **Data Analytics**: Natural language queries about expenses, income, and budgets
- **Role-Based Access**: Secure data access based on user permissions

## Prerequisites

### 1. Get a Google Gemini API Key

The chatbot uses Google's Gemini 1.5 Flash model (free tier with 15 requests/minute).

**Steps to get your API key:**

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

### 2. Set Environment Variable

The chatbot requires the API key to be set as an environment variable.

#### For Local Development (Windows):

```powershell
# Set for current session
$env:GEMINI_API_KEY="your-api-key-here"

# Set permanently (requires restart)
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'your-api-key-here', 'User')
```

#### For Local Development (Mac/Linux):

```bash
# Add to ~/.bashrc or ~/.zshrc
export GEMINI_API_KEY="your-api-key-here"

# Then reload:
source ~/.bashrc  # or source ~/.zshrc
```

#### For Deployment (Render.com):

1. Go to your Render dashboard
2. Select your web service
3. Navigate to "Environment"
4. Add new environment variable:
   - **Key**: `GEMINI_API_KEY`
   - **Value**: your-api-key-here
5. Click "Save Changes"

#### For Deployment (Hugging Face Spaces):

1. Go to your Space settings
2. Click on "Variables and secrets"
3. Add new secret:
   - **Name**: `GEMINI_API_KEY`
   - **Value**: your-api-key-here

## Installation

1. **Install dependencies:**

```bash
pip install google-generativeai>=0.3.0
```

(This is already included in `requirements.txt`)

2. **Verify installation:**

```bash
python -c "import google.generativeai as genai; print('✅ Gemini SDK installed successfully')"
```

## How to Use the Chatbot

### 1. Login to the Application

The chatbot is only available AFTER logging in (hidden on login pages).

### 2. Open the Chatbot

Click the **"🤖 Budget Assistant"** button in the sidebar.

### 3. Ask Questions

**Example Questions:**

#### General Q&A:
- "How do I add a new expense?"
- "How do I create a budget allocation?"
- "What is the difference between allocated and spent amounts?"

#### Data Analytics (Member Role):
- "How much have I spent this month?"
- "How much did I spend on groceries?"
- "Show my total income for December 2025"
- "How much have I spent on Food - Online?"

#### Data Analytics (Admin Role):
- "What's the total family spending this month?"
- "How much has the family spent on groceries this year?"
- "What's our family's total income?"

### 4. Understanding Responses

- **✅ Success**: Chatbot provides clear, conversational answers
- **⚠️ Access Denied**: You're trying to access data you don't have permission for
- **❌ Error**: Check API key configuration or network connection

## Security & Privacy

### Role-Based Access Control

The chatbot enforces strict data isolation:

1. **Super Admin**: Can view all household data
2. **Family Admin**: Can view all family member data within their household
3. **Family Member**: Can ONLY view their own personal data

### What the Chatbot CANNOT Do:

- ❌ Modify, delete, or create data (read-only access)
- ❌ Access data from other families
- ❌ Show SQL queries or code to users
- ❌ Answer off-topic questions (weather, sports, etc.)

## Troubleshooting

### Chatbot Button Not Visible

**Possible causes:**
1. Not logged in yet (chatbot only shows after login)
2. `CHATBOT_ENABLED = False` in `config.py`
3. `GEMINI_API_KEY` not set

**Solution:**
- Ensure you're logged in
- Check `config.py`: `CHATBOT_ENABLED` should be `True`
- Verify environment variable is set correctly

### "Chatbot is currently unavailable" Error

**Cause:** API key not configured or invalid

**Solution:**
```bash
# Check if environment variable is set
echo $GEMINI_API_KEY  # Mac/Linux
echo $env:GEMINI_API_KEY  # Windows PowerShell

# If empty, set it again (see "Set Environment Variable" above)
```

### "Access Denied" Messages

**Cause:** Trying to access data outside your permissions

**Example:**
- Member asking: "How much did my dad spend?" → **Denied**
- Member should ask: "How much have I spent?" → **Allowed**

**Solution:** Rephrase question to focus on your own data (if you're a member)

### Rate Limit Errors

**Cause:** Exceeded Gemini free tier limit (15 requests/minute)

**Solution:** Wait 60 seconds before sending more queries

## Advanced Configuration

### Disable Chatbot Temporarily

Edit `config.py`:

```python
CHATBOT_ENABLED = False  # Set to False to disable
```

### Adjust Chat History Limit

Edit `config.py`:

```python
MAX_CHAT_HISTORY = 10  # Change to desired number of messages to keep
```

### Change LLM Model

Edit `config.py`:

```python
CHATBOT_MODEL = "gemini-1.5-pro"  # Use Pro model (requires paid API)
```

## Cost & Usage

### Free Tier (Gemini 1.5 Flash):
- **Cost**: $0 (completely free)
- **Rate Limit**: 15 requests per minute
- **Best for**: Personal use, small families

### Paid Tier (Gemini 1.5 Pro):
- **Cost**: Pay per request (check Google AI pricing)
- **Rate Limit**: Higher limits available
- **Best for**: Heavy usage, commercial deployments

## Knowledge Base

The chatbot uses ALL `.md` documentation files in the project directory to answer questions:

- `README.md`
- `SUPER_ADMIN_GUIDE.md`
- `DEPLOYMENT_GUIDE.md`
- `QUICKSTART.md`
- And 18+ other documentation files

**To update chatbot knowledge:**
1. Edit the relevant `.md` file
2. Restart the application
3. Chatbot will automatically load updated content

## Technical Details

### Architecture:
- **LLM**: Google Gemini 1.5 Flash
- **RAG**: Document retrieval from .md files
- **Text-to-SQL**: Natural language to PostgreSQL conversion
- **Security**: SQL injection prevention, read-only queries

### Files:
- `chatbot_engine.py` - Backend logic
- `chatbot_widget.py` - UI components
- `config.py` - Configuration
- `multi_user_database.py` - Database integration

---

**Need Help?**

If you encounter issues not covered here, please:
1. Check the application logs
2. Verify your Gemini API key is valid
3. Ensure you have an active internet connection
