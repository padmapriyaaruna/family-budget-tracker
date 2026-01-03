# Chatbot Troubleshooting Guide

## Current Status (2026-01-01)

The AI chatbot feature has been implemented but is experiencing API connectivity issues with Google Gemini.

### Issue Summary

**Error:** `404 NOT_FOUND - models/<model-name> is not found for API version v1beta`

This error occurs for ALL Gemini model names tried:
- ❌ `gemini-2.0-flash-exp`
- ❌ `gemini-1.5-flash-latest` 
- ❌ `gemini-1.5-flash`
- ❌ `models/gemini-1.5-flash`
- ❌ `gemini-pro`

### Root Cause Analysis

The 404 errors suggest one of these issues:

1. **Invalid/Expired API Key**
   - The `GEMINI_API_KEY` environment variable may be invalid
   - The key may have expired or been revoked
   - The key may not have proper permissions

2. **API Regional Restrictions**
   - The Gemini API might not be available in your region
   - Some models may require paid tier access

3. **SDK Version Incompatibility**
   - Conflicts between `google-generativeai` (deprecated) and `google-genai` (new)
   - Package caching issues on Render

## Immediate Action Items

### 1. Verify API Key

Go to [Google AI Studio](https://makersuite.google.com/app/apikey) and:

1. Check if your existing API key is still valid
2. Generate a NEW API key if needed
3. Update the `GEMINI_API_KEY` environment variable on Render:
   - Go to Render Dashboard → Your Service → Environment
   - Update `GEMINI_API_KEY` with the new key
   - Manual Deploy → Clear build cache & deploy

### 2. Test API Key Locally

Create a simple test script to verify the API key works:

```python
import google.generativeai as genai
import os

# Test your API key
api_key = "YOUR_API_KEY_HERE"
genai.configure(api_key=api_key)

try:
    # Try to list available models
    for model in genai.list_models():
        print(f"✅ Model: {model.name}")
    
    # Try to generate content
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hello, this is a test")
    print(f"✅ Response: {response.text}")
    print("\\n🎉 API key works!")
    
except Exception as e:
    print(f"❌ Error: {e}")
```

### 3. Alternative Solutions

If Gemini API continues to fail, consider these alternatives:

#### Option A: Simple FAQ Chatbot (No LLM)
Remove AI dependency and use a rule-based chatbot:
- Match user questions to predefined FAQ
- Return pre-written answers
- Still useful for common questions

#### Option B: Use Different LLM Provider
- OpenAI GPT (requires paid API)
- Anthropic Claude (requires paid API)
- Open-source models via Hugging Face

#### Option C: Disable Chatbot Temporarily
Comment out chatbot integration until API issues are resolved.

## What's Been Implemented

Despite API issues, the chatbot infrastructure is complete:

✅ **Backend (`chatbot_engine.py`)**
- LLM client wrapper
- RAG document retrieval (22 .md files indexed)
- Text-to-SQL engine
- Role-based access control
- Security validations

✅ **Frontend (`family_expense_tracker.py`)**
- Chat UI in main area (expander component)
- Chat history management
- Error handling

✅ **Database Integration**
- `execute_chatbot_query` method for safe SQL execution
- Read-only query enforcement
- Family isolation

✅ **Documentation**
- [CHATBOT_SETUP_GUIDE.md](CHATBOT_SETUP_GUIDE.md)
- [walkthrough.md](../.gemini/antigravity/brain/b334b79b-c192-406c-b0dd-1dc02442501b/walkthrough.md)

## Next Steps

1. **Verify API Key** (highest priority)
2. **Test locally** with the test script above  
3. **Check Render logs** after redeployment for any new errors
4. **Consider alternatives** if Gemini API unavailable in your region

## Files Modified

- `chatbot_engine.py` - Core chatbot logic
- `chatbot_widget.py` - UI components
- `chatbot_widget_simple.py` - Simplified widget
- `chatbot_widget_debug.py` - Debug version
- `family_expense_tracker.py` - Integration
- `multi_user_database.py` - Database methods
- `config.py` - Configuration
- `requirements.txt` - Dependencies

## Contact & Support

If issues persist:
1. Check [Google AI Studio Status](https://status.cloud.google.com/)
2. Review [Gemini API Documentation](https://ai.google.dev/docs)
3. Contact Google AI support for API key issues
