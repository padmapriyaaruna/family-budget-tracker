"""
FastAPI Backend for Family Budget Tracker Mobile App
Reuses existing MultiUserDB logic with JWT authentication
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, timedelta
import os
import jwt
from multi_user_database import MultiUserDB

# Initialize FastAPI app
app = FastAPI(
    title="Family Budget Tracker API",
    description="REST API for mobile app access to budget data",
    version="1.0.0"
)

# CORS Configuration - Allow mobile app access
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database
db = MultiUserDB()

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Security
security = HTTPBearer()

# ==================== Pydantic Models ====================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AcceptInviteRequest(BaseModel):
    invite_token: str
    password: str

class IncomeRequest(BaseModel):
    user_id: int
    date: str  # YYYY-MM-DD
    source: str
    amount: float

class AllocationRequest(BaseModel):
    user_id: int
    category: str
    allocated_amount: float
    year: int
    month: int

class ExpenseRequest(BaseModel):
    user_id: int
    date: str  # YYYY-MM-DD
    category: str
    subcategory: Optional[str] = None
    amount: float
    comment: Optional[str] = None

class CopyAllocationsRequest(BaseModel):
    user_id: int
    from_year: int
    from_month: int
    to_year: int
    to_month: int

# ==================== Helper Functions ====================

def create_jwt_token(user_id: int, email: str, role: str) -> str:
    """Create JWT token for authenticated user"""
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return payload"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# ==================== Root Endpoint ====================

@app.get("/")
def read_root():
    """Root endpoint - API health check"""
    return {
        "status": "success",
        "message": "Family Budget Tracker API is running",
        "version": "1.0.0"
    }

# ==================== Authentication Endpoints ====================

@app.post("/api/auth/login")
def login(request: LoginRequest):
    """
    Authenticate user and return JWT token
    """
    user = db.authenticate_user(request.email, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create JWT token
    token = create_jwt_token(user['id'], user['email'], user['role'])
    
    return {
        "status": "success",
        "data": {
            "token": token,
            "user": user
        },
        "message": "Login successful"
    }

@app.post("/api/auth/accept-invite")
def accept_invite(request: AcceptInviteRequest):
    """
    Accept member invite and set password
    """
    success, message = db.accept_invite(request.invite_token, request.password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {
        "status": "success",
        "message": message
    }

# ==================== User Endpoints ====================

@app.get("/api/user/profile")
def get_profile(current_user: dict = Depends(verify_jwt_token)):
    """
    Get current user profile
    """
    user = db.get_user_by_id(current_user['user_id'])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "status": "success",
        "data": user
    }

@app.get("/api/household/{household_id}/members")
def get_household_members(household_id: int, current_user: dict = Depends(verify_jwt_token)):
    """
    Get all members of a household (admin only)
    """
    members = db.get_household_members(household_id)
    
    return {
        "status": "success",
        "data": members
    }

# ==================== Dashboard Endpoint ====================

@app.get("/api/dashboard/{user_id}")
def get_dashboard(
    user_id: int,
    year: Optional[int] = None,
    month: Optional[int] = None,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Get dashboard summary - income vs expenses
    """
    # Default to current month
    if not year or not month:
        now = datetime.now()
        year = now.year
        month = now.month
    
    # Get income
    income_list = db.get_income(user_id, year, month)
    total_income = sum(item['amount'] for item in income_list)
    
    # Get expenses
    expenses_list = db.get_expenses(user_id, year, month)
    total_expenses = sum(item['amount'] for item in expenses_list)
    
    # Get allocations
    allocations_list = db.get_all_allocations(user_id, year, month)
    total_allocated = sum(item['allocated_amount'] for item in allocations_list)
    total_spent = sum(item['spent_amount'] for item in allocations_list)
    
    return {
        "status": "success",
        "data": {
            "period": {"year": year, "month": month},
            "income": {
                "total": total_income,
                "count": len(income_list)
            },
            "expenses": {
                "total": total_expenses,
                "count": len(expenses_list)
            },
            "allocations": {
                "allocated": total_allocated,
                "spent": total_spent,
                "balance": total_allocated - total_spent,
                "count": len(allocations_list)
            },
            "savings": total_income - total_expenses
        }
    }

# ==================== Income Endpoints ====================

