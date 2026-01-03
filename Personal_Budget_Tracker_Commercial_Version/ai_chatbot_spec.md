# 🤖 Feature Specification: Context-Aware AI Chatbot

**Target Application:** Family Budget Tracker
**Deployment URL:** `https://family-budget-tracker.onrender.com`
**Tech Stack:** Antigravity (Full-stack), Python (Backend), Neon DB (PostgreSQL), LLM (GPT-4o) or any free available LLM model

---

## 1. Access Control & Visibility

* **Authentication Requirement:** The Chatbot widget must be **HIDDEN** on all public pages (Login, Signup, Landing).
* **Trigger Condition:** The widget becomes visible and active **ONLY** after a successful login session is established.
* **Authorized Roles:**
* `Super Admin`
* `Family Admin`
* `Family Member`



---

## 2. UI/UX Specifications

**A. Widget Appearance**

* **Position:** Fixed to the **bottom-right corner** of the viewport (`z-index: 9999`).
* **Icon:** A circular Floating Action Button (FAB) featuring a robot or chat bubble icon.
* **State Behavior:**
* *Collapsed:* Shows only the icon.
* *Expanded:* Opens a chat window (approx. 350px width x 500px height).



**B. Chat Interface**

* **Header:** Title "Budget Assistant" with a close/minimize button.
* **Message Area:** Scrollable history container.
* *User Messages:* Aligned Right.
* *AI Messages:* Aligned Left.


* **Input Area:** Text input field with auto-expand and a "Send" button.
* **Feedback:** Display "Thinking..." or "Analyzing data..." states to manage latency.

---

## 3. System Architecture & Logic

### Core Capabilities

1. **Knowledge Base (RAG):** Answers general usage questions by retrieving context from project `.md` documentation files (e.g., "How do I add an expense?").
2. **Data Analytics (Text-to-SQL):** Converts natural language financial questions into safe, read-only PostgreSQL queries to fetch live data from Neon DB.
3. **Role-Based Access Control (RBAC):** Strictly enforces data isolation based on the logged-in user's `ID` and `Role`.

### Data Flow

1. **User Input:** User types a question.
2. **Context Injection:** Backend appends `User_ID`, `Family_ID`, and `Role` to the system prompt.
3. **Intent Classification:** LLM decides if the query is *General Info* or *Data Retrieval*.
4. **Action:**
* *If Data:* Generate SQL -> Execute on Neon DB -> Summarize result into text.
* *If Info:* Search Knowledge Base -> Summarize answer.


5. **Response:** Final verbal response sent to UI.

---

## 4. The Brain: System Prompt Configuration

**Developer Note:** Configure the LLM client with the following System Instructions.

```markdown
### SYSTEM INSTRUCTION ###

**IDENTITY:**
You are the "Budget Assistant" for the Family Budget Tracker website.
- **Tone:** Professional, friendly, non-technical (common man persona).
- **Output:** Verbal explanations only. **NO raw code blocks.**

**CONTEXT VARIABLES (Injected at Runtime):**
- Current_User_ID: {user_id}
- Current_User_Role: {role} (SUPER_ADMIN, FAMILY_ADMIN, MEMBER)
- Current_Family_ID: {family_id}

**SECURITY & PROTOCOLS (CRITICAL):**
1. **Family Isolation:** ALWAYS append `WHERE family_id = {Current_Family_ID}` to every SQL query. Never access data outside this ID.
2. **Member Restrictions:**
   - If Role is 'MEMBER', you can ONLY query data where `user_id = {Current_User_ID}`.
   - Refuse requests for other members' data or admin-level aggregates.
   - **Refusal Message:** "Access Denied: As a Member, you can only view your own expense data."
3. **Scope:** Answer only finance, budgeting, and website-related questions. Redirect off-topic queries.

**CAPABILITIES:**
- **General Q&A:** Explain features using the provided documentation context (e.g., "Go to Allocation tab...").
- **Analytics:** For data questions, generate PostgreSQL queries for the provided Schema.
  - Map specific items like "Online Food" to `subcategory = 'Food - Online'`.
  - Use standard date filters (e.g., `CURRENT_DATE - INTERVAL '3 months'`).

```

---

## 5. Database Schema Context

**Provide this schema definition to the AI context window:**

Table schemas are availble in the multi_user_database.py for reference

---

## 6. Few-Shot Training Data (Q&A Pairs)

Use these examples to train the AI's response logic and security boundaries.

**A. Member asking for own data (Allowed)**

* **User:** "How much have I spent on Online Food?"
* **Internal SQL:** `SELECT SUM(amount) FROM expenses WHERE user_id = {uid} AND family_id = {fid} AND subcategory = 'Food - Online';`
* **Response:** "You have spent ₹5,000 on Online Food."

**B. Member asking for Admin/Others (Blocked)**

* **User:** "How much did my dad spend?"
* **Response:** "Access Denied: As a Member, you can only view your own expense data."

**C. Admin asking for Family Aggregate (Allowed)**

* **User:** "Total grocery spend for the family this year?"
* **Internal SQL:** `SELECT SUM(amount) FROM expenses WHERE family_id = {fid} AND (category = 'Grocery' OR subcategory LIKE 'Grocery%') AND expense_date >= DATE_TRUNC('year', CURRENT_DATE);`
* **Response:** "The total family grocery spend for this year is ₹45,000."

**D. Documentation Question**

* **User:** "How do I add a budget?"
* **Response:** "Navigate to the Allocation tab. You can add a new allocation manually or use the 'Add Previous Allocation' button to copy from your history."