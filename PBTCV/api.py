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
    payment_mode: Optional[str] = None
    payment_details: Optional[str] = None

class CopyAllocationsRequest(BaseModel):
    user_id: int
    from_year: int
    from_month: int
    to_year: int
    to_month: int

class FamilyRegistrationRequest(BaseModel):
    """Public family registration request for mobile/web"""
    family_name: str
    admin_email: str
    admin_name: str


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

@app.post("/api/families/create")
def create_family_public(request: FamilyRegistrationRequest):
    """
    Public endpoint for family self-registration (mobile/web)
    No authentication required - this is for new users
    """
    try:
        # Validate inputs
        if not request.family_name or not request.admin_email or not request.admin_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All fields are required"
            )
        
        # Email format validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, request.admin_email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email address format"
            )
        
        # Create household with admin using existing database method
        success, household_id, invite_token, message = db.create_household_with_admin(
            household_name=request.family_name,
            admin_email=request.admin_email,
            admin_name=request.admin_name
        )
        
        if not success:
            # Check for duplicate error
            if "already exists" in message.lower() or "duplicate" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This family name and email combination already exists"
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # Return success with invite token
        return {
            "status": "success",
            "message": "Family created successfully",
            "invite_token": invite_token,
            "household_id": household_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in family registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create family: {str(e)}"
        )


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
    db._execute(cursor, 'SELECT COUNT(*) as count FROM households')
    result = cursor.fetchone()
    total_households = result['count'] if result else 0
    
    # Get total users (excluding superadmin)
    db._execute(cursor, 'SELECT COUNT(*) as count FROM users WHERE role != %s', ('superadmin',))
    result = cursor.fetchone()
    total_users = result['count'] if result else 0
    
    return {
        "status": "success",
        "data": {
            "total_households": total_households,
            "total_users": total_users
        }
    }

@app.put("/api/admin/household/{household_id}/toggle")
def toggle_household(household_id: int, current_user: dict = Depends(verify_jwt_token)):
    """Toggle household active status (Super Admin only)"""
    if current_user.get('role') != 'superadmin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    
    success = db.toggle_household_status(household_id)
    
    if success:
        return {"status": "success", "message": "Household status toggled successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle household status"
        )

@app.delete("/api/admin/household/{household_id}")
def delete_household(household_id: int, current_user: dict = Depends(verify_jwt_token)):
    """Delete household and all its data (Super Admin only)"""
    if current_user.get('role') != 'superadmin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    
    success, message = db.delete_household(household_id)
    
    if success:
        return {"status": "success", "message": message}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )


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
    
    try:
        # Use the existing database method
        households_df = db.get_all_households()
        
        households = []
        for _, row in households_df.iterrows():
            households.append({
                "id": int(row['id']),
                "name": str(row['name']),
                "member_count": int(row.get('member_count', 0)),
                "admin_name": str(row.get('admin_name', 'No Admin')),
                "is_active": bool(row.get('is_active', True))
            })
        
        print(f"DEBUG: Returning {len(households)} households to super admin")
        return {
            "status": "success",
            "data": {
                "households": households
            }
        }
    except Exception as e:
        print(f"ERROR in get_all_households: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch households: {str(e)}"
        )

