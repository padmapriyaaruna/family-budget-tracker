# Setting Up Gemini API Key on Render

## Your API Key Details
✅ API Key: `AIzaSyAepM1-hGVTWr-8Ki1MQRV4iEVsHgD5b0g`
✅ Project: Default Gemini Project  
✅ Project ID: gen-lang-client-0204505749

## Steps to Configure on Render

### 1. Go to Render Dashboard
- Navigate to: https://dashboard.render.com
- Click on your service: `family-budget-tracker`

### 2. Set Environment Variable
- Click on "Environment" in the left sidebar
- Look for `GEMINI_API_KEY` variable

**If it exists:**
- Click "Edit" 
- Replace the value with: `AIzaSyAepM1-hGVTWr-8Ki1MQRV4iEVsHgD5b0g`
- Click "Save Changes"

**If it doesn't exist:**
- Click "+ Add Environment Variable"
- Key: `GEMINI_API_KEY`
- Value: `AIzaSyAepM1-hGVTWr-8Ki1MQRV4iEVsHgD5b0g`
- Click "Add"

### 3. Redeploy with Clean Build
**Important:** You MUST do a clean deployment for the new key to work

- Click "Manual Deploy" button (top right)
- Select "Clear build cache & deploy"
- Wait for deployment to complete (2-5 minutes)

### 4. Test the Chatbot
After deployment completes:

1. Login to your app
2. Expand the "🤖 Budget Assistant Chatbot" section
3. Try these queries:
   - "What is my total income?"
   - "How much did I spend on groceries?"
   - "How many members in my family?"

## Expected Result
✅ The chatbot should now work and return actual responses from your database!

## If Still Not Working
Check Render logs for any errors:
- Go to "Logs" tab in Render dashboard  
- Look for error messages
- Share any errors you see

## Security Note
⚠️ **Never share your API key publicly!** 
- I can see it because you shared it in our private conversation
- Don't commit it to GitHub
- Only set it in Render environment variables
