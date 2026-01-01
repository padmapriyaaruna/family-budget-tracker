"""
AI Chatbot Engine for Family Budget Tracker
Handles LLM interactions, RAG document retrieval, and text-to-SQL conversion
"""
import os
import re
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import google.generativeai as genai


class LLMClient:
    """Wrapper for Google Gemini API interactions"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client with API key from environment or parameter"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. Please set GEMINI_API_KEY or GOOGLE_API_KEY "
                "environment variable. Get your key from: https://makersuite.google.com/app/apikey"
            )
        
        # Initialize with old but working API
        genai.configure(api_key=self.api_key)
        # Use current 2026 model
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.chat_session = None
    
    def generate_response(self, prompt: str, system_instruction: str = "") -> str:
        """Generate a response from Gemini with optional system instruction"""
        try:
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"⚠️ Error communicating with AI: {str(e)}"
    
    def start_chat(self, system_instruction: str = ""):
        """Start a chat session with context"""
        self.chat_session = self.model.start_chat(history=[])
        if system_instruction:
            self.chat_session.send_message(f"SYSTEM: {system_instruction}")
    
    def send_message(self, message: str) -> str:
        """Send a message in ongoing chat session"""
        if not self.chat_session:
            self.start_chat()
        
        try:
            response = self.chat_session.send_message(message)
            return response.text
        except Exception as e:
            return f"⚠️ Error: {str(e)}"


class DocumentRetriever:
    """RAG system to retrieve relevant documentation from .md files"""
    
    def __init__(self, docs_directory: str):
        """Initialize document retriever with directory containing .md files"""
        self.docs_directory = Path(docs_directory)
        self.documents = {}
        self._load_documents()
    
    def _load_documents(self):
        """Load all .md files from the directory"""
        if not self.docs_directory.exists():
            print(f"⚠️ Documentation directory not found: {self.docs_directory}")
            return
        
        for md_file in self.docs_directory.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.documents[md_file.name] = {
                        'content': content,
                        'filename': md_file.name,
                        'size': len(content)
                    }
            except Exception as e:
                print(f"⚠️ Error loading {md_file.name}: {e}")
        
        print(f"✅ Loaded {len(self.documents)} documentation files")
    
    def retrieve_relevant_docs(self, query: str, max_docs: int = 3) -> str:
        """Retrieve most relevant documents based on keyword matching"""
        if not self.documents:
            return "No documentation available."
        
        # Simple keyword-based relevance scoring
        query_lower = query.lower()
        keywords = set(query_lower.split())
        
        scored_docs = []
        for filename, doc in self.documents.items():
            content_lower = doc['content'].lower()
            
            # Calculate relevance score
            score = 0
            for keyword in keywords:
                if len(keyword) > 3:  # Skip short words
                    score += content_lower.count(keyword)
            
            # Boost score for title matches
            if any(keyword in filename.lower() for keyword in keywords):
                score += 10
            
            scored_docs.append((filename, doc, score))
        
        # Sort by relevance
        scored_docs.sort(key=lambda x: x[2], reverse=True)
        
        # Return top documents
        relevant_content = []
        for filename, doc, score in scored_docs[:max_docs]:
            if score > 0:
                relevant_content.append(f"### From {filename}:\n{doc['content'][:1000]}\n")
        
        return "\n".join(relevant_content) if relevant_content else "No relevant documentation found."


class TextToSQLEngine:
    """Converts natural language queries to safe PostgreSQL queries"""
    
    def __init__(self, llm_client: LLMClient):
        """Initialize with LLM client for NL to SQL conversion"""
        self.llm = llm_client
        self.schema = self._get_schema_definition()
    
    def _get_schema_definition(self) -> str:
        """Define database schema for SQL generation"""
        return """
DATABASE SCHEMA:

Table: households
- id (INTEGER PRIMARY KEY)
- name (TEXT) - Family/household name
- is_active (BOOLEAN)
- created_at (TIMESTAMP)

Table: users
- id (INTEGER PRIMARY KEY)
- household_id (INTEGER) - Foreign key to households
- email (TEXT)
- full_name (TEXT) - User's display name
- role (TEXT) - 'superadmin', 'admin', or 'member'
- relationship (TEXT) - e.g., 'Father', 'Mother', 'Son'
- is_active (BOOLEAN)

Table: income
- id (INTEGER PRIMARY KEY)
- user_id (INTEGER) - Foreign key to users
- date (TEXT) - Format: 'YYYY-MM-DD'
- source (TEXT) - Income source name
- amount (NUMERIC) - Income amount
- created_at (TIMESTAMP)

Table: allocations
- id (INTEGER PRIMARY KEY)
- user_id (INTEGER) - Foreign key to users
- category (TEXT) - Allocation category name
- allocated_amount (NUMERIC) - Allocated budget
- spent_amount (NUMERIC) - Amount spent
- balance (NUMERIC) - Remaining balance

