# Backend API - Complete Documentation

**File:** `api.py`  
**Lines:** 1,394  
**Framework:** FastAPI  
**Purpose:** RESTful API backend for mobile and web access

---

## Overview

### What is the Backend API?

**Simple Explanation:**
The backend API is the "middleman" between your apps (web/mobile) and the database. Think of it as a translator and traffic controller.

**Architecture:**
```
Mobile/Web App → Makes Request → Backend API → Validates → Database
                                        ←  Returns Data  ←
```

### Technology Stack

- **Framework:** FastAPI (Python)
- **Authentication:** JWT (JSON Web Tokens)
- **Database:** MultiUserDB (PostgreSQL/SQLite)
- **Security:** CORS, Bearer tokens

---

## Configuration & Setup

### FastAPI Initialization

```python
# Lines 16-20
app = FastAPI(
    title="Family Budget Tracker API",
    description="REST API for mobile app access to budget data",
    version="1.0.0"
)
```

### CORS Configuration

```python
# Lines 22-30
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**What is CORS?**
- Cross-Origin Resource Sharing
- Allows mobile app to call API from different domain
- Security feature of web browsers

### Database Connection

```python
# Lines 33-46
def get_database_url():
    db_url = os.getenv('DATABASE_URL')
    if db_url and db_url.startswith('postgres://'):
        # Fix for SQLAlchemy compatibility
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    return db_url