@app.get("/api/admin/users")
def get_all_users_admin(current_user: dict = Depends(verify_jwt_token)):
    """
    Get all users across all households (Super Admin only)
    """
    if current_user.get('role') != 'superadmin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    
    try:
        # Use the existing database method
        users_df = db.get_all_users_super_admin()
        
        users = []
        for _, row in users_df.iterrows():
            users.append({
                "id": int(row['id']),
                "email": str(row['email']),
                "full_name": str(row['full_name']),
                "role": str(row['role']),
                "household_id": int(row['household_id']) if row.get('household_id') else None,
                "household_name": str(row.get('household_name', 'N/A')),
                "relationship": str(row.get('relationship', 'N/A')),
                "is_active": bool(row.get('is_active', True))
            })
        
        print(f"DEBUG: Returning {len(users)} users to super admin")
        return {
            "status": "success",
            "data": {
                "users": users
            }
        }
    except Exception as e:
        print(f"ERROR in get_all_users_admin: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )

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
    print(f"DEBUG create_household_member:")
    print(f"  current_user: {current_user}")
    print(f"  user_id from JWT: {current_user['user_id']}")
    print(f"  user from DB: {user}")
    print(f"  household_id param: {household_id}")
    
    if not user:
        print(f"  ERROR: User not found")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not found"
        )
    
    print(f"  user household_id: {user['household_id']} (type: {type(user['household_id'])})")
    print(f"  param household_id: {household_id} (type: {type(household_id)})")
    print(f"  Match: {user['household_id'] == household_id}")
    
    if user['household_id'] != household_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied - wrong household (user: {user['household_id']}, requested: {household_id})"
        )
    
    # Check if user is admin
    print(f"  user role: {user['role']}")
    if user['role'] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only household admins can add members"
        )
    
    # Create member and get invite token
    success, member_id, invite_token = db.create_member(
        household_id=household_id,
        email=request.email,
        full_name=request.name,
        relationship=request.relationship,
        created_by_admin_id=current_user['user_id']
    )
    
    if not success:
        # Check if it's a duplicate email error
        error_msg = "Failed to create member"
        if member_id == "DUPLICATE_EMAIL":
            error_msg = f"A user with email '{request.email}' already exists in the system"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    return {
        "status": "success",
        "data": {
            "invite_token": invite_token,
            "message": f"Member {request.name} created successfully. Share this token with them."
        }
    }

@app.get("/api/households/{household_id}/members")
def get_household_members_list(
    household_id: int,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Get all members of a household (Admin only)
    """
    # Verify user is admin of this household
    user = db.get_user_by_id(current_user['user_id'])
    print(f"DEBUG get_household_members:")
    print(f"  current_user: {current_user}")
    print(f"  user_id from JWT: {current_user['user_id']}")
    print(f"  user from DB: {user}")
    print(f"  household_id param: {household_id}")
    
    if not user:
        print(f"  ERROR: User not found")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not found"
        )
    
    print(f"  user household_id: {user['household_id']} (type: {type(user['household_id'])})")
    print(f"  param household_id: {household_id} (type: {type(household_id)})")
    print(f"  Match: {user['household_id'] == household_id}")
    
    if user['household_id'] != household_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied - wrong household (user: {user['household_id']}, requested: {household_id})"
        )
    
    # Check if user is admin
    print(f"  user role: {user['role']}")
    if user['role'] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only household admins can view members"
        )
    
    try:
        members_df = db.get_household_members(household_id)
        
        # Convert DataFrame to list of dicts
        members = []
        for _, row in members_df.iterrows():
            members.append({
                "id": int(row['id']),
                "email": str(row['email']),
                "full_name": str(row['full_name']),
                "role": str(row['role']),
                "relationship": str(row.get('relationship', 'N/A')),
                "is_active": bool(row.get('is_active', True)),
                "invite_token": str(row.get('invite_token', '')) if row.get('invite_token') else None
            })
        
        print(f"DEBUG: Returning {len(members)} members for household {household_id}")
        return {
            "status": "success",
            "data": {
                "members": members
            }
        }
    except Exception as e:
        print(f"ERROR in get_household_members: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch members: {str(e)}"
        )

@app.delete("/api/households/{household_id}/members/{member_id}")
def delete_household_member(
    household_id: int,
    member_id: int,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Delete a household member (Admin only)
    """
    # Verify user is admin of this household
    user = db.get_user_by_id(current_user['user_id'])
    if not user or user['household_id'] != household_id or user['role'] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only household admins can delete members"
        )
    
    # Don't allow deleting yourself
    if member_id == current_user['user_id']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    success = db.delete_member(member_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete member"
        )
    
    return {
        "status": "success",
        "message": "Member deleted successfully"
    }

@app.post("/api/households/{household_id}/members/{member_id}/promote")
def promote_member(
    household_id: int,
    member_id: int,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Promote a member to admin (Super Admin only)
    """
    if current_user.get('role') != 'superadmin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admin can promote members"
        )
    
    success = db.promote_member_to_admin(member_id, household_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to promote member"
        )
    
    return {
        "status": "success",
        "message": "Member promoted to admin successfully"
    }

class CreateFamilyAdminRequest(BaseModel):
    household_name: str
    admin_name: str
    admin_email: str

@app.post("/api/admin/create-family")
def create_family_admin(
    request: CreateFamilyAdminRequest,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Create a new household with family admin (Super Admin only)
    """
    if current_user.get('role') != 'superadmin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admin can create families"
        )
    
    success, household_id, invite_token, message = db.create_household_with_admin(
        household_name=request.household_name,
        admin_email=request.admin_email,
        admin_name=request.admin_name
    )
    
    if not success:
        error_detail = message if message else "Failed to create family"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail
        )
    
    return {
        "status": "success",
        "data": {
            "invite_token": invite_token,
            "message": f"Family '{request.household_name}' created. Share this token with {request.admin_name}."
        }
    }