Table: expenses
- id (INTEGER PRIMARY KEY)
- user_id (INTEGER) - Foreign key to users
- date (TEXT) - Expense date format: 'YYYY-MM-DD'
- category (TEXT) - Expense category
- subcategory (TEXT) - Options: 'Investment', 'Food - Online', 'Food - Hotel', 
                       'Grocery - Online', 'Grocery - Offline', 'School Fee',
                       'Extra-Curricular', 'Co-Curricular', 'Others'
- amount (NUMERIC) - Expense amount
- comment (TEXT) - Optional notes
- created_at (TIMESTAMP)

IMPORTANT NOTES:
- Currency symbol is ₹ (Indian Rupees)
- Date format is 'YYYY-MM-DD'
- Use CURRENT_DATE for today's date
- Use DATE_TRUNC for period filtering
"""
    
    def generate_sql(self, query: str, user_id: int, family_id: int, role: str) -> Tuple[str, str]:
        """
        Generate SQL query from natural language
        Returns: (sql_query, explanation)
        """
        # Build context-aware prompt
        prompt = f"""
You are a SQL query generator for a Family Budget Tracker database.

{self.schema}

USER CONTEXT:
- User ID: {user_id}
- Family ID: {family_id}
- Role: {role}

SECURITY RULES (CRITICAL):
1. ONLY generate SELECT queries (read-only)
2. ALWAYS include WHERE clause with household_id = {family_id} for family data isolation
3. Role-based access:
   - If role is 'member': MUST restrict to user_id = {user_id} in WHERE clause
   - If role is 'admin': Can query ALL family members' data (household_id = {family_id})
   - If role is 'superadmin': Can query any household data
4. For 'admin' role: DO NOT restrict by user_id - they can see all family expenses/income

Natural Language Query: "{query}"

Generate a safe PostgreSQL query. Return ONLY the SQL query, no explanations.
If the query is not possible or violates security rules, return: "UNSAFE_QUERY"
"""
        
        # Get SQL from LLM
        sql_response = self.llm.generate_response(prompt)
        sql_query = sql_response.strip()
        
        # Strip markdown code blocks if present (```sql ... ```)
        if sql_query.startswith('```'):
            lines = sql_query.split('\n')
            # Remove first line (```sql)
            if len(lines) > 1:
                lines = lines[1:]
            # Remove last line if it's ```
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            sql_query = '\n'.join(lines).strip()
        
        # Validate the query
        is_safe, debug_msg = self._is_safe_query(sql_query, user_id, family_id, role)
        if not is_safe:
            return "UNSAFE_QUERY", f"Security validation failed: {debug_msg}. SQL was: {sql_query[:200]}"
        
        return sql_query, "SQL query generated successfully"
    
    def _is_safe_query(self, sql: str, user_id: int, family_id: int, role: str) -> tuple[bool, str]:
        """Validate SQL query for safety. Returns (is_safe, debug_message)"""
        
        if sql == "UNSAFE_QUERY":
            return False, "LLM returned 'UNSAFE_QUERY'"
        
        sql_upper = sql.upper()
        
        # Must be SELECT only
        if not sql_upper.strip().startswith("SELECT"):
            return False, "Not a SELECT query"
        
        # Block dangerous operations
        dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE", "EXECUTE"]
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return False, f"Contains dangerous keyword: {keyword}"
        
        # For members: Must have WHERE clause restricting to their user_id
        if role == 'member':
            if "WHERE" not in sql_upper:
                return False, "Member query missing WHERE clause"
            if f"USER_ID = {user_id}" not in sql_upper and f"USER_ID={user_id}" not in sql_upper:
                return False, f"Member query missing user_id={user_id} restriction"
        
        # Admin/superadmin: Allow queries without strict user_id restriction
        return True, "Passed all validations"


class ChatbotEngine:
    """Main chatbot orchestrator - handles intent classification and response generation"""
    
    def __init__(self, docs_directory: str, api_key: Optional[str] = None):
        """Initialize chatbot with LLM, document retrieval, and SQL engine"""
        self.llm = LLMClient(api_key)
        self.doc_retriever = DocumentRetriever(docs_directory)
        self.sql_engine = TextToSQLEngine(self.llm)
    
    def _build_system_instruction(self, user_id: int, family_id: int, role: str, full_name: str) -> str:
        """Build system instruction with user context"""
        return f"""### SYSTEM INSTRUCTION ###

**IDENTITY:**
You are the "Budget Assistant" for the Family Budget Tracker application.
- **Tone:** Professional, friendly, helpful (common person language)
- **Output:** Verbal explanations ONLY. NO code blocks, NO raw SQL, NO technical jargon.
- **Important:** NEVER show code to users. Explain concepts in simple, everyday language.

**CURRENT USER CONTEXT:**
- Name: {full_name}
- User ID: {user_id}
- Family ID: {family_id}
- Role: {role.upper()}