db = MultiUserDB()
```

---

## Authentication System

### JWT Configuration

```python
# Lines 48-54
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "your-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
security = HTTPBearer()
```

**What is JWT?**
- JSON Web Token
- Like a digital passport
- Created at login, checked on every request
- Expires after 24 hours

### Create Token Function

```python
# Lines 96-104
def create_jwt_token(user_id: int, email: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
```

**How It Works:**
1. Takes user info
2. Adds expiration time
3. Encrypts with secret key
4. Returns encrypted string

**Example Token:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyOCwiZW1haWwiOiJ2aW5ub2RoQGdtYWlsLmNvbSIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTY0MjUwNjAwMH0.xyzabc123...
```

### Verify Token Function

```python
# Lines 106-121
def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except (jwt.DecodeError, jwt.InvalidTokenError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

**What It Does:**
1. Extracts token from request header
2. Decrypts with secret key
3. Checks expiration
4. Returns user data OR raises error

---

## Pydantic Models (Request Validation)

### What are Pydantic Models?

Think of them as **forms that check if you filled everything correctly**.

### LoginRequest

```python
# Lines 58-60
class LoginRequest(BaseModel):
    email: str
    password: str
```

**Validates:**
- email is a string
- password is a string
- Both fields present

**Example Valid Request:**
```json
{
    "email": "vinnodh@gmail.com",
    "password": "secret123"
}
```

### AllocationRequest ✨ (v6.1)

```python
# Lines 72-77
class AllocationRequest(BaseModel):
    user_id: int
    category: str
    allocated_amount: float
    year: int
    month: int
```

**Why All These Fields?**
- `user_id`: Who owns this allocation
- `category`: What category (Rent, Food, etc.)
- `allocated_amount`: How much money
- `year`, `month`: Which period

**v6.1 Note:** All fields are required now!

### ExpenseRequest

```python
# Lines 79-85
class ExpenseRequest(BaseModel):
    user_id: int
    date: str  # YYYY-MM-DD
    category: str
    subcategory: Optional[str] = None
    amount: float
    comment: Optional[str] = None
```

**Optional vs Required:**
- `Optional[str] = None`: Can be omitted
- `str`: Must be provided

---

## API Endpoints

### Format

```
METHOD /path
Description
Request Body
Response
```

---

## Authentication Endpoints

### 1. Login

**Endpoint:** `POST /api/auth/login`  
**Purpose:** Authenticate user and get token  
**Lines:** 136-163

**Request:**
```json
{
    "email": "vinnodh@gmail.com",
    "password": "secret123"
}
```

**Response (Success):**
```json
{
    "status": "success",
    "data": {
        "token": "eyJhbGciOiJIUzI1NiIs...",
        "user": {
            "id": 28,
            "email": "vinnodh@gmail.com",
            "full_name": "Vinnodh",
            "role": "admin",
            "household_id": 5,
            "is_active": true
        }
    },
    "message": "Login successful"
}
```

**Response (Error):**
```json
HTTP 401 Unauthorized
{
    "detail": "Invalid email or password"
}
```

**Code Flow:**
```python
@app.post("/api/auth/login")
def login(request: LoginRequest):
    # 1. Validate credentials
    success, user_data = db.authenticate_user(request.email, request.password)
    
    # 2. Check if valid
    if not success:
        raise HTTPException(...)
    
    # 3. Create token
    token = create_jwt_token(user['id'], user['email'], user['role'])
    
    # 4. Return token + user data
    return {"status": "success", "data": {"token": token, "user": user}}
```

---

## Dashboard Endpoint

### Get Dashboard Summary

**Endpoint:** `GET /api/dashboard/{user_id}`  
**Purpose:** Get income/expense/allocation summary  
**Auth:** Required (JWT)

**Request:**
```
GET /api/dashboard/28?year=2026&month=1
Headers:
  Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "income": {
            "total": 140000,
            "count": 1
        },
        "expenses": {
            "total": 137558,
            "count": 34
        },
        "allocations": {
            "allocated": 115000,
            "spent": 112558,
            "balance": 2442
        }
    }
}
```

---

## Income Endpoints

### 1. Get Income

**Endpoint:** `GET /api/income/{user_id}`  
**Auth:** Required

**Request:**
```
GET /api/income/28?year=2026&month=1
```

**Response:**
```json
{
    "status": "success",
    "data": [
        {
            "id": 45,
            "user_id": 28,
            "date": "2026-01-01",
            "source": "Salary",
            "amount": 50000,
            "created_at": "2026-01-01T10:30:00"
        },
        {
            "id": 46,
            "user_id": 28,
            "date": "2026-01-15",
            "source": "Bonus",
            "amount": 10000,
            "created_at": "2026-01-15T14:20:00"
        }
    ]
}
```

### 2. Add Income

**Endpoint:** `POST /api/income`  
**Auth:** Required

**Request:**
```json
{
    "user_id": 28,
    "date": "2026-01-20",
    "source": "Freelance",
    "amount": 5000
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Income added successfully",
    "data": {
        "id": 47
    }
}
```

### 3. Update Income

**Endpoint:** `PUT /api/income/{id}`  
**Auth:** Required

**Request:**
```json
{
    "user_id": 28,
    "date": "2026-01-20",
    "source": "Freelance Project",
    "amount": 7500
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Income updated successfully"
}
```

### 4. Delete Income

**Endpoint:** `DELETE /api/income/{id}`  
**Auth:** Required

**Request:**
```
DELETE /api/income/47
```

**Response:**
```json
{
    "status": "success",
    "message": "Income deleted successfully"
}
```

---

## Allocation Endpoints ✨ (v6.1 Updated)

### 1. Get Allocations

**Endpoint:** `GET /api/allocations/{user_id}`  
**Auth:** Required

**Response:**
```json
{
    "status": "success",
    "data": [
        {
            "index": 15,
            "Category": "Rent",
            "Allocated Amount": 25000,
            "Spent Amount": 25000,
            "Balance": 0,
            "year": 2026,
            "month": 1
        },
        {
            "index": 16,
            "Category": "Food",
            "Allocated Amount": 15000,
            "Spent Amount": 12558,
            "Balance": 2442,
            "year": 2026,
            "month": 1
        }
    ]
}
```

### 2. Add Allocation

**Endpoint:** `POST /api/allocations`  
**Auth:** Required

**Request:**
```json
{
    "user_id": 28,
    "category": "Transport",
    "allocated_amount": 5000,
    "year": 2026,
    "month": 1
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Allocation added successfully"
}
```

### 3. Update Allocation ✨ (v6.1 Fixed)

**Endpoint:** `PUT /api/allocations/{id}`  
**Auth:** Required

**Request (v6.1 - All fields required):**
```json
{
    "user_id": 28,
    "category": "Rent",
    "allocated_amount": 25001,
    "year": 2026,
    "month": 1
}
```

**Backend Code (v6.1 Fix):**
```python
@app.put("/api/allocations/{allocation_id}")
def update_allocation(
    allocation_id: int,
    request: AllocationRequest,
    current_user: dict = Depends(verify_jwt_token)
):
    # ✨ v6.1: Now passes user_id to database
    success = db.update_allocation(
        allocation_id,
        request.user_id,      # ← Added in v6.1
        request.category,
        request.allocated_amount,
        request.year,         # ← Added in v6.1
        request.month         # ← Added in v6.1
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update allocation"
        )
    
    return {
        "status": "success",
        "message": "Allocation updated successfully"
    }