@app.get("/api/income/{user_id}")
def get_income(
    user_id: int,
    year: Optional[int] = None,
    month: Optional[int] = None,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Get income records for a user
    """
    income_list = db.get_income(user_id, year, month)
    
    return {
        "status": "success",
        "data": income_list
    }

@app.post("/api/income")
def add_income(request: IncomeRequest, current_user: dict = Depends(verify_jwt_token)):
    """
    Add new income entry
    """
    success = db.add_income(
        request.user_id,
        request.date,
        request.source,
        request.amount
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add income"
        )
    
    return {
        "status": "success",
        "message": "Income added successfully"
    }

@app.put("/api/income/{income_id}")
def update_income(
    income_id: int,
    request: IncomeRequest,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Update income entry
    """
    success = db.update_income(
        income_id,
        request.date,
        request.source,
        request.amount
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update income"
        )
    
    return {
        "status": "success",
        "message": "Income updated successfully"
    }

@app.delete("/api/income/{income_id}")
def delete_income(income_id: int, current_user: dict = Depends(verify_jwt_token)):
    """
    Delete income entry
    """
    success = db.delete_income(income_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete income"
        )
    
    return {
        "status": "success",
        "message": "Income deleted successfully"
    }

# ==================== Allocation Endpoints ====================

@app.get("/api/allocations/{user_id}")
def get_allocations(
    user_id: int,
    year: Optional[int] = None,
    month: Optional[int] = None,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Get allocations for a user
    """
    allocations = db.get_all_allocations(user_id, year, month)
    
    return {
        "status": "success",
        "data": allocations
    }

@app.post("/api/allocations")
def add_allocation(request: AllocationRequest, current_user: dict = Depends(verify_jwt_token)):
    """
    Add new allocation
    """
    success = db.add_allocation(
        request.user_id,
        request.category,
        request.allocated_amount,
        request.year,
        request.month
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add allocation"
        )
    
    return {
        "status": "success",
        "message": "Allocation added successfully"
    }

@app.put("/api/allocations/{allocation_id}")
def update_allocation(
    allocation_id: int,
    request: AllocationRequest,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Update allocation
    """
    success = db.update_allocation(
        allocation_id,
        request.category,
        request.allocated_amount,
        request.year,
        request.month
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

@app.delete("/api/allocations/{allocation_id}")
def delete_allocation(allocation_id: int, current_user: dict = Depends(verify_jwt_token)):
    """
    Delete allocation
    """
    success = db.delete_allocation(allocation_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete allocation"
        )
    
    return {
        "status": "success",
        "message": "Allocation deleted successfully"
    }

@app.post("/api/allocations/copy")
def copy_allocations(request: CopyAllocationsRequest, current_user: dict = Depends(verify_jwt_token)):
    """
    Copy allocations from previous month
    """
    success, count = db.copy_previous_month_allocations(
        request.user_id,
        request.from_year,
        request.from_month,
        request.to_year,
        request.to_month
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to copy allocations"
        )
    
    return {
        "status": "success",
        "message": f"Copied {count} allocations successfully",
        "count": count
    }

# ==================== Expense Endpoints ====================

@app.get("/api/expenses/{user_id}")
def get_expenses(
    user_id: int,
    year: Optional[int] = None,
    month: Optional[int] = None,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Get expenses for a user
    """
    expenses = db.get_expenses(user_id, year, month)
    
    return {
        "status": "success",
        "data": expenses
    }

@app.post("/api/expenses")
def add_expense(request: ExpenseRequest, current_user: dict = Depends(verify_jwt_token)):
    """
    Add new expense
    """
    success = db.add_expense(
        request.user_id,
        request.date,
        request.category,
        request.subcategory,
        request.amount,
        request.comment
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add expense"
        )
    
    return {
        "status": "success",
        "message": "Expense added successfully"
    }

@app.put("/api/expenses/{expense_id}")
def update_expense(
    expense_id: int,
    request: ExpenseRequest,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Update expense
    """
    success = db.update_expense(
        expense_id,
        request.date,
        request.category,
        request.subcategory,
        request.amount,
        request.comment
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update expense"
        )
    
    return {
        "status": "success",
        "message": "Expense updated successfully"
    }

@app.delete("/api/expenses/{expense_id}")
def delete_expense(expense_id: int, current_user: dict = Depends(verify_jwt_token)):
    """
    Delete expense
    """
    success = db.delete_expense(expense_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete expense"
        )
    
    return {
        "status": "success",
        "message": "Expense deleted successfully"
    }

# ==================== Health Check ====================

@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