**SECURITY & ACCESS RULES:**
1. **Family Isolation:** Only access data for Family ID {family_id}
2. **Role-Based Access:**
   - If role is 'member': 
     * Can ONLY see their own data (User ID {user_id})
     * Refuse requests for other family members' data
     * Response: "As a Family Member, you can only view your own expense and income data."
   - If role is 'admin':
     * Can view ALL family members' data within household {family_id}
     * Can answer questions about any family member's expenses/income
     * Examples: "kids' education", "spouse's spending", "total family expenses"
   - If role is 'superadmin':
     * Can view aggregated data across all households

**YOUR CAPABILITIES:**
1. **Answer Questions:** Help users understand how to use the budget tracker
2. **Data Insights:** Answer questions about expenses, income, allocations, and savings
3. **Guidance:** Explain features, steps, and best practices

**WHAT YOU CANNOT DO:**
- Access data outside Family ID {family_id}
- Show code or technical implementation details
- Answer off-topic questions (weather, sports, general knowledge)
- Modify or delete data (read-only access)

**RESPONSE STYLE:**
- Be conversational and friendly
- Use currency symbol ₹ for amounts
- Format numbers clearly (e.g., ₹1,234.56)
- If you don't have enough data, say so politely
- Keep responses concise but complete

**OFF-TOPIC HANDLING:**
If asked about non-budget topics, politely redirect:
"I'm here to help with your budget and expenses. Please ask about your income, expenses, allocations, or how to use the tracker."
"""
    
    def _classify_intent(self, query: str) -> str:
        """Classify user query as 'data' or 'general'"""
        query_lower = query.lower()
        
        # Keywords that indicate data queries
        data_keywords = [
        
        return "data" if data_score > general_score else "general"
    
    def process_query(
        self, 
        query: str, 
        user_id: int, 
        family_id: int, 
        role: str, 
        full_name: str,
        db_connection
    ) -> str:
        """
        Process user query and generate response
        
        Args:
            query: User's question
            user_id: Current user ID
            family_id: User's family/household ID
            role: User role (member, admin, superadmin)
            full_name: User's display name
            db_connection: Database connection for executing queries
        
        Returns:
            AI-generated response
        """
        # Build system instruction
        system_instruction = self._build_system_instruction(user_id, family_id, role, full_name)
        
        # Classify intent
        intent = self.classify_intent(query)
        
        if intent == "data":
            # Data analytics query
            return self._handle_data_query(query, user_id, family_id, role, system_instruction, db_connection)
        else:
            # General documentation query
            return self._handle_general_query(query, system_instruction)
    
    def _handle_data_query(
        self, 
        query: str, 
        user_id: int, 
        family_id: int, 
        role: str,
        system_instruction: str,
        db_connection
    ) -> str:
        """Handle data analytics queries using text-to-SQL"""
        try:
            # Generate SQL
            sql_query, explanation = self.sql_engine.generate_sql(query, user_id, family_id, role)
            
            # DEBUG: Print details
            print(f"🔍 DEBUG - Role: {role}, User ID: {user_id}, Family ID: {family_id}")
            print(f"🔍 DEBUG - SQL: {sql_query}")
            
            if sql_query == "UNSAFE_QUERY":
                print(f"🔍 DEBUG - Query blocked: {explanation}")
                return f"I cannot process this query due to security restrictions.\n\n[DEBUG: {explanation}]"
            
            # Execute query using dedicated chatbot method
            results = db_connection.execute_chatbot_query(
                sql_query=sql_query,
                user_id=user_id,
                family_id=family_id,
                role=role
            )
            
            # Format results for LLM
            results_text = "\n".join([str(row) for row in results])
            
            # Generate natural language response
            prompt = f"""
{system_instruction}

User asked: "{query}"

Database Results:
{results_text}

Based on these results, provide a clear, conversational answer to the user's question.
Remember: NO code, NO SQL, just explain the data in simple terms with proper formatting.
If results are empty, say "No data found for this query."
"""
            
            response = self.llm.generate_response(prompt)
            return response
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"🔍 DEBUG - Exception: {error_trace}")
            return f"I encountered an issue retrieving your data.\n\n[DEBUG Error: {str(e)}]"
    
    def _handle_general_query(self, query: str, system_instruction: str) -> str:
        """Handle general questions using RAG document retrieval"""
        # Retrieve relevant documentation
        relevant_docs = self.doc_retriever.retrieve_relevant_docs(query, max_docs=2)
        
        # Generate response with context
        prompt = f"""
{system_instruction}

User Question: "{query}"

Relevant Documentation Context:
{relevant_docs}

Answer the user's question using the documentation context.
Explain in simple, step-by-step language. NO code snippets, NO technical terms.
If documentation doesn't cover the question, provide general guidance.
"""
        
        response = self.llm.generate_response(prompt)
        return response
