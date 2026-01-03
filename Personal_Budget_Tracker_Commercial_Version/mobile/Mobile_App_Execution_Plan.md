# Mobile App Execution Plan (Antigravity)

**Goal:** Create a FastAPI backend (hosted on Render) and a React Native mobile app (Expo) that connects to the existing Neon database.
**Constraint:** Use existing `multi_user_database.py` logic. Ignore chatbot features for now.

---

## Phase 1: Backend API Creation
**Instruction to User:** Paste this entire block into Antigravity to generate the API layer.

> **PROMPT 1: Create FastAPI Backend**
>
> I need to turn my existing Python logic into an API for a mobile app.
>
> 1.  **Create a file named `api.py`** in the root directory.
> 2.  **Dependencies:** Use `fastapi`, `uvicorn`, and `pydantic`.
> 3.  **Database Connection:** Import the `MultiUserDB` class from my existing `multi_user_database.py` file. Initialize it globally.
> 4.  **CORS:** Configure FastAPI CORS middleware to allow all origins (`allow_origins=["*"]`) so my mobile app can connect.
> 5.  **Create the following Endpoints:**
>     * `POST /login`: Accepts JSON `{email, password}`. Uses `db.authenticate_user`. Returns `{"status": "success", "user": user_dict}` or HTTP 401 if failed.
>     * `GET /users/{user_id}/dashboard`: Returns a JSON summary of income vs expenses for the current month.
>     * `GET /users/{user_id}/expenses`: Accepts optional query params `year` and `month`. Returns a list of expenses.
>     * `POST /expenses`: Accepts JSON `{user_id, date, category, subcategory, amount, comment}`. Uses `db.add_expense`. Returns success status.
>     * `GET /households/{household_id}/members`: Returns list of family members (for admin view).
> 6.  **Pydantic Models:** Create classes for `LoginRequest` and `ExpenseRequest` to validate input data.
> 7.  **Environment:** Ensure it uses `os.getenv("DATABASE_URL")` to connect to my Neon DB.

---

## Phase 2: Deploy Backend to Render
**Instruction to User:** Once `api.py` is created, use this prompt to deploy it.

> **PROMPT 2: Deploy to Render**
>
> 1.  **Update Requirements:** Add `fastapi` and `uvicorn` to my `requirements.txt` file.
> 2.  **Create Build Script:** Ensure there is a `render.yaml` or configuration instructing Render to run the app using: `uvicorn api:app --host 0.0.0.0 --port $PORT`.
> 3.  **Deploy:** Deploy this updated code to my existing Render Web Service.
> 4.  **Output:** Provide me with the public URL of the deployed API (e.g., `https://my-app.onrender.com`).

---

## Phase 3: Mobile App Setup (Local)
**Instruction to User:** Run these commands in your local VS Code terminal to set up the folder structure (Antigravity cannot run terminal commands for you, you must do this).

```bash
# 1. Create the Expo app
npx create-expo-app FamilyBudgetMobile

# 2. Navigate into the folder
cd FamilyBudgetMobile

# 3. Install necessary mobile libraries
npm install axios @react-navigation/native @react-navigation/stack react-native-safe-area-context react-native-screens react-native-gesture-handler react-native-chart-kit react-native-svg