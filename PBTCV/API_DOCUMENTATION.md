# Family Budget Tracker API - Usage Guide

## Overview
REST API backend for Family Budget Tracker mobile app.

## Base URL
- **Local Development**: `http://localhost:8000`
- **Production (Render)**: `https://family-budget-api.onrender.com`

## Authentication

All endpoints (except `/api/auth/login` and root `/`) require JWT token authentication.

### Header Format
```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### 1. Authentication

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "token": "eyJ...",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "member",
      "household_id": 1
    }
  },
  "message": "Login successful"
}
```

#### Accept Invite
```http
POST /api/auth/accept-invite
Content-Type: application/json

{
  "invite_token": "abc123...",
  "password": "newpassword123"
}
```

### 2. User Profile

#### Get Profile
```http
GET /api/user/profile
Authorization: Bearer <token>
```

#### Get Household Members
```http
GET /api/household/{household_id}/members
Authorization: Bearer <token>
```

### 3. Dashboard

#### Get Dashboard Summary
```http
GET /api/dashboard/{user_id}?year=2026&month=1
Authorization: Bearer <token>
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "period": {"year": 2026, "month": 1},
    "income": {"total": 50000, "count": 2},
    "expenses": {"total": 35000, "count": 45},
    "allocations": {
      "allocated": 45000,
      "spent": 35000,
      "balance": 10000,
      "count": 8
    },
    "savings": 15000
  }
}
```

### 4. Income

#### Get Income
```http
GET /api/income/{user_id}?year=2026&month=1
Authorization: Bearer <token>
```

#### Add Income
```http
POST /api/income
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": 1,
  "date": "2026-01-15",
  "source": "Salary",
  "amount": 50000
}
```

#### Update Income
```http
PUT /api/income/{income_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": 1,
  "date": "2026-01-15",
  "source": "Salary (Updated)",
  "amount": 55000
}
```

#### Delete Income
```http
DELETE /api/income/{income_id}
Authorization: Bearer <token>
```

### 5. Allocations

#### Get Allocations
```http
GET /api/allocations/{user_id}?year=2026&month=1
Authorization: Bearer <token>
```

#### Add Allocation
```http
POST /api/allocations
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": 1,
  "category": "Groceries",
  "allocated_amount": 10000,
  "year": 2026,
  "month": 1
}
```

#### Update Allocation
```http
PUT /api/allocations/{allocation_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": 1,
  "category": "Groceries",
  "allocated_amount": 12000,
  "year": 2026,
  "month": 1
}
```

#### Delete Allocation
```http
DELETE /api/allocations/{allocation_id}
Authorization: Bearer <token>
```

#### Copy Previous Month Allocations
```http
POST /api/allocations/copy
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": 1,
  "from_year": 2025,
  "from_month": 12,
  "to_year": 2026,
  "to_month": 1
}
```

### 6. Expenses

#### Get Expenses
```http
GET /api/expenses/{user_id}?year=2026&month=1
Authorization: Bearer <token>
```

#### Add Expense
```http
POST /api/expenses
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": 1,
  "date": "2026-01-15",
  "category": "Groceries",
  "subcategory": "Grocery - Online",
  "amount": 1500,
  "comment": "Monthly grocery shopping"
}
```

#### Update Expense
```http
PUT /api/expenses/{expense_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": 1,
  "date": "2026-01-15",
  "category": "Groceries",
  "subcategory": "Grocery - Offline",
  "amount": 1600,
  "comment": "Updated amount"
}
```

#### Delete Expense
```http
DELETE /api/expenses/{expense_id}
Authorization: Bearer <token>
```

### 7. Household Member Management

#### Add Member to Household (Admin/Super Admin Only)
```http
POST /api/households/{household_id}/members
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "relationship": "Son"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Member John Doe added successfully",
  "data": {
    "member_id": 45,
    "household_id": 12,
    "name": "John Doe",
    "email": "john@example.com",
    "relationship": "Son",
    "note": "A temporary password has been set. Member should be invited to set their own password."
  }
}
```

**Permissions Required:** Family Admin or Super Admin role

**Validation:**
- Email must be unique across all users
- All fields (name, email, relationship) are required
- Returns 400 if email already exists
- Returns 403 if user lacks admin privileges

#### Delete User (Super Admin Only)
```http
DELETE /api/admin/users/{user_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "status": "success",
  "message": "User Sarah Smith (ID: 44) and all associated data deleted successfully"
}
```

**Permissions Required:** Super Admin role only

**Behavior:**
- Performs cascade delete: Removes user's expenses, income, allocations, and savings
- Returns 404 if user not found
- Returns 403 if user is not super admin
- Transaction-based: All deletes succeed or all fail (rollback on error)

## Running Locally

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
export DATABASE_URL="your_postgresql_connection_string"
export JWT_SECRET_KEY="your-secret-key-here"
export ALLOWED_ORIGINS="*"
```

### 3. Run Server
```bash
# Development (auto-reload)
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Production
python api.py
```

### 4. Test API
Visit: http://localhost:8000/docs for interactive API documentation (Swagger UI)

## Deploying to Render

### 1. Push to GitHub
```bash
git add api.py requirements.txt render.yaml
git commit -m "Add FastAPI backend for mobile app"
git push
```

### 2. Create New Web Service on Render
- Go to Render Dashboard
- Click "New" → "Web Service"
- Connect your GitHub repository
- Render will auto-detect `render.yaml` configuration

### 3. Set Environment Variables
In Render dashboard, add:
- `DATABASE_URL` - Your Neon/Supabase PostgreSQL URL
- `JWT_SECRET_KEY` - Will be auto-generated by Render
- `ALLOWED_ORIGINS` - Set to `*` or your mobile app domain

### 4. Deploy
Render will automatically deploy. Your API will be available at:
`https://family-budget-api.onrender.com`

## Error Handling

All errors return JSON in this format:
```json
{
  "detail": "Error message here"
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid/missing token)
- `404` - Not Found
- `500` - Server Error

## Security Notes

1. **JWT Tokens**: Expire after 24 hours - mobile app should handle re-authentication
2. **HTTPS Only**: Use HTTPS in production
3. **CORS**: Configure `ALLOWED_ORIGINS` properly for production
4. **Rate Limiting**: Consider adding rate limiting for production

## Testing with cURL

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

### Get Dashboard (with token)
```bash
curl -X GET http://localhost:8000/api/dashboard/1?year=2026&month=1 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Support

For issues or questions, refer to the main project README or create an issue on GitHub.