```

**Before v6.1 (BROKEN):**
```python
# Missing fields!
success = db.update_allocation(
    allocation_id,
    request.category,
    request.allocated_amount
)
# → TypeError: missing required arguments
```

### 4. Delete Allocation

**Endpoint:** `DELETE /api/allocations/{id}`  
**Auth:** Required

**Response:**
```json
{
    "status": "success",
    "message": "Allocation deleted successfully"
}
```

---

## Expense Endpoints

### 1. Get Expenses

**Endpoint:** `GET /api/expenses/{user_id}`  
**Auth:** Required

**Response:**
```json
{
    "status": "success",
    "data": [
        {
            "id": 152,
            "user_id": 28,
            "date": "2026-01-15",
            "category": "Food",
            "subcategory": "Grocery-Online",
            "amount": 3000,
            "comment": "Weekly groceries",
            "created_at": "2026-01-15T18:30:00"
        }
    ]
}
```

### 2. Add Expense

**Endpoint:** `POST /api/expenses`  
**Auth:** Required

**Request:**
```json
{
    "user_id": 28,
    "date": "2026-01-20",
    "category": "Food",
    "subcategory": "Food-Hotel",
    "amount": 1500,
    "comment": "Dinner with family"
}
```

### 3. Update Expense

**Endpoint:** `PUT /api/expenses/{id}`  
**Auth:** Required

### 4. Delete Expense

**Endpoint:** `DELETE /api/expenses/{id}`  
**Auth:** Required

---

## Error Responses

### Common HTTP Status Codes

**200 OK** - Success
**201 Created** - Resource created
**400 Bad Request** - Invalid data
**401 Unauthorized** - Not logged in / invalid token
**403 Forbidden** - Logged in but not allowed
**404 Not Found** - Resource doesn't exist
**422 Unprocessable Entity** - Validation error
**500 Internal Server Error** - Server problem

### Error Response Format

```json
{
    "detail": "Error message here"
}
```

### Example Errors

**Missing Field:**
```json
HTTP 422
{
    "detail": [
        {
            "loc": ["body", "user_id"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}
```

**Expired Token:**
```json
HTTP 401
{
    "detail": "Token has expired"
}
```

**Over Budget (from app logic):**
```json
HTTP 400
{
    "detail": "Allocation exceeds available budget"
}
```

---

## Request Flow Example

### Complete Flow: Add Expense

**1. Mobile App Calls API:**
```javascript
await api.addExpense({
    user_id: 28,
    date: "2026-01-20",
    category: "Food",
    subcategory: "Grocery-Online",
    amount: 3000,
    comment: "Weekly shopping"
});
```

**2. HTTP Request:**
```
POST https://api.example.com/api/expenses
Headers:
  Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
  Content-Type: application/json
Body:
{
    "user_id": 28,
    "date": "2026-01-20",
    "category": "Food",
    "subcategory": "Grocery-Online",
    "amount": 3000,
    "comment": "Weekly shopping"
}
```

**3. FastAPI Receives:**
```python
@app.post("/api/expenses")
def add_expense(
    request: ExpenseRequest,
    current_user: dict = Depends(verify_jwt_token)
):
```

**4. Validation:**
- Pydantic validates request body
- verify_jwt_token validates token
- Both pass ✓

**5. Database Call:**
```python
success = db.add_expense(
    request.user_id,
    request.date,
    request.category,
    request.subcategory,
    request.amount,
    request.comment
)
```

**6. Auto-Update Allocation:**
```python
# Inside db.add_expense:
db.update_allocation_spent_amount(user_id, category, year, month)
```

**7. Response:**
```python
return {
    "status": "success",
    "message": "Expense added successfully"
}
```

**8. Back to Mobile:**
```javascript
// Success!
Alert.alert('Success', 'Expense added');
navigation.goBack();
```

---

## Security Features

### 1. JWT Authentication
- Every request (except login) requires valid token
- Token includes user ID and role
- Expires after 24 hours

### 2. Role-Based Access
```python
if current_user.get('role') != 'superadmin':
    raise HTTPException(status_code=403, detail="Access denied")
```

### 3. Data Isolation
- Users can only access their own data
- Admin can access household data
- Super admin can access all data

### 4. Password Hashing
- Passwords never stored in plain text
- SHA-256 hashing
- Cannot be reversed

---

*Backend API Documentation Complete - Proceeding to Database...*