@app.get("/api/admin/households/{household_id}") 
def get_household_detail(
    household_id: int,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Get household details with members list (Super Admin only)
    """
    if current_user.get('role') != 'superadmin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    
    try:
        # Get household info
        cursor = db.conn.cursor()
        db._execute(cursor, 'SELECT id, name, is_active, created_at FROM households WHERE id = ?', (household_id,))
        household = cursor.fetchone()
        
        if not household:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Household not found"
            )
        
        # Get members
        members = db.get_household_members_for_admin(household_id)
        
        return {
            "status": "success",
            "data": {
                "household": dict(household),
                "members": members
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in get_household_detail: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch household details: {str(e)}"
        )

@app.patch("/api/admin/households/{household_id}/deactivate")
def deactivate_household(
    household_id: int,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Deactivate household (soft delete) - Super Admin only
    """
    if current_user.get('role') != 'superadmin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    
    success = db.toggle_household_status(household_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle household status"
        )
    
    return {
        "status": "success",
        "message": "Household status toggled successfully"
    }

@app.delete("/api/admin/households/{household_id}")
def delete_household_permanently(
    household_id: int,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Permanently delete household and ALL associated data (Super Admin only)
    WARNING: This is irreversible!
    """
    if current_user.get('role') != 'superadmin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    
    success, message = db.delete_household(household_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
    
    print(f"DEBUG Budget Calc - Period: {year}-{month}")
    print(f"DEBUG Budget Calc - Total Income: {total_income} (from {len(filtered_income)} income records)")
    print(f"DEBUG Budget Calc - Total Expenses: {total_expenses} (from {len(filtered_expenses)} expense records)")
    print(f"DEBUG Budget Calc - Allocations: allocated={total_allocated}, spent={total_spent}")
    
    if total_income > 0:
        # Force float division and log values for debugging
        budget_used_percentage = round((float(total_expenses) / float(total_income)) * 100, 2)
        print(f"DEBUG Budget Calc - Percentage: {budget_used_percentage}% (expenses/income * 100)")
    else:
        print(f"DEBUG Budget Calc - No income for period {year}-{month}, percentage set to 0")
    
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
    income_result = db.get_income_with_ids(user_id)
    
    if hasattr(income_result, 'to_dict'):
        income = income_result.to_dict('records') if not income_result.empty else []
    else:
        income = income_result if income_result else []
    
    # Filter by period if provided (same logic as expenses)
    if year and month:
        filtered = []
        for item in income:
            # Try both 'date' and 'Date' keys
            date_val = item.get('Date') or item.get('date', '')
            # Convert to string if it's a datetime object
            if hasattr(date_val, 'strftime'):
                date_str = date_val.strftime('%Y-%m-%d')
            else:
                date_str = str(date_val)
            
            # Check if date matches year-month pattern
            if date_str.startswith(f"{year}-{month:02d}"):
                filtered.append(item)
        income = filtered
    
    return {
        "status": "success",
        "data": income
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
def delete_income_endpoint(
    income_id: int,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Delete an income entry
    """
    user_id = current_user.get('user_id')
    
    if db.delete_income(income_id, user_id):
        return {
            "status": "success",
            "message": "Income deleted successfully"
        }
    else:
        raise HTTPException(status_code=400, detail="Failed to delete income")

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

@app.post("/api/admin/recalculate-allocations")
def recalculate_all_allocations(current_user: dict = Depends(verify_jwt_token)):
    """
    Recalculate all allocation spent amounts from actual expenses
    Fixes discrepancies from old logic that didn't filter by year/month
    Super admin only
    """
    if current_user.get('role') not in ['super', 'superadmin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    
    try:
        # Get all allocations
        conn = db.conn
        cursor = conn.cursor()
        
        # Use _execute helper for PostgreSQL compatibility
        db._execute(cursor, 'SELECT id, user_id, category, year, month, allocated_amount FROM allocations', ())
        allocations = cursor.fetchall()
        
        updated_count = 0
        
        for allocation in allocations:
            alloc_id = allocation['id']
            user_id = allocation['user_id']
            category = allocation['category']
            year = allocation['year']
            month = allocation['month']
            allocated_amount = float(allocation['allocated_amount'])
            
            # Calculate actual spent amount from expenses for this category/year/month
            db._execute(cursor, '''
                SELECT COALESCE(SUM(amount), 0) as total_spent
                FROM expenses
                WHERE user_id = ? 
                  AND category = ?
                  AND date LIKE ?
            ''', (user_id, category, f"{year}-{month:02d}%"))
            
            result = cursor.fetchone()
            actual_spent = float(result['total_spent'])
            new_balance = allocated_amount - actual_spent
            
            # Update the allocation
            db._execute(cursor, '''
                UPDATE allocations 
                SET spent_amount = ?, balance = ?
                WHERE id = ?
            ''', (actual_spent, new_balance, alloc_id))
            
            updated_count += 1
        
        conn.commit()
        
        return {
            "status": "success",
            "message": f"Successfully recalculated {updated_count} allocations",
            "updated_count": updated_count
        }
        
    except Exception as e:
        print(f"Error recalculating allocations: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to recalculate allocations: {str(e)}"
        )

def recalculate_allocation_for_category(user_id: int, category: str, year: int, month: int):
    """Helper function to recalculate a single allocation from actual expenses"""
    try:
        conn = db.conn
        cursor = conn.cursor()
        
        # Get the allocation for this category/period
        db._execute(cursor, '''
            SELECT id, allocated_amount 
            FROM allocations 
            WHERE user_id = ? AND category = ? AND year = ? AND month = ?
        ''', (user_id, category, year, month))
        
        allocation = cursor.fetchone()
        if not allocation:
            print(f"No allocation found for {category} {year}-{month:02d}")
            return
        
        # Calculate actual spent from expenses
        db._execute(cursor, '''
            SELECT COALESCE(SUM(amount), 0) as total_spent
            FROM expenses
            WHERE user_id = ? AND category = ? AND date LIKE ?
        ''', (user_id, category, f"{year}-{month:02d}%"))
        
        result = cursor.fetchone()
        actual_spent = float(result['total_spent'])
        allocated_amount = float(allocation['allocated_amount'])
        new_balance = allocated_amount - actual_spent
        
        # Update the allocation
        db._execute(cursor, '''
            UPDATE allocations 
            SET spent_amount = ?, balance = ?
            WHERE id = ?
        ''', (actual_spent, new_balance, allocation['id']))
        
        conn.commit()
        print(f"Recalculated {category} {year}-{month:02d}: spent={actual_spent}, balance={new_balance}")
        
    except Exception as e:
        print(f"Error in recalculate_allocation_for_category: {e}")
        import traceback
        traceback.print_exc()

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
        if not allocations_result.empty:
            # Make sure id is a column, not the index
            # If id is the index, reset it to be a column
            if 'id' not in allocations_result.columns and allocations_result.index.name == 'id':
                allocations_result = allocations_result.reset_index()
            elif 'id' not in allocations_result.columns:
                # If there's no id column at all, add row numbers as temporary IDs
                allocations_result = allocations_result.reset_index(drop=True)
                allocations_result['id'] = allocations_result.index
            
            allocations = allocations_result.to_dict('records')
            
            # DEBUG: Print what we're actually returning
            print(f"=== ALLOCATIONS API DEBUG ===")
            print(f"Number of allocations: {len(allocations)}")
            if allocations:
                print(f"First allocation keys: {list(allocations[0].keys())}")
                print(f"First allocation: {allocations[0]}")
        else:
            allocations = []
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
        request.user_id,
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
    user_id = current_user['user_id']
    print(f"Attempting to delete allocation: id={allocation_id}, user_id={user_id}")
    
    success = db.delete_allocation_by_id(allocation_id, user_id)
    
    print(f"Delete allocation result: {success}")
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete allocation id={allocation_id}. Either it doesn't exist or doesn't belong to user {user_id}"
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
    
    print(f"=== EXPENSES API DEBUG ===")
    print(f"User ID: {user_id}, Year: {year}, Month: {month}")
    print(f"Total expenses before filter: {len(expenses)}")
    if expenses:
        print(f"First expense keys: {list(expenses[0].keys())}")
        print(f"First expense: {expenses[0]}")
    
    # Filter by period if provided
    if year and month:
        filtered = []
        for e in expenses:
            # Try both 'date' and 'Date' keys (case-sensitive)
            date_val = e.get('Date') or e.get('date', '')
            # Convert to string if it's a datetime object
            if hasattr(date_val, 'strftime'):
                date_str = date_val.strftime('%Y-%m-%d')
            else:
                date_str = str(date_val)
            
            print(f"Checking expense: date_val={date_val}, date_str={date_str}, looking for {year}-{month:02d}")
            
            # Check if date matches year-month pattern
            if date_str.startswith(f"{year}-{month:02d}"):
                filtered.append(e)
                print(f"  -> MATCH!")
        expenses = filtered
        print(f"After filter: {len(expenses)} expenses")
    
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
    
    # Recalculate allocation for this category/period to ensure sync
    try:
        year, month = int(request.date[:4]), int(request.date[5:7])
        recalculate_allocation_for_category(request.user_id, request.category, year, month)
    except Exception as e:
        print(f"Warning: Failed to recalculate allocation: {e}")
    
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
    # Database signature: update_expense(expense_id, user_id, date, category, amount, old_category, old_amount, comment, subcategory, old_date, payment_mode, payment_details)
    success = db.update_expense(
        expense_id,
        request.user_id,
        request.date,
        request.category,
        request.amount,
        None,  # old_category
        None,  # old_amount
        request.comment,
        request.subcategory,
        None,  # old_date
        request.payment_mode,
        request.payment_details
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update expense"
        )
    
    # Recalculate allocation for this category/period
    try:
        year, month = int(request.date[:4]), int(request.date[5:7])
        recalculate_allocation_for_category(request.user_id, request.category, year, month)
    except Exception as e:
        print(f"Warning: Failed to recalculate allocation: {e}")
    
    return {
        "status": "success",
        "message": "Expense updated successfully"
    }

@app.delete("/api/expenses/{expense_id}")
def delete_expense(expense_id: int, current_user: dict = Depends(verify_jwt_token)):
    """
    Delete expense
    """
    # Get expense details before deleting for recalculation
    try:
        conn = db.conn
        cursor = conn.cursor()
        db._execute(cursor, 'SELECT user_id, category, date FROM expenses WHERE id = ?', (expense_id,))
        expense = cursor.fetchone()
        
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )
        
        user_id = expense['user_id']
        category = expense['category']
        date = expense['date']
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get expense details: {str(e)}"
        )
    
    success = db.delete_expense(expense_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete expense"
        )
    
    # Recalculate allocation for this category/period
    try:
        year, month = int(date[:4]), int(date[5:7])
        recalculate_allocation_for_category(user_id, category, year, month)
    except Exception as e:
        print(f"Warning: Failed to recalculate allocation: {e}")
    
    return {
        "status": "success",
        "message": "Expense deleted successfully"
    }

# ==================== Savings/Liquidity Endpoints ====================

@app.get("/api/savings/years/{user_id}")
def get_savings_years(
    user_id: int,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Get all years where income/allocation data exists for liquidity view
    """
    try:
        # Get user info to determine if admin
        user = db.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        is_admin = user['role'] == 'admin'
        household_id = user['household_id']
        
        years = db.get_savings_years(user_id, is_admin, household_id)
        
        return {
            "status": "success",
            "data": years
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in get_savings_years: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch savings years: {str(e)}"
        )

@app.get("/api/savings/liquidity/{user_id}/{year}")
def get_monthly_liquidity(
    user_id: int,
    year: int,
    current_user: dict = Depends(verify_jwt_token)
):
    """
    Get monthly liquidity (Income - Allocations) for a specific year
    Returns different data structure for admin vs member
    """
    try:
        # Get user info to determine if admin
        user = db.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        is_admin = user['role'] == 'admin'
        household_id = user['household_id']
        
        # Get liquidity data
        liquidity_df = db.get_monthly_liquidity_by_member_simple(
            household_id, year, is_admin, user_id
        )
        
        # Convert DataFrame to list of dicts
        if hasattr(liquidity_df, 'to_dict'):
            liquidity_data = liquidity_df.to_dict('records') if not liquidity_df.empty else []
        else:
            liquidity_data = liquidity_df if liquidity_df else []
        
        return {
            "status": "success",
            "data": {
                "year": year,
                "is_admin": is_admin,
                "liquidity": liquidity_data
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in get_monthly_liquidity: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch monthly liquidity: {str(e)}"
        )

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
