"""
FastAPI Backend for Family Budget Tracker Mobile App
Reuses existing MultiUserDB logic with JWT authentication
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
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

# Initialize database connection with Render-compatible URL handling
def get_database_url():
    """Get database URL and ensure PostgreSQL dialect compatibility"""
    db_url = os.getenv('DATABASE_URL')
    if db_url and db_url.startswith('postgres://'):
        # Fix for SQLAlchemy - replace postgres:// with postgresql://
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    return db_url

# Set the corrected DATABASE_URL back to environment
if get_database_url():
    os.environ['DATABASE_URL'] = get_database_url()

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
    email: str
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
    except (jwt.DecodeError, jwt.InvalidTokenError, Exception):
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
    # authenticate_user returns (success: bool, user_dict or None)
    success, user_data = db.authenticate_user(request.email, request.password)
    
    if not success or not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # user_data is already a dict
    user = user_data
    
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

@app.post("/api/auth/setup-password")
def setup_password(request: AcceptInviteRequest):
    """
    Setup password for new user (alias for accept-invite)
    """
    return accept_invite(request)

# ==================== Super Admin Endpoints ====================

@app.get("/api/admin/stats")
def get_admin_stats(current_user: dict = Depends(verify_jwt_token)):
    """
    Get system statistics (Super Admin only)
    """
    if current_user.get('role') != 'superadmin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    
    # Get total households
    cursor = db.conn.cursor()
    db._execute(cursor, 'SELECT COUNT(*) FROM households')
    total_households = cursor.fetchone()[0]
    
    # Get total users
    db._execute(cursor, 'SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    return {
        "status": "success",
        "data": {
            "total_households": total_households,
            "total_users": total_users
        }
    }

@app.get("/api/admin/households")
def get_all_households(current_user: dict = Depends(verify_jwt_token)):
    """
    Get all households (Super Admin only)
    """
    if current_user.get('role') != 'superadmin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    
    cursor = db.conn.cursor()
    db._execute(cursor, '''
        SELECT h.id, h.name, 
               COUNT(DISTINCT u.id) as member_count,
               MAX(CASE WHEN u.role = 'admin' THEN u.full_name END) as admin_name
        FROM households h
        LEFT JOIN users u ON h.id = u.household_id
        GROUP BY h.id, h.name
        ORDER BY h.name
    ''')
    
    households = []
    for row in cursor.fetchall():
        households.append({
            "id": row[0],
            "name": row[1],
            "member_count": row[2] or 0,
            "admin_name": row[3] or "No Admin",
            "is_active": True  # Add actual status field if needed
        })
    
    return {
        "status": "success",
        "data": {
            "households": households
        }
    }

# ==================== Household/Family Admin Endpoints ====================

class CreateMemberRequest(BaseModel):
    name: str
    email: str
    relationship: str

@app.post("/api/households/{household_id}/members")
def create_household_member(
    household_id: int,
    request: CreateMemberRequest,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Create a new family member (Family Admin only)
    """
    # Verify user is admin of this household
    user = db.get_user_by_id(current_user['user_id'])
    if not user or user['household_id'] != household_id or user['role'] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only household admins can add members"
        )
    
    # Create member and get invite token
    success, result = db.create_member(
        household_id=household_id,
        email=request.email,
        full_name=request.name,
        relationship=request.relationship,
        created_by_admin_id=current_user['user_id']
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result
        )
    
    return {
        "status": "success",
        "data": {
            "invite_token": result,
            "message": f"Member {request.name} created successfully. Share this token with them."
        }
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
    
    # Get income (returns DataFrame)
    income_df = db.get_all_income(user_id)
    income_list = income_df.to_dict('records') if not income_df.empty else []
    # Filter by period
    filtered_income = [i for i in income_list if str(i.get('Date', '')).startswith(f"{year}-{month:02d}")]
    total_income = sum(item.get('Amount', 0) for item in filtered_income)
    
    # Get expenses (returns DataFrame)
    expenses_df = db.get_all_expenses(user_id)
    expenses_list = expenses_df.to_dict('records') if not expenses_df.empty else []
    # Filter by period
    filtered_expenses = [e for e in expenses_list if str(e.get('Date', '')).startswith(f"{year}-{month:02d}")]
    total_expenses = sum(item.get('Amount', 0) for item in filtered_expenses)
    
    # Get allocations (returns list of dicts)
    allocations_result = db.get_all_allocations(user_id, year, month)
    # Check if it's a DataFrame
    if hasattr(allocations_result, 'to_dict'):
        allocations_list = allocations_result.to_dict('records') if not allocations_result.empty else []
    else:
        allocations_list = allocations_result if allocations_result else []
    
    total_allocated = sum(item.get('allocated_amount', 0) for item in allocations_list)
    total_spent = sum(item.get('spent_amount', 0) for item in allocations_list)
    
    # Calculate budget used percentage (total_expenses / total_income * 100)
    budget_used_percentage = 0
    if total_income > 0:
        # Force float division and log values for debugging
        budget_used_percentage = round((float(total_expenses) / float(total_income)) * 100, 2)
        print(f"DEBUG Budget Calc - Income: {total_income}, Expenses: {total_expenses}, Percentage: {budget_used_percentage}%")
    else:
        print(f"DEBUG Budget Calc - No income for period {year}-{month}")
    
    return {
        "status": "success",
        "data": {
            "period": {"year": year, "month": month},
            "income": {
                "total": total_income,
                "count": len(filtered_income)
            },
            "expenses": {
                "total": total_expenses,
                "count": len(filtered_expenses)
            },
            "allocations": {
                "allocated": total_allocated,
                "spent": total_spent,
                "balance": total_allocated - total_spent,
                "count": len(allocations_list)
            },
            "savings": total_income - total_expenses,
            "budget_used_percentage": budget_used_percentage
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
    income_result = db.get_all_income(user_id)
    
    # Convert DataFrame to list of dicts if needed
    if hasattr(income_result, 'to_dict'):
        income_list = income_result.to_dict('records') if not income_result.empty else []
    else:
        income_list = income_result if income_result else []
    
    # Filter by period if provided
    if year and month:
        income_list = [i for i in income_list if i.get('date', '').startswith(f"{year}-{month:02d}")]
    
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
    allocations_result = db.get_all_allocations(user_id, year, month)
    
    # Convert DataFrame to list of dicts if needed
    if hasattr(allocations_result, 'to_dict'):
        allocations = allocations_result.to_dict('records') if not allocations_result.empty else []
    else:
        allocations = allocations_result if allocations_result else []
    
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
    expenses_result = db.get_all_expenses(user_id)
    
    # Convert DataFrame to list of dicts if needed
    if hasattr(expenses_result, 'to_dict'):
        expenses = expenses_result.to_dict('records') if not expenses_result.empty else []
    else:
        expenses = expenses_result if expenses_result else []
    
    # Filter by period if provided
    if year and month:
        expenses = [e for e in expenses if e.get('date', '').startswith(f"{year}-{month:02d}")]
    
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
        request.amount,
        request.comment,
        request.subcategory
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

@app.get("/")
def root():
    """
    Root endpoint - Render uses this to check if deployment succeeded
    """
    return {
        "status": "alive",
        "message": "Family Budget Tracker API is running",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
