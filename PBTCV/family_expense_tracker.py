"""
Family Budget Tracker - Multi-User Version
Streamlit application with admin and member dashboards
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from multi_user_database import MultiUserDB
import config

# Try to import debug chatbot widget
try:
    from chatbot_widget_simple import render_chatbot_sidebar_simple as render_chatbot_sidebar
    print("✅ Simple chatbot widget imported")
except Exception as e:
    print(f"⚠️ Debug widget error: {e}")
    def render_chatbot_sidebar():
        import streamlit as st
        with st.sidebar:
            st.error(f"Chatbot import failed: {e}")

# Page configuration
st.set_page_config(
    page_title="Family Budget Tracker",
    page_icon="👨‍👩‍👧‍👦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS styling
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    [data-testid="stMetricValue"] {
        font-size: 24px;
    }
    
    /* Hide default Streamlit header */
    header[data-testid="stHeader"] {
        display: none;
    }
    
    /* Hide Streamlit menu button */
    #MainMenu {
        visibility: hidden;
    }
    
    /* Hide footer */
    footer {
        visibility: hidden;
    }
    
    /* Excel-like table styling - minimal and clean */
    [data-testid="column"] {
        border-right: 1px solid #e0e0e0;
        padding: 4px 8px !important;
    }
    
    [data-testid="column"]:last-child {
        border-right: none;
    }
    
    /* Compact buttons */
    .stButton button {
        padding: 4px 10px;
        font-size: 13px;
        height: 30px;
    }

    .login-container {
       max-width: 500px;
        margin: auto;
        padding: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database 
@st.cache_resource
def get_database():
    return MultiUserDB()

try:
    db = get_database()
except Exception as e:
    st.error(f"⚠️ Database error: {str(e)}")
    st.stop()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None

# Initialize budget period context (shared across Income, Allocation, Expenses tabs)
if 'budget_year' not in st.session_state:
    st.session_state.budget_year = datetime.now().year
if 'budget_month' not in st.session_state:
    st.session_state.budget_month = datetime.now().month

# ==================== AUTHENTICATION PAGES ====================


def show_login_page():
    """Display landing page with role-based navigation or specific login screen"""
    
    # Initialize navigation state
    if 'login_page' not in st.session_state:
        st.session_state.login_page = None
    
    # Show appropriate page based on navigation state
    if st.session_state.login_page is None:
        show_landing_page()
    elif st.session_state.login_page == 'master':
        show_master_login()
    elif st.session_state.login_page == 'admin':
        show_admin_login()
    elif st.session_state.login_page == 'member':
        show_member_login()
    elif st.session_state.login_page == 'setup':
        show_password_setup()
    elif st.session_state.login_page == 'create_family':
        show_family_registration()


def show_landing_page():
    """Display main landing page with 4 navigation buttons"""
    
    # Add custom styling for landing page with flexbox header
    st.markdown("""
    <style>
        /* Landing page header bar */
        .landing-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem 2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            border-radius: 0 0 15px 15px;
            margin: 0 auto 2rem auto;
            max-width: 100%;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .landing-logo {
            font-size: 3rem;
            line-height: 1;
        }
        
        .landing-title-text {
            color: white;
            font-size: 2.2rem;
            font-weight: bold;
            margin: 0;
            text-align: center;
        }
        
        .landing-subtitle {
            color: rgba(255, 255, 255, 0.95);
            font-size: 1rem;
            margin: 0;
            text-align: center;
        }
        
        @media (max-width: 768px) {
            .landing-header {
                flex-direction: column;
                gap: 0.5rem;
            }
            .landing-title-text {
                font-size: 1.8rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Landing page header with flexbox
    st.markdown("""
    <div class="landing-header">
        <div class="landing-logo">👨‍👩‍👧‍👦</div>
        <div>
            <div class="landing-title-text">Family Budget Tracker</div>
            <div class="landing-subtitle">Multi-Family Budget Management System</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the buttons below the header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Choose Your Role")
        st.markdown("")
        
        if st.button("🔱 Master", use_container_width=True, key="btn_master"):
            st.session_state.login_page = 'master'
            st.rerun()
        
        if st.button("👨‍👩‍👧 Family Admin", use_container_width=True, key="btn_admin"):
            st.session_state.login_page = 'admin'
            st.rerun()
        
        if st.button("👤 Family Member", use_container_width=True, key="btn_member"):
            st.session_state.login_page = 'member'
            st.rerun()
        
        # Password Setup with submenu
        if 'password_setup_menu' not in st.session_state:
            st.session_state.password_setup_menu = False
        
        if not st.session_state.password_setup_menu:
            if st.button("🔑 Password Setup", use_container_width=True, key="btn_setup"):
                st.session_state.password_setup_menu = True
                st.rerun()
        else:
            st.markdown("---")
            st.markdown("#### Password Management")
            st.markdown("")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🆕 New Password", use_container_width=True, key="btn_new_pwd", help="Set up password for new users"):
                    st.session_state.login_page = 'setup'
                    st.session_state.password_setup_menu = False
                    st.rerun()
            
            with col_b:
                st.button("🔄 Reset Password", use_container_width=True, key="btn_reset_pwd", disabled=True, help="Coming soon")
            
            st.markdown("")
            if st.button("← Back", use_container_width=True, key="btn_back_setup"):
                st.session_state.password_setup_menu = False
                st.rerun()
        
        # Separator and Create Family button
        st.markdown("---")
        st.markdown("### Don't have an account?")
        st.markdown("")
        
        if st.button("🏠 Create New Family", use_container_width=True, key="btn_create_family", type="primary"):
            st.session_state.login_page = 'create_family'
            st.session_state.password_setup_menu = False
            st.rerun()



def show_master_login():
    """Display Master login (password-only for superadmin)"""
    # Add spacing for visibility
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Home"):
        st.session_state.login_page = None
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.title("🔱 Master Login")
    st.info("For system administrators only. Manage multiple families and users.")
    
    with st.form("master_login_form"):
        master_password = st.text_input("Password", type="password", key="master_password")
        master_submit = st.form_submit_button("Login", use_container_width=True)
        
        if master_submit:
            if master_password:
                # Automatically use 'superadmin' as username
                success, user_data = db.authenticate_user('superadmin', master_password)
                if success and user_data.get('role') == 'superadmin':
                    st.session_state.logged_in = True
                    st.session_state.user = user_data
                    st.session_state.login_page = None  # Reset navigation
                    st.success(f"Welcome, {user_data['full_name']}!")
                    st.rerun()
                else:
                    st.error("Invalid master password or account not found")
            else:
                st.error("Please enter the master password")


def show_admin_login():
    """Display Family Admin login"""
    # Add spacing for visibility
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Home"):
        st.session_state.login_page = None
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.title("👨‍👩‍👧 Family Admin Login")
    st.info("Login to manage your family household. Contact super admin if you don't have an account.")
    
    with st.form("admin_login_form"):
        admin_email = st.text_input("Email", placeholder="your.email@example.com", key="admin_email")
        admin_password = st.text_input("Password", type="password", key="admin_password")
        admin_submit = st.form_submit_button("Login as Family Admin", use_container_width=True)
        
        if admin_submit:
            if admin_email and admin_password:
                success, user_data = db.authenticate_user(admin_email, admin_password)
                if success and user_data.get('role') == 'admin':
                    st.session_state.logged_in = True
                    st.session_state.user = user_data
                    st.session_state.login_page = None  # Reset navigation
                    st.success(f"Welcome, {user_data['full_name']}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials or not a family admin account")
            else:
                st.error("Please enter both email and password")


def show_member_login():
    """Display Family Member login"""
    # Add spacing for visibility
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Home"):
        st.session_state.login_page = None
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.title("👤 Family Member Login")
    st.info("Login to track your personal expenses. Use the invite token to set up your account first.")
    
    with st.form("member_login_form"):
        member_email = st.text_input("Email", placeholder="your.email@example.com", key="member_email")
        member_password = st.text_input("Password", type="password", key="member_password")
        member_submit = st.form_submit_button("Login as Member", use_container_width=True)
        
        if member_submit:
            if member_email and member_password:
                success, user_data = db.authenticate_user(member_email, member_password)
                if success and user_data.get('role') == 'member':
                    st.session_state.logged_in = True
                    st.session_state.user = user_data
                    st.session_state.login_page = None  # Reset navigation
                    st.success(f"Welcome, {user_data['full_name']}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials or not a member account")
            else:
                st.error("Please enter both email and password")


def show_password_setup():
    """Display password setup for new members"""
    # Add spacing for visibility
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Home"):
        st.session_state.login_page = None
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.title("🔑 Setup Your Password")
    st.info("If you were invited as a family member, use your invite token to set up your password")
    
    with st.form("password_setup_form"):
        invite_token = st.text_input("Invite Token", placeholder="Paste the token shared by your family admin")
        new_password = st.text_input("New Password", type="password")
        confirm_new_password = st.text_input("Confirm Password", type="password")
        
        submit_password = st.form_submit_button("Set Password", use_container_width=True)
        
        if submit_password:
            if not all([invite_token, new_password, confirm_new_password]):
                st.error("Please fill all fields")
            elif new_password != confirm_new_password:
                st.error("Passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                success, message = db.accept_invite(invite_token, new_password)
                if success:
                    st.success(f"✅ {message}")
                    st.info("You can now login with your email using the 'Family Member' button!")
                else:
                    st.error(f"❌ {message}")


def show_family_registration():
    """Display public family registration form"""
    import re
    import requests
    
    # Add spacing for visibility
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Home"):
        st.session_state.login_page = None
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.title("🏠 Create Your Family Account")
    st.info("Register your family to start tracking your budget together!")
    
    with st.form("family_registration_form"):
        # Family Name
        family_name = st.text_input(
            "Family Name *",
            placeholder="e.g., The Sharma Family",
            help="This will identify your household"
        )
        
        # Admin Email
        admin_email = st.text_input(
            "Your Email Address *",
            placeholder="admin@example.com",
            help="You will be the family administrator"
        )
        
        # Admin Name
        admin_name = st.text_input(
            "Your Full Name *",
            placeholder="Raj Sharma"
        )
        
        # Submit button
        submitted = st.form_submit_button(
            "Create Family Account",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            # Validation
            if not family_name or not admin_email or not admin_name:
                st.error("⚠️ Please fill all required fields")
            else:
                # Email format validation
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, admin_email):
                    st.error("⚠️ Please enter a valid email address")
                else:
                    # Call database method directly
                    try:
                        success, household_id, invite_token, message = db.create_household_with_admin(
                            household_name=family_name,
                            admin_email=admin_email,
                            admin_name=admin_name
                        )
                        
                        if success:
                            st.success("✅ Family created successfully!")
                            
                            # Show invite token
                            st.markdown("---")
                            st.subheader("🔑 Your Invite Token")
                            st.info(
                                "**Important:** Save this token to set your password!"
                            )
                            st.code(invite_token, language=None)
                            
                            st.markdown("---")
                            st.markdown("### Next Steps:")
                            st.markdown("""
                            1. **Save your invite token** (shown above)
                            2. Click "← Back to Home"
                            3. Select **🔑 Password Setup** → **🆕 New Password**
                            4. Enter your invite token and create your password
                            5. Login as **👨‍👩‍👧‍👦 Family Admin** with your email and password
                            """)
                            
                        else:
                            # Check for duplicate error
                            if "already exists" in message.lower() or "duplicate" in message.lower():
                                st.error(f"❌ This family name and email combination already exists!")
                            else:
                                st.error(f"❌ {message}")
                                
                    except Exception as e:
                        st.error(f"❌ Error creating family: {str(e)}")





# ==================== HELPER FUNCTIONS FOR ADVANCED FILTERING ====================

def get_user_available_periods(db, user_ids):
    """Get available year/month combinations for selected user(s)"""
    if not user_ids:
        return {'years': set(), 'months_by_year': {}, 'all_periods': set()}
    
    all_periods = set()
    
    for user_id in user_ids:
        # Get allocations
        try:
            cursor = db.conn.cursor()
            db._execute(cursor, 'SELECT DISTINCT year, month FROM allocations WHERE user_id = ?', (user_id,))
            for row in cursor.fetchall():
                all_periods.add((int(row['year']), int(row['month'])))
        except:
            pass
        
        # Get income
        try:
            income_df = db.get_income_with_ids(user_id)
            if not income_df.empty:
                income_df['date_parsed'] = pd.to_datetime(income_df['date'])
                for _, row in income_df.iterrows():
                    all_periods.add((row['date_parsed'].year, row['date_parsed'].month))
        except:
            pass
        
        # Get expenses
        try:
            expense_df = db.get_expenses_with_ids(user_id)
            if not expense_df.empty:
                expense_df['date_parsed'] = pd.to_datetime(expense_df['date'])
                for _, row in expense_df.iterrows():
                    all_periods.add((row['date_parsed'].year, row['date_parsed'].month))
        except:
            pass
    
    years = set()
    months_by_year = {}
    for year, month in all_periods:
        years.add(year)
        if year not in months_by_year:
            months_by_year[year] = set()
        months_by_year[year].add(month)
    
    return {'years': years, 'months_by_year': months_by_year, 'all_periods': all_periods}


# ==================== ADMIN DASHBOARD ====================

def show_admin_dashboard():
    """Display family admin dashboard"""
    st.header("👨‍👩‍👧 Family Admin Dashboard")
    user = st.session_state.user
    household_id = user['household_id']
    
    st.caption(f"Admin: {user['full_name']}")
    
    # Logout button
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()
    
    st.divider()
    
    # Tabs for admin functions
    tab1, tab2, tab3 = st.tabs(["💰 My Expenses", "📊 Family Overview", "👥 Manage Members"])
    
    # TAB 1: Admin's Personal Expenses
    with tab1:
        st.header("💰 My Personal Expenses")
        st.caption("Track your own income and expenses")
        
        # Reuse member dashboard for admin's personal tracking
        show_member_expense_tracking(user['id'])
    
    # TAB 2: Family Overview
    with tab2:
        st.header("📊 Family Financial Overview")
        
        # Get household members
        members_df = db.get_household_members(household_id)
        
        if members_df.empty:
            st.info("No family members found. Add members in the 'Manage Members' tab.")
        else:
            # Prepare member options
            member_options = {row['full_name']: row['id'] for _, row in members_df.iterrows()}
            member_names = list(member_options.keys())
            
            # Initialize session state for filters
            if 'filter_selected_members' not in st.session_state:
                # Default to admin
                admin_name = user['full_name']
                st.session_state.filter_selected_members = [admin_name] if admin_name in member_names else member_names[:1]
            
            if 'filter_selected_years' not in st.session_state:
                st.session_state.filter_selected_years = [datetime.now().year]
            
            if 'filter_selected_months' not in st.session_state:
                st.session_state.filter_selected_months = [datetime.now().month]
            
            # Create filter UI
            st.subheader("🔍 Filters")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                selected_member_names = st.multiselect(
                    "👥 Family Members",
                    options=member_names,
                    default=st.session_state.filter_selected_members,
                    key="member_filter",
                    help="Select one or more family members to view their financial data. Multiple selections show combined data (union)."
                )
                # Update session state
                if selected_member_names:
                    st.session_state.filter_selected_members = selected_member_names
                
                # Show info if no members selected
                if not selected_member_names:
                    st.info("👥 Select family members to view their available periods")
            
            # Get selected member IDs
            selected_member_ids = [member_options[name] for name in selected_member_names] if selected_member_names else []
            
            # Get available periods for selected members
            available_data = get_user_available_periods(db, selected_member_ids) if selected_member_ids else {'years': set(), 'months_by_year': {}, 'all_periods': set()}
            available_years = available_data['years']
            available_months_by_year = available_data['months_by_year']
            
            # Show warning if members selected but no data exists
            if selected_member_ids and not available_years:
                st.warning("⚠️ No financial data found for selected members. Add income, expenses, or allocations first.")
            
            # Define year range (dynamically extend if past July)
            current_year = datetime.now().year
            current_month = datetime.now().month
            # If past July, add one more future year for planning next year's budget
            if current_month >= 7:
                all_years = list(range(current_year - 5, current_year + 3))  # Last 5 years + next 2 years
            else:
                all_years = list(range(current_year - 5, current_year + 2))  # Last 5 years + next year
            
            with col2:
                # Format year options with visual prefix for unavailable years
                year_options = []
                year_mapping = {}
                for year in all_years:
                    if year in available_years:
                        label = str(year)
                    else:
                        label = f"⊘ {year} (No Data)"
                    year_options.append(label)
                    year_mapping[label] = year
                
                # Get previously selected years that are still valid
                prev_years_labels = [str(y) if y in available_years else f"⊘ {y} (No Data)" for y in st.session_state.filter_selected_years if y in all_years]
                if not prev_years_labels:
                    # Default to current year if available
                    if current_year in available_years:
                        prev_years_labels = [str(current_year)]
                    elif available_years:
                        # Default to most recent year with data
                        prev_years_labels = [str(max(available_years))]
                
                selected_year_labels = st.multiselect(
                    "📅 Years",
                    options=year_options,
                    default=prev_years_labels,
                    key="year_filter",
                    help="Select years to view. Options marked with ⊘ have no data for selected members."
                )
                
                # Parse selected years
                selected_years = [year_mapping[label] for label in selected_year_labels]
                st.session_state.filter_selected_years = selected_years
            
            with col3:
                # Get available months for selected years (union of all months across selected years)
                available_months_for_selection = set()
                for year in selected_years:
                    if year in available_months_by_year:
                        available_months_for_selection.update(available_months_by_year[year])
                
                # Format month options with visual prefix for unavailable months
                import calendar
                all_months = list(range(1, 13))
                month_options = []
                month_mapping = {}
                for month in all_months:
                    month_name = calendar.month_name[month]
                    if month in available_months_for_selection:
                        label = month_name
                    else:
                        label = f"⊘ {month_name} (No Data)"
                    month_options.append(label)
                    month_mapping[label] = month
                
                # Get previously selected months that are still valid
                prev_months_labels = [
                    calendar.month_name[m] if m in available_months_for_selection else f"⊘ {calendar.month_name[m]} (No Data)"
                    for m in st.session_state.filter_selected_months if 1 <= m <= 12
                ]
                if not prev_months_labels and available_months_for_selection:
                    # Default to current month if available, otherwise most recent
                    current_month = datetime.now().month
                    if current_month in available_months_for_selection:
                        prev_months_labels = [calendar.month_name[current_month]]
                    else:
                        # Default to most recent available month
                        latest_month = max(available_months_for_selection)
                        prev_months_labels = [calendar.month_name[latest_month]]
                
                selected_month_labels = st.multiselect(
                    "📆 Months",
                    options=month_options,
                    default=prev_months_labels,
                    key="month_filter",
                    help="Select months to view. Options marked with ⊘ have no data for selected members and years."
                )
                
                # Parse selected months
                selected_months = [month_mapping[label] for label in selected_month_labels]
                st.session_state.filter_selected_months = selected_months
            
            st.divider()
            
            # Display data based on selections
            if not selected_member_ids or not selected_years or not selected_months:
                st.warning("⚠️ Please select at least one member, year, and month to view data.")
            else:
                # Use spinner for data loading
                with st.spinner('🔄 Loading filtered data...'):
                    # Collect data for all selected combinations
                    all_income_data = []
                    all_allocation_data = []
                    
                    for member_id in selected_member_ids:
                        for year in selected_years:
                            for month in selected_months:
                                # Get income data
                                try:
                                    income_df = db.get_income_with_ids(member_id)
                                    if not income_df.empty:
                                        income_df['date_parsed'] = pd.to_datetime(income_df['date'])
                                        period_income = income_df[
                                            (income_df['date_parsed'].dt.year == year) &
                                            (income_df['date_parsed'].dt.month == month)
                                        ].copy()
                                        if not period_income.empty:
                                            period_income['member_id'] = member_id
                                            period_income['member_name'] = [name for name, mid in member_options.items() if mid == member_id][0]
                                            period_income['year'] = year
                                            period_income['month'] = month
                                            all_income_data.append(period_income)
                                except:
                                    pass
                                
                                # Get allocation data
                                try:
                                    alloc_df = db.get_all_allocations(member_id, year, month)
                                    if not alloc_df.empty:
                                        alloc_df['member_id'] = member_id
                                        alloc_df['member_name'] = [name for name, mid in member_options.items() if mid == member_id][0]
                                        alloc_df['year'] = year
                                        alloc_df['month'] = month
                                        all_allocation_data.append(alloc_df)
                                except:
                                    pass
                
                # Combine data
                combined_income_df = pd.concat(all_income_data) if all_income_data else pd.DataFrame()
                combined_alloc_df = pd.concat(all_allocation_data) if all_allocation_data else pd.DataFrame()
                
                # Calculate total metrics
                total_income = float(combined_income_df['amount'].apply(lambda x: float(x)).sum()) if not combined_income_df.empty else 0.0
                total_allocated = float(combined_alloc_df["Allocated Amount"].sum()) if not combined_alloc_df.empty else 0.0
                total_spent = float(combined_alloc_df["Spent Amount"].sum()) if not combined_alloc_df.empty else 0.0
                total_balance = float(combined_alloc_df["Balance"].sum()) if not combined_alloc_df.empty else 0.0
                remaining_liquidity = total_income - total_allocated
                
                # Show selection summary
                member_str = ", ".join(selected_member_names) if len(selected_member_names) <= 3 else f"{len(selected_member_names)} members"
                year_str = ", ".join(map(str, sorted(selected_years))) if len(selected_years) <= 3 else f"{len(selected_years)} years"
                month_str = ", ".join([calendar.month_name[m] for m in sorted(selected_months)]) if len(selected_months) <= 3 else f"{len(selected_months)} months"
                st.caption(f"📊 Showing: **{member_str}** | **{year_str}** | **{month_str}**")
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("💰 Total Income", f"{config.CURRENCY_SYMBOL}{total_income:,.2f}")
                with col2:
                    st.metric("🎯 Total Allocated", f"{config.CURRENCY_SYMBOL}{total_allocated:,.2f}")
                with col3:
                    st.metric("💸 Total Spent", f"{config.CURRENCY_SYMBOL}{total_spent:,.2f}")
                with col4:
                    st.metric("💵 Liquidity", f"{config.CURRENCY_SYMBOL}{remaining_liquidity:,.2f}")
                
                st.divider()
                
                # Visualizations
                if not combined_alloc_df.empty:
                    # Check if multi-member comparison
                    if len(selected_member_ids) > 1:
                        st.subheader("📊 Member Comparison")
                        
                        # Aggregate by member
                        member_summary = combined_alloc_df.groupby('member_name').agg({
                            'Allocated Amount': 'sum',
                            'Spent Amount': 'sum',
                            'Balance': 'sum'
                        }).reset_index()
                        
                        # Comparative bar chart
                        fig = go.Figure(data=[
                            go.Bar(name='Allocated', x=member_summary['member_name'], y=member_summary['Allocated Amount']),
                            go.Bar(name='Spent', x=member_summary['member_name'], y=member_summary['Spent Amount']),
                            go.Bar(name='Balance', x=member_summary['member_name'], y=member_summary['Balance'])
                        ])
                        fig.update_layout(
                            barmode='group',
                            title='Financial Comparison by Member',
                            xaxis_title='Member',
                            yaxis_title=f'Amount ({config.CURRENCY_SYMBOL})',
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        # Single member view - show category breakdown
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Allocation Breakdown")
                            fig_pie = px.pie(
                                combined_alloc_df,
                                values="Allocated Amount",
                                names="Category",
                                title="By Category",
                                hole=0.4
                            )
                            fig_pie.update_layout(height=350)
                            st.plotly_chart(fig_pie, use_container_width=True)
                        
                        with col2:
                            st.subheader("Spent vs Allocated")
                            fig_bar = go.Figure()
                            fig_bar.add_trace(go.Bar(
                                name="Allocated",
                                x=combined_alloc_df["Category"],
                                y=combined_alloc_df["Allocated Amount"],
                                marker_color='lightblue'
                            ))
                            fig_bar.add_trace(go.Bar(
                                name="Spent",
                                x=combined_alloc_df["Category"],
                                y=combined_alloc_df["Spent Amount"],
                                marker_color='coral'
                            ))
                            fig_bar.update_layout(barmode='group', height=350, title="By Category")
                            st.plotly_chart(fig_bar, use_container_width=True)
                    
                    # Detailed table
                    st.subheader("📋 Detailed Breakdown")
                    display_df = combined_alloc_df.copy()
                    display_df["Allocated Amount"] = display_df["Allocated Amount"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
                    display_df["Spent Amount"] = display_df["Spent Amount"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
                    display_df["Balance"] = display_df["Balance"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
                    
                    # Show relevant columns
                    if len(selected_member_ids) > 1:
                        display_cols = ['member_name', 'Category', 'year', 'month', 'Allocated Amount', 'Spent Amount', 'Balance']
                    else:
                        display_cols = ['Category', 'year', 'month', 'Allocated Amount', 'Spent Amount', 'Balance']
                    
                    display_df_filtered = display_df[[col for col in display_cols if col in display_df.columns]]
                    st.dataframe(display_df_filtered, use_container_width=True, hide_index=True)
                else:
                    st.info("No allocation data found for the selected filters.")


    
    # TAB 3: Manage Members
    with tab3:
        st.header("👥 Family Member Management")
       
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("➕ Add New Member")
            
            with st.form("add_member_form"):
                member_name = st.text_input("Full Name")
                member_email = st.text_input("Email Address")
                relationship = st.selectbox(
                    "Relationship",
                    ["Spouse", "Child", "Parent", "Sibling", "Other"]
                )
                
                add_member_btn = st.form_submit_button("Add Member", use_container_width=True)
                
                if add_member_btn:
                    if member_name and member_email:
                        success, member_id, invite_token = db.create_member(
                            household_id, member_email, member_name, relationship, user['id']
                        )
                        if success:
                            st.success(f"✅ Member {member_name} added successfully!")
                            st.markdown("---")
                            st.subheader("🔑 Invite Token")
                            st.info(f"**Share this token with {member_name}:**")
                            st.code(invite_token, language=None)
                            st.caption("💡 Member needs this token to set up their password in the 'Setup Password' tab")
                            st.markdown("**Instructions to share:**")
                            st.markdown(f"""
                            1. Send them the app URL: `{st.session_state.get('app_url', 'your-app-url')}`
                            2. Send them the token: `{invite_token}`
                            3. Tell them to go to '🔑 Setup Password' tab
                            4. Paste token and create password
                            """)
                            # Don't auto-rerun so user can copy token
                        else:
                            st.error("❌ Failed to add member. Email may already exist.")
                    else:
                        st.error("Please fill all fields")
        
        with col2:
            st.subheader("👨‍👩‍👧 Current Family Members")
            
            members_df = db.get_household_members(household_id)
            
            if not members_df.empty:
                # Display each member with action buttons
                for idx, member in members_df.iterrows():
                    with st.container():
                        col_info, col_actions = st.columns([3, 1])
                        
                        with col_info:
                            status_icon = "✅" if member['is_active'] else "❌"
                            invite_icon = "⏳" if member['pending_invite'] else "✓"
                            
                            st.markdown(f"""
                            **{member['full_name']}** {status_icon}  
                            📧 {member['email']} | 👔 {member['role'].title()} | 🤝 {member['relationship']}  
                            Status: {invite_icon} {('Pending Invite' if member['pending_invite'] else 'Active')}
                            """)
                            
                            # Show token if invite is pending
                            if member['pending_invite'] and member['invite_token']:
                                with st.expander("📋 View Invite Token"):
                                    st.code(member['invite_token'], language=None)
                                    st.caption("Share this with the member to let them set up their account")
                        
                        with col_actions:
                            # Only show delete for non-admin members
                            if member['role'] != 'admin':
                                if st.button("🗑️ Delete", key=f"delete_{member['id']}", use_container_width=True):
                                    st.session_state[f'confirm_delete_{member["id"]}'] = True
                                
                                # Confirm deletion
                                if st.session_state.get(f'confirm_delete_{member["id"]}', False):
                                    st.warning(f"Delete {member['full_name']}?")
                                    col_yes, col_no = st.columns(2)
                                    with col_yes:
                                        if st.button("✓", key=f"yes_{member['id']}"):
                                            if db.delete_member(member['id']):
                                                st.success(f"Deleted {member['full_name']}")
                                                st.session_state.pop(f'confirm_delete_{member["id"]}')
                                                st.cache_resource.clear()
                                                st.rerun()
                                            else:
                                                st.error("Failed to delete")
                                    with col_no:
                                        if st.button("✗", key=f"no_{member['id']}"):
                                            st.session_state.pop(f'confirm_delete_{member["id"]}')
                                            st.rerun()
                            else:
                                # Admin user - show message
                                st.caption("Admins cannot be deleted")
                            
                            # Reset Password Button (for all members including admins)
                            if st.button("🔄 Reset Password", key=f"reset_pwd_fam_{member['id']}", use_container_width=True):
                                success, new_token, message = db.reset_user_password(member['id'])
                                if success:
                                    st.success("✅ Password reset successfully!")
                                    with st.expander("🔑 New Invite Token - Click to view", expanded=True):
                                        st.info(f"**Share this token with {member['full_name']}:**")
                                        st.code(new_token, language=None)
                                        st.caption("💡 User must use Password Setup → New Password to set their password")
                                        st.markdown("""
                                        **Instructions:**
                                        1. Share token with user
                                        2. User clicks Password Setup → New Password
                                        3. User pastes token and creates new password
                                        """)
                                    st.cache_data.clear()
                                else:
                                    st.error(f"❌ {message}")
                        
                        st.divider()
            else:
                st.info("No additional members yet")

# ==================== MEMBER DASHBOARD ====================

def show_member_dashboard():
    """Display member dashboard with personal expense tracking"""
    user = st.session_state.user
    
    st.title(f"💰 Personal Budget Tracker")
    st.caption(f"Welcome, {user['full_name']} ({user['relationship']})")
    
    # Logout button
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()
    
    st.divider()
    
    # Show personal expense tracking
    show_member_expense_tracking(user['id'])

# ==================== SHARED EXPENSE TRACKING ====================

def show_member_expense_tracking(user_id):
    """Shared expense tracking UI for both admin and members"""
    
    # Initialize tab state in session_state
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0  # Default to Income tab
    
    # Create tab navigation using radio buttons (preserves state across reruns)
    tab_options = ["💵 Income", "🎯 Allocations", "💸 Expenses", "📊 Review", "💰 Savings"]
    selected_tab = st.radio(
        "Navigation", 
        tab_options, 
        index=st.session_state.active_tab,
        horizontal=True, 
        label_visibility="collapsed",
        key="member_tab_selector"
    )
    
    # Update active tab index
    st.session_state.active_tab = tab_options.index(selected_tab)
    
    st.markdown("---")  # Visual separator
    
    # TAB 1: Income
    if selected_tab == "💵 Income":
        st.header("💵 Income Management")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Add New Income")
            
            # Budget Period Selection (Year -> Month -> Date)
            st.markdown("**📅 Select Budget Period**")
            
            # Callback functions for immediate state update
            def update_budget_year():
                st.session_state.budget_year = st.session_state.income_year_select
                st.cache_data.clear()
                st.cache_resource.clear()
            
            def update_budget_month():
                st.session_state.budget_month = st.session_state.income_month_select
                st.cache_data.clear()
                st.cache_resource.clear()
            
            # Year selection
            current_year = datetime.now().year
            year_options = list(range(current_year - 4, current_year + 2))  # Last 5 years + next year
            st.selectbox(
                "Year",
                options=year_options,
                index=year_options.index(st.session_state.budget_year) if st.session_state.budget_year in year_options else len(year_options) - 2,
                key="income_year_select",
                on_change=update_budget_year
            )
            
            # Month selection
            import calendar
            month_names = [calendar.month_name[i] for i in range(1, 13)]
            month_options = list(range(1, 13))
            st.selectbox(
                "Month",
                options=month_options,
                format_func=lambda x: month_names[x-1],
                index=st.session_state.budget_month - 1,
                key="income_month_select",
                on_change=update_budget_month
            )
            
            # Get final values from session state (already updated by callbacks)
            selected_year = st.session_state.budget_year
            selected_month = st.session_state.budget_month
            
            st.divider()
            
            # Add Income Form
            with st.form("income_form", clear_on_submit=True):
                # Calculate min/max dates for the selected month
                import calendar
                _, last_day = calendar.monthrange(selected_year, selected_month)
                min_date = date(selected_year, selected_month, 1)
                max_date = date(selected_year, selected_month, last_day)
                
                # Default to today if within range, otherwise first day of month
                default_date = date.today() if min_date <= date.today() <= max_date else min_date
                
                income_date = st.date_input(
                    "Date",
                    value=default_date,
                    min_value=min_date,
                    max_value=max_date,
                    help=f"Select a date within {month_names[selected_month-1]} {selected_year}"
                )
                income_source = st.text_input("Source", placeholder="e.g., Salary, Bonus")
                income_amount = st.number_input(f"Amount ({config.CURRENCY_SYMBOL})", min_value=0.0, step=100.0)
                
                submit_income = st.form_submit_button("➕ Add Income", use_container_width=True)
                
                if submit_income and income_source and income_amount > 0:
                    if db.add_income(user_id, income_date.strftime(config.DATE_FORMAT), income_source, income_amount):
                        st.success(f"✅ Added {config.CURRENCY_SYMBOL}{income_amount:,.2f}")
                        st.cache_resource.clear()
                        st.rerun()
        
        with col2:
            st.subheader("Income History")
            
            # Display selected period prominently
            period_display = f"{month_names[st.session_state.budget_month-1]} {st.session_state.budget_year}"
            st.info(f"📅 **Showing:** {period_display}")
            
            # Get all income and filter by selected period
            income_df = db.get_income_with_ids(user_id)
            
            if not income_df.empty:
                # Filter by year and month
                income_df['date_parsed'] = pd.to_datetime(income_df['date'])
                filtered_df = income_df[
                    (income_df['date_parsed'].dt.year == st.session_state.budget_year) &
                    (income_df['date_parsed'].dt.month == st.session_state.budget_month)
                ].copy()
                
                # Calculate period-specific total
                period_total = filtered_df['amount'].apply(lambda x: float(x)).sum() if not filtered_df.empty else 0.0
                st.metric(f"💰 Total for {period_display}", f"{config.CURRENCY_SYMBOL}{period_total:,.2f}")
                
                if not filtered_df.empty:
                    # Prepare display dataframe
                    display_df = filtered_df.copy()
                    display_df['Amount'] = display_df['amount'].apply(lambda x: f"{config.CURRENCY_SYMBOL}{float(x):,.2f}")
                    display_df = display_df.rename(columns={
                        'date': 'Date',
                        'source': 'Source'
                    })
                    
                    # Show as dataframe (Excel-like)
                    st.dataframe(
                        display_df[['Date', 'Source', 'Amount']],
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Edit/Delete controls below table
                    st.caption("Select an entry to edit or delete:")
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if len(filtered_df) > 0:
                            options = [f"{row['date']} - {row['source']} - {config.CURRENCY_SYMBOL}{float(row['amount']):,.2f}" 
                                     for _, row in filtered_df.iterrows()]
                            selected_idx = st.selectbox("", options, label_visibility="collapsed", key="income_select")
                            
                            if selected_idx:
                                idx = options.index(selected_idx)
                                selected_row = filtered_df.iloc[idx]
                                income_id = int(selected_row['id'])
                                
                                # Show edit form in expander
                                with st.expander("✏️ Edit Selected Entry", expanded=False):
                                    # Parse the date from the selected row
                                    edit_date_parsed = pd.to_datetime(selected_row['date']).date()
                                    edit_year = edit_date_parsed.year
                                    edit_month = edit_date_parsed.month
                                    
                                    # Calculate min/max for edit month
                                    _, edit_last_day = calendar.monthrange(edit_year, edit_month)
                                    edit_min_date = date(edit_year, edit_month, 1)
                                    edit_max_date = date(edit_year, edit_month, edit_last_day)
                                    
                                    new_date = st.date_input(
                                        "Date",
                                        value=edit_date_parsed,
                                        min_value=edit_min_date,
                                        max_value=edit_max_date,
                                        key=f"edit_date_{income_id}"
                                    )
                                    new_source = st.text_input("Source", value=selected_row['source'], key=f"edit_source_{income_id}")
                                    new_amount = st.number_input("Amount", value=float(selected_row['amount']), min_value=0.0, step=100.0, key=f"edit_amount_{income_id}")
                                    
                                    col_a, col_b = st.columns(2)
                                    if col_a.button("💾 Save Changes", key=f"save_{income_id}"):
                                        if not new_source or new_source.strip() == "":
                                            st.error("Source cannot be empty")
                                        elif new_amount <= 0:
                                            st.error("Amount must be greater than 0")
                                        else:
                                            if db.update_income(income_id, user_id, new_date.strftime(config.DATE_FORMAT), new_source, new_amount):
                                                st.success("✅ Updated successfully!")
                                                st.cache_resource.clear()
                                                st.rerun()
                                            else:
                                                st.error("Failed to update")
                                    
                                    if col_b.button("🗑️ Delete Entry", key=f"del_{income_id}"):
                                        if db.delete_income(income_id, user_id):
                                            st.success("✅ Deleted successfully!")
                                            st.cache_resource.clear()
                                            st.rerun()
                                        else:
                                            st.error("Failed to delete")
                else:
                    st.warning(f"No income entries found for {period_display}")
                    st.caption("💡 Use the form on the left to add income for this period")

            else:
                st.info("No income entries yet")
                st.caption("💡 Use the form on the left to add your first income entry")

    
    # TAB 2: Allocations
    elif selected_tab == "🎯 Allocations":
        st.header("🎯 Budget Allocations")
        
        # Show current budget period (read-only indicator)
        import calendar
        period_display = f"{calendar.month_name[st.session_state.budget_month]} {st.session_state.budget_year}"
        
        # Calculate budget metrics
        total_income = db.get_total_income(user_id, st.session_state.budget_year, st.session_state.budget_month)
        allocations_df_temp = db.get_allocations_with_ids(user_id, st.session_state.budget_year, st.session_state.budget_month)
        total_allocated = allocations_df_temp['allocated_amount'].sum() if not allocations_df_temp.empty else 0.0
        allocation_left = total_income - total_allocated
        
        # Display budget metrics in a compact container
        with st.container():
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            with metric_col1:
                st.metric("💵 Total Income", f"{config.CURRENCY_SYMBOL}{total_income:,.2f}")
            with metric_col2:
                st.metric("📈 Total Allocated", f"{config.CURRENCY_SYMBOL}{total_allocated:,.2f}")
            with metric_col3:
                # Color indicator based on remaining budget
                if allocation_left > 0:
                    st.metric("💰 Allocation Amount Left", f"{config.CURRENCY_SYMBOL}{allocation_left:,.2f}", delta="Available", delta_color="normal")
                elif allocation_left == 0:
                    st.metric("💰 Allocation Amount Left", f"{config.CURRENCY_SYMBOL}0.00", delta="Fully Allocated", delta_color="off")
                else:
                    st.metric("💰 Allocation Amount Left", f"{config.CURRENCY_SYMBOL}{allocation_left:,.2f}", delta="Over-allocated!", delta_color="inverse")
        
        st.divider()
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Add Allocation")
            
            # Display read-only Year and Month
            st.markdown("**📅 Budget Period** *(readonly)*")
            col_y, col_m = st.columns(2)
            with col_y:
                st.text_input("Year",value=str(st.session_state.budget_year), disabled=True, key="alloc_year_display")
            with col_m:
                st.text_input("Month", value=calendar.month_name[st.session_state.budget_month], disabled=True, key="alloc_month_display")
            
            st.caption("💡 Change period in Income tab to budget for different months")
            st.divider()
            
            with st.form("allocation_form", clear_on_submit=True):
                alloc_category = st.text_input("Category", placeholder="e.g., Groceries, Rent")
                alloc_amount = st.number_input(f"Amount ({config.CURRENCY_SYMBOL})", min_value=0.0, step=100.0)
                
                submit_alloc = st.form_submit_button("➕ Add Allocation", use_container_width=True)
                
                if submit_alloc and alloc_category and alloc_amount > 0:
                    # Check if allocation exceeds available budget
                    if alloc_amount > allocation_left:
                        # Show warning and ask for confirmation
                        st.session_state.pending_allocation = {
                            'category': alloc_category,
                            'amount': alloc_amount,
                            'year': st.session_state.budget_year,
                            'month': st.session_state.budget_month
                        }
                        st.session_state.show_allocation_warning = True
                        st.rerun()
                    else:
                        # Proceed directly if within budget
                        year = st.session_state.budget_year
                        month = st.session_state.budget_month
                        
                        if db.add_allocation(user_id, alloc_category, alloc_amount, year, month):
                            st.success(f"✅ Created allocation: {alloc_category} for {period_display}")
                            st.cache_resource.clear()
                            st.rerun()
                        else:
                            st.error(f"Category '{alloc_category}' already exists for {period_display}!")
            
            # Show confirmation dialog for over-allocation
            if st.session_state.get('show_allocation_warning', False):
                pending = st.session_state.pending_allocation
                over_amount = pending['amount'] - allocation_left
                
                st.warning(f"⚠️ **Budget Exceeded Warning**")
                st.markdown(f"""
                You are trying to allocate **{config.CURRENCY_SYMBOL}{pending['amount']:,.2f}** for **{pending['category']}**.
                
                - Available budget: **{config.CURRENCY_SYMBOL}{allocation_left:,.2f}**
                - Over-allocation: **{config.CURRENCY_SYMBOL}{over_amount:,.2f}**
                
                **You may go into debt for this month. Do you want to proceed?**
                """)
                
                col_ok, col_cancel = st.columns(2)
                with col_ok:
                    if st.button("✅ OK, Proceed", use_container_width=True, type="primary"):
                        # Add the allocation
                        if db.add_allocation(user_id, pending['category'], pending['amount'], pending['year'], pending['month']):
                            st.success(f"✅ Created allocation: {pending['category']} (over-allocated)")
                            st.session_state.show_allocation_warning = False
                            st.session_state.pending_allocation = None
                            st.cache_resource.clear()
                            st.rerun()
                        else:
                            st.error(f"Category '{pending['category']}' already exists!")
                            st.session_state.show_allocation_warning = False
                            st.session_state.pending_allocation = None
                
                with col_cancel:
                    if st.button("❌ Cancel", use_container_width=True):
                        st.session_state.show_allocation_warning = False
                        st.session_state.pending_allocation = None
                        st.rerun()
            
            st.divider()
            
            # Export Previous Month Allocations - Enhanced Version  
            st.markdown("---")
            if st.button("📥 Export Previous Month Allocations", use_container_width=True, key="btn_export_prev_alloc_new"):
                st.session_state.show_export_allocations = True
            
            if st.session_state.get('show_export_allocations', False):
                with st.expander("📥 Export Allocations from Previous Period", expanded=True):
                    available_periods = db.get_available_allocation_periods(user_id)
                    
                    if not available_periods:
                        st.info("No previous allocations found to export")
                        if st.button("Close", key="close_no_export"):
                            st.session_state.show_export_allocations = False
                            st.rerun()
                    else:
                        years = sorted(set(p['year'] for p in available_periods), reverse=True)
                        selected_year = st.selectbox("Select Year", options=years, key="export_year_select")
                        
                        months_for_year = sorted([p['month'] for p in available_periods if p['year'] == selected_year], reverse=True)
                        selected_month = st.selectbox("Select Month", options=months_for_year, format_func=lambda x: calendar.month_name[x], key="export_month_select")
                        
                        st.info(f"📅 **From:** {calendar.month_name[selected_month]} {selected_year} → **To:** {calendar.month_name[st.session_state.budget_month]} {st.session_state.budget_year}")
                        
                        col_export, col_cancel = st.columns(2)
                        with col_export:
                            if st.button("✅ Copy All", key="confirm_export", use_container_width=True):
                                success, message = db.copy_allocations_from_period(user_id, selected_year, selected_month, st.session_state.budget_year, st.session_state.budget_month)
                                if success:
                                    st.success(f"✅ {message}")
                                    st.session_state.show_export_allocations = False
                                    st.cache_resource.clear()
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
                        with col_cancel:
                            if st.button("Cancel", key="cancel_export", use_container_width=True):
                                st.session_state.show_export_allocations = False
                                st.rerun()
        
        
        with col2:
            st.subheader(f"Allocations for {period_display}")
            
            # Get allocations filtered by period
            allocations_df = db.get_allocations_with_ids(user_id, st.session_state.budget_year, st.session_state.budget_month)
            
            if not allocations_df.empty:
                # Prepare display dataframe
                display_df = allocations_df.copy()
                display_df['Allocated'] = display_df['allocated_amount'].apply(lambda x: f"{config.CURRENCY_SYMBOL}{float(x):,.2f}")
                display_df['Spent'] = display_df['spent_amount'].apply(lambda x: f"{config.CURRENCY_SYMBOL}{float(x):,.2f}")
                display_df['Balance'] = display_df['balance'].apply(lambda x: f"{config.CURRENCY_SYMBOL}{float(x):,.2f}")
                display_df = display_df.rename(columns={'category': 'Category'})
                
                # Show as dataframe (Excel-like)
                st.dataframe(
                    display_df[['Category', 'Allocated', 'Spent', 'Balance']],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Edit/Delete controls below table
                st.caption("Select a category to edit or delete:")
                col1, col2 = st.columns([3, 1])
                with col1:
                    if len(allocations_df) > 0:
                        options = [f"{row['category']} - Allocated: {config.CURRENCY_SYMBOL}{float(row['allocated_amount']):,.2f}" 
                                 for _, row in allocations_df.iterrows()]
                        selected_idx = st.selectbox("", options, label_visibility="collapsed", key="alloc_select")
                        
                        if selected_idx:
                            idx = options.index(selected_idx)
                            selected_row = allocations_df.iloc[idx]
                            alloc_id = int(selected_row['id'])
                            
                            # Show edit form in expander
                            with st.expander("✏️ Edit Selected Allocation", expanded=False):
                                new_category = st.text_input("Category", value=selected_row['category'], key=f"edit_cat_{alloc_id}")
                                new_allocated = st.number_input("Allocated Amount", value=float(selected_row['allocated_amount']), 
                                                               min_value=0.0, step=100.0, key=f"edit_alloc_{alloc_id}")
                                st.caption(f"Spent: {config.CURRENCY_SYMBOL}{float(selected_row['spent_amount']):,.2f} (read-only)")
                                st.caption(f"New Balance: {config.CURRENCY_SYMBOL}{new_allocated - float(selected_row['spent_amount']):,.2f}")
                                
                                col_a, col_b = st.columns(2)
                                if col_a.button("💾 Save Changes", key=f"save_alloc_{alloc_id}"):
                                    if not new_category or new_category.strip() == "":
                                        st.error("Category cannot be empty")
                                    elif new_allocated <= 0:
                                        st.error("Allocated amount must be greater than 0")
                                    else:
                                        # Use year/month from the selected row
                                        year = int(selected_row['year'])
                                        month = int(selected_row['month'])
                                        if db.update_allocation(alloc_id, user_id, new_category, new_allocated, year, month):
                                            st.success("✅ Updated successfully!")
                                            st.cache_resource.clear()
                                            st.rerun()
                                        else:
                                            st.error("Failed to update")
                                
                                if col_b.button("🗑️ Delete Allocation", key=f"del_alloc_{alloc_id}"):
                                    if db.delete_allocation_by_id(alloc_id, user_id):
                                        st.success("✅ Deleted successfully!")
                                        st.cache_resource.clear()
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete")

            else:
                st.warning(f"No allocations found for {period_display}")
                st.caption("💡 Use the form on the left to create allocations for this period")
            
            # Fix Allocations button at bottom
            st.divider()
            if st.button("🔧 Fix Allocation Spent Amounts", help="Recalculate spent values from actual expenses"):
                with st.spinner("Recalculating..."):
                    try:
                        cursor = db.conn.cursor()
                        db._execute(cursor, 'SELECT id, user_id, category, allocated_amount FROM allocations')
                        allocations = cursor.fetchall()
                        
                        fixed_count = 0
                        for alloc in allocations:
                            user_id_alloc = alloc['user_id']
                            category = alloc['category']
                            allocated_amount = float(alloc['allocated_amount'])
                            
                            db._execute(cursor, 
                                'SELECT SUM(amount) as total_spent FROM expenses WHERE user_id = ? AND category = ?',
                                (user_id_alloc, category)
                            )
                            result = cursor.fetchone()
                            total_spent = float(result['total_spent']) if result and result['total_spent'] else 0.0
                            
                            new_balance = allocated_amount - total_spent
                            db._execute(cursor,
                                'UPDATE allocations SET spent_amount = ?, balance = ? WHERE id = ?',
                                (total_spent, new_balance, alloc['id'])
                            )
                            fixed_count += 1
                        
                        db.conn.commit()
                        st.success(f"✅ Fixed {fixed_count} allocations! Refresh the page to see updated values.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        db.conn.rollback()
            st.caption("💡 Use this button if Spent amounts show incorrect or negative values")




    
    # TAB 3: Expenses
    elif selected_tab == "💸 Expenses":
        st.header("💸 Daily Expenses")
        
        # Show current budget period
        import calendar
        period_display = f"{calendar.month_name[st.session_state.budget_month]} {st.session_state.budget_year}"
        
        col1, col2 = st.columns([1, 2])
        
        # Get categories for the current period
        categories = db.get_categories(user_id, st.session_state.budget_year, st.session_state.budget_month)
        
        with col1:
            st.subheader("Add New Expense")
            
            # Display read-only Year and Month
            st.markdown("**📅 Budget Period** *(readonly)*")
            col_y, col_m = st.columns(2)
            with col_y:
                st.text_input("Year", value=str(st.session_state.budget_year), disabled=True, key="expense_year_display")
            with col_m:
                st.text_input("Month", value=calendar.month_name[st.session_state.budget_month], disabled=True, key="expense_month_display")
            
            st.caption("💡 Change period in Income tab to log expenses for different months")
            st.divider()
            if not categories:
                st.warning("⚠️ Create allocation categories first in the Allocations tab!")
            else:
                with st.form("expense_form", clear_on_submit=True):
                    # Calculate min/max dates for the selected month
                    _, last_day = calendar.monthrange(st.session_state.budget_year, st.session_state.budget_month)
                    min_date = date(st.session_state.budget_year, st.session_state.budget_month, 1)
                    max_date = date(st.session_state.budget_year, st.session_state.budget_month, last_day)
                    
                    # Default to today if within range, otherwise first day of month
                    default_date = date.today() if min_date <= date.today() <= max_date else min_date
                    
                    expense_date = st.date_input(
                        "Date",
                        value=default_date,
                        min_value=min_date,
                        max_value=max_date,
                        help=f"Select a date within {calendar.month_name[st.session_state.budget_month]} {st.session_state.budget_year}"
                    )
                    expense_category = st.selectbox("Category", options=categories)
                    expense_amount = st.number_input(f"Amount ({config.CURRENCY_SYMBOL})", min_value=0.0, step=10.0)
                    
                    # Subcategory dropdown
                    subcategory_options = ["Investment", "Food - Online", "Food - Hotel", "Grocery - Online", "Grocery - Offline", "School Fee", "Extra-Curricular", "Co-Curricular", "House Rent", "Maintenance", "Vehicle", "Gadgets", "Others"]
                    expense_subcategory = st.selectbox("Subcategory", options=subcategory_options)
                    
                    # Payment Mode dropdown
                    payment_mode_options = ["UPI", "Credit Card", "Debit Card", "Netbanking", "Cash"]
                    expense_payment_mode = st.selectbox("Payment Mode", options=payment_mode_options)
                    
                    # Payment Details text box
                    expense_payment_details = st.text_input("Payment Details", placeholder="e.g., Card ending in 1234, UPI ID, etc.")
                    
                    expense_comment = st.text_area("Comment", placeholder="Brief description")
                    
                    submit_expense = st.form_submit_button("➕ Add Expense", use_container_width=True)
                    
                    if submit_expense and expense_category and expense_amount > 0:
                        # Conditional validation: Comment required if subcategory is "Others"
                        if expense_subcategory == "Others" and (not expense_comment or expense_comment.strip() == ""):
                            st.error("⚠️ Comment is required when subcategory is 'Others'")
                        else:
                            if db.add_expense(user_id, expense_date.strftime(config.DATE_FORMAT), 
                                            expense_category, expense_amount, expense_comment, expense_subcategory, expense_payment_mode, expense_payment_details):
                                st.success(f"✅ Added expense: {config.CURRENCY_SYMBOL}{expense_amount:,.2f}")
                                st.cache_resource.clear()
                                st.rerun()
        
        with col2:
            st.subheader(f"Expense History for {period_display}")
            
            # Get all expenses and filter by period
            expenses_df = db.get_expenses_with_ids(user_id)
            
            if not expenses_df.empty:
                # Filter by year and month
                expenses_df['date_parsed'] = pd.to_datetime(expenses_df['date'])
                filtered_df = expenses_df[
                    (expenses_df['date_parsed'].dt.year == st.session_state.budget_year) &
                    (expenses_df['date_parsed'].dt.month == st.session_state.budget_month)
                ].copy()
                
                if not filtered_df.empty:
                    # Calculate original total
                    original_total = filtered_df["amount"].apply(lambda x: float(x)).sum()
                    
                    # Excel-like Filters - Multiselect for each column
                    st.markdown("**🔍 Filters** (Select to filter, leave empty to show all)")
                    
                    filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns(5)
                    
                    # Get unique values for each column
                    all_dates = sorted(filtered_df['date'].unique().tolist())
                    all_categories = sorted(filtered_df['category'].unique().tolist())
                    all_subcategories = sorted(filtered_df['subcategory'].dropna().unique().tolist())
                    
                    # Safely get payment modes if column exists
                    if 'payment_mode' in filtered_df.columns:
                        all_payment_modes = sorted(filtered_df['payment_mode'].dropna().unique().tolist())
                    else:
                        all_payment_modes = []
                    
                    all_comments = sorted(filtered_df['comment'].dropna().unique().tolist())
                    
                    with filter_col1:
                        selected_dates = st.multiselect("Date", options=all_dates, default=[], key="filter_date")
                    
                    with filter_col2:
                        selected_categories = st.multiselect("Category", options=all_categories, default=[], key="filter_category")
                    
                    with filter_col3:
                        selected_subcategories = st.multiselect("Subcategory", options=all_subcategories, default=[], key="filter_subcategory")
                    
                    with filter_col4:
                        # Only show payment mode filter if column exists
                        if all_payment_modes:
                            selected_payment_modes = st.multiselect("Payment Mode", options=all_payment_modes, default=[], key="filter_payment_mode")
                        else:
                            selected_payment_modes = []
                            st.info("No payment data yet")
                    
                    with filter_col5:
                        selected_comments = st.multiselect("Comment", options=all_comments, default=[], key="filter_comment")
                    
                    # Apply filters
                    display_df = filtered_df.copy()
                    
                    if selected_dates:
                        display_df = display_df[display_df['date'].isin(selected_dates)]
                    
                    if selected_categories:
                        display_df = display_df[display_df['category'].isin(selected_categories)]
                    
                    if selected_subcategories:
                        display_df = display_df[display_df['subcategory'].isin(selected_subcategories)]
                    
                    if selected_payment_modes and 'payment_mode' in display_df.columns:
                        display_df = display_df[display_df['payment_mode'].isin(selected_payment_modes)]
                    
                    if selected_comments:
                        display_df = display_df[display_df['comment'].isin(selected_comments)]
                    
                    # Calculate filtered total
                    if not display_df.empty:
                        filtered_total = display_df["amount"].apply(lambda x: float(x)).sum()
                    else:
                        filtered_total = 0
                    
                    # Show totals side by side
                    metric_col1, metric_col2 = st.columns(2)
                    with metric_col1:
                        st.metric(f"💸 Total for {period_display}", f"{config.CURRENCY_SYMBOL}{original_total:,.2f}")
                    with metric_col2:
                        st.metric(f"📊 Filtered Total", f"{config.CURRENCY_SYMBOL}{filtered_total:,.2f}")
                    
                    # Prepare display
                    if not display_df.empty:
                        display_df_formatted = display_df.copy()
                        display_df_formatted['Amount'] = display_df_formatted['amount'].apply(lambda x: f"{config.CURRENCY_SYMBOL}{float(x):,.2f}")
                        
                        # Build column rename dict based on what exists
                        rename_dict = {
                            'date': 'Date',
                            'category': 'Category',
                            'subcategory': 'Subcategory',
                            'comment': 'Comment'
                        }
                        
                        # Add payment columns if they exist
                        if 'payment_mode' in display_df_formatted.columns:
                            rename_dict['payment_mode'] = 'Payment Mode'
                        if 'payment_details' in display_df_formatted.columns:
                            rename_dict['payment_details'] = 'Payment Details'
                        
                        display_df_formatted = display_df_formatted.rename(columns=rename_dict)
                        
                        # Build column list based on what exists
                        display_columns = ['Date', 'Category', 'Amount', 'Subcategory']
                        if 'Payment Mode' in display_df_formatted.columns:
                            display_columns.append('Payment Mode')
                        if 'Payment Details' in display_df_formatted.columns:
                            display_columns.append('Payment Details')
                        display_columns.append('Comment')
                        
                        # Show as dataframe with horizontal scroll enabled
                        st.dataframe(
                            display_df_formatted[display_columns],
                            hide_index=True,
                            height=400  # Fixed height enables scrollbars
                        )
                    else:
                        st.info("No expenses match the selected filters")
                    
                    # Edit/Delete controls below table
                    st.caption("Select an expense to edit or delete:")
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if len(filtered_df) > 0:
                            options = [f"{row['date']} - {row['category']} - {config.CURRENCY_SYMBOL}{float(row['amount']):,.2f}" 
                                     for _, row in filtered_df.iterrows()]
                            selected_idx = st.selectbox("", options, label_visibility="collapsed", key="expense_select")
                            
                            if selected_idx:
                                idx = options.index(selected_idx)
                                selected_row = filtered_df.iloc[idx]
                                expense_id = int(selected_row['id'])
                                
                                # Show edit form in expander
                                with st.expander("✏️ Edit Selected Expense", expanded=False):
                                    # Parse the date from the selected row
                                    edit_date_parsed = pd.to_datetime(selected_row['date']).date()
                                    edit_year = edit_date_parsed.year
                                    edit_month = edit_date_parsed.month
                                    
                                    # Calculate min/max for edit month
                                    _, edit_last_day = calendar.monthrange(edit_year, edit_month)
                                    edit_min_date = date(edit_year, edit_month, 1)
                                    edit_max_date = date(edit_year, edit_month, edit_last_day)
                                    
                                    new_date = st.date_input(
                                        "Date",
                                        value=edit_date_parsed,
                                        min_value=edit_min_date,
                                        max_value=edit_max_date,
                                        key=f"edit_exp_date_{expense_id}"
                                    )
                                    cat_options = categories if categories else [selected_row['category']]
                                    cat_index = cat_options.index(selected_row['category']) if selected_row['category'] in cat_options else 0
                                    new_category = st.selectbox("Category", options=cat_options, index=cat_index, key=f"edit_exp_cat_{expense_id}")
                                    new_amount = st.number_input("Amount", value=float(selected_row['amount']), min_value=0.0, step=10.0, key=f"edit_exp_amt_{expense_id}")
                                    
                                    # Subcategory dropdown
                                    subcategory_options = ["Investment", "Food - Online", "Food - Hotel", "Grocery - Online", "Grocery - Offline", "School Fee", "Extra-Curricular", "Co-Curricular", "House Rent", "Maintenance", "Vehicle", "Gadgets", "Others"]
                                    current_subcategory = selected_row.get('subcategory', None) or "Investment"
                                    subcat_index = subcategory_options.index(current_subcategory) if current_subcategory in subcategory_options else 0
                                    new_subcategory = st.selectbox("Subcategory", options=subcategory_options, index=subcat_index, key=f"edit_exp_subcat_{expense_id}")
                                    
                                    # Payment Mode dropdown
                                    payment_mode_options = ["UPI", "Credit Card", "Debit Card", "Netbanking", "Cash"]
                                    current_payment_mode = selected_row.get('payment_mode', None) or "UPI"
                                    payment_mode_index = payment_mode_options.index(current_payment_mode) if current_payment_mode in payment_mode_options else 0
                                    new_payment_mode = st.selectbox("Payment Mode", options=payment_mode_options, index=payment_mode_index, key=f"edit_exp_payment_mode_{expense_id}")
                                    
                                    # Payment Details text box
                                    current_payment_details = selected_row.get('payment_details', None) or ""
                                    new_payment_details = st.text_input("Payment Details", value=current_payment_details, placeholder="e.g., Card ending in 1234, UPI ID, etc.", key=f"edit_exp_payment_details_{expense_id}")
                                    
                                    new_comment = st.text_input("Comment", value=selected_row['comment'] if selected_row['comment'] else "", key=f"edit_exp_cmt_{expense_id}")
                                    
                                    col_a, col_b = st.columns(2)
                                    if col_a.button("💾 Save Changes", key=f"save_exp_{expense_id}"):
                                        # Conditional validation: Comment required if subcategory is "Others"
                                        if new_subcategory == "Others" and (not new_comment or new_comment.strip() == ""):
                                            st.error("⚠️ Comment is required when subcategory is 'Others'")
                                        elif new_amount <= 0:
                                            st.error("Amount must be greater than 0")
                                        elif new_category not in categories:
                                            st.error("Invalid category")
                                        else:
                                            old_category = selected_row['category']
                                            old_amount = float(selected_row['amount'])
                                            if db.update_expense(expense_id, user_id, new_date.strftime(config.DATE_FORMAT), 
                                                               new_category, new_amount, old_category, old_amount, new_comment, new_subcategory, None, new_payment_mode, new_payment_details):
                                                st.success("✅ Updated successfully!")
                                                st.cache_resource.clear()
                                                st.rerun()
                                            else:
                                                st.error("Failed to update")
                                    
                                    if col_b.button("🗑️ Delete Expense", key=f"del_exp_{expense_id}"):
                                        if db.delete_expense(expense_id, user_id, selected_row['category'], float(selected_row['amount'])):
                                            st.success("✅ Deleted successfully!")
                                            st.cache_resource.clear()
                                            st.rerun()
                                        else:
                                            st.error("Failed to delete")
                else:
                    st.warning(f"No expenses found for {period_display}")
                    st.caption("💡 Use the form on the left to add expenses for this period")

            else:
                st.info("No expenses recorded yet")
                st.caption("💡 Create allocations first, then add expenses")




    
    # TAB 4: Review (Dashboard)
    elif selected_tab == "📊 Review":
        st.header("📊 Financial Review")
        
        # Initialize review filter session state
        if 'review_selected_years' not in st.session_state:
            st.session_state.review_selected_years = []
        if 'review_selected_months' not in st.session_state:
            st.session_state.review_selected_months = []
        
        # Get available periods for this user only
        available_data = get_user_available_periods(db, [user_id])
        available_years = available_data['years']
        available_months_by_year = available_data['months_by_year']
        
        # Check if user has any data
        if not available_years:
            st.info("ℹ️ No financial data found. Start by adding income and allocations in the respective tabs!")
        else:
            # Create filter UI
            st.subheader("🔍 Select Period(s)")
            col1, col2 = st.columns(2)
            
            # Define year range (dynamically extend if past July)
            current_year = datetime.now().year
            current_month = datetime.now().month
            # If past July, add one more future year for planning next year's budget
            if current_month >= 7:
                all_years = list(range(current_year - 5, current_year + 3))  # Last 5 years + next 2 years
            else:
                all_years = list(range(current_year - 5, current_year + 2))  # Last 5 years + next year
            
            with col1:
                # Format year options with visual prefix for unavailable years
                year_options = []
                year_mapping = {}
                for year in all_years:
                    if year in available_years:
                        label = str(year)
                    else:
                        label = f"⊘ {year} (No Data)"
                    year_options.append(label)
                    year_mapping[label] = year
                
                # Smart defaults for years
                if not st.session_state.review_selected_years:
                    # Default to most recent year with data
                    if available_years:
                        st.session_state.review_selected_years = [max(available_years)]
                
                # Get previously selected years that are still valid
                prev_years_labels = [
                    str(y) if y in available_years else f"⊘ {y} (No Data)" 
                    for y in st.session_state.review_selected_years if y in all_years
                ]
                if not prev_years_labels and available_years:
                    # Fallback to most recent year
                    prev_years_labels = [str(max(available_years))]
                
                selected_year_labels = st.multiselect(
                    "📅 Years",
                    options=year_options,
                    default=prev_years_labels,
                    key="review_year_filter",
                    help="Select years to review. Options marked with ⊘ have no data."
                )
                
                # Parse selected years
                selected_years = [year_mapping[label] for label in selected_year_labels]
                st.session_state.review_selected_years = selected_years
            
            with col2:
                # Get available months for selected years (union of all months across selected years)
                available_months_for_selection = set()
                for year in selected_years:
                    if year in available_months_by_year:
                        available_months_for_selection.update(available_months_by_year[year])
                
                # Format month options with visual prefix for unavailable months
                import calendar
                all_months = list(range(1, 13))
                month_options = []
                month_mapping = {}
                for month in all_months:
                    month_name = calendar.month_name[month]
                    if month in available_months_for_selection:
                        label = month_name
                    else:
                        label = f"⊘ {month_name} (No Data)"
                    month_options.append(label)
                    month_mapping[label] = month
                
                # Smart defaults for months
                if not st.session_state.review_selected_months and available_months_for_selection:
                    # Default to current month if available, otherwise most recent
                    current_month = datetime.now().month
                    if current_month in available_months_for_selection:
                        st.session_state.review_selected_months = [current_month]
                    else:
                        st.session_state.review_selected_months = [max(available_months_for_selection)]
                
                # Get previously selected months that are still valid
                prev_months_labels = [
                    calendar.month_name[m] if m in available_months_for_selection else f"⊘ {calendar.month_name[m]} (No Data)"
                    for m in st.session_state.review_selected_months if 1 <= m <= 12
                ]
                if not prev_months_labels and available_months_for_selection:
                    # Fallback to most recent month
                    latest_month = max(available_months_for_selection)
                    prev_months_labels = [calendar.month_name[latest_month]]
                
                selected_month_labels = st.multiselect(
                    "📆 Months",
                    options=month_options,
                    default=prev_months_labels,
                    key="review_month_filter",
                    help="Select months to review. Options marked with ⊘ have no data for selected years."
                )
                
                # Parse selected months
                selected_months = [month_mapping[label] for label in selected_month_labels]
                st.session_state.review_selected_months = selected_months
            
            st.divider()
            
            # Display data based on selections
            if not selected_years or not selected_months:
                st.warning("⚠️ Please select at least one year and month to review.")
            else:
                # Show selection summary
                if len(selected_years) <= 3:
                    year_str = ", ".join(map(str, sorted(selected_years)))
                else:
                    year_str = f"{len(selected_years)} years"
                    
                if len(selected_months) <= 3:
                    month_str = ", ".join([calendar.month_name[m] for m in sorted(selected_months)])
                else:
                    month_str = f"{len(selected_months)} months"
                
                st.caption(f"📊 Showing: **{year_str}** | **{month_str}**")
                
                # Load data with spinner
                with st.spinner('🔄 Loading review data...'):
                    all_income_data = []
                    all_allocation_data = []
                    
                    for year in selected_years:
                        for month in selected_months:
                            # Get income data
                            try:
                                income_df = db.get_income_with_ids(user_id)
                                if not income_df.empty:
                                    income_df['date_parsed'] = pd.to_datetime(income_df['date'])
                                    period_income = income_df[
                                        (income_df['date_parsed'].dt.year == year) &
                                        (income_df['date_parsed'].dt.month == month)
                                    ].copy()
                                    if not period_income.empty:
                                        period_income['year'] = year
                                        period_income['month'] = month
                                        all_income_data.append(period_income)
                            except:
                                pass
                            
                            # Get allocation data
                            try:
                                alloc_df = db.get_all_allocations(user_id, year, month)
                                if not alloc_df.empty:
                                    alloc_df['year'] = year
                                    alloc_df['month'] = month
                                    all_allocation_data.append(alloc_df)
                            except:
                                pass
                    
                    # Combine data
                    combined_income_df = pd.concat(all_income_data) if all_income_data else pd.DataFrame()
                    combined_alloc_df = pd.concat(all_allocation_data) if all_allocation_data else pd.DataFrame()
                
                # Calculate metrics
                total_income = float(combined_income_df['amount'].apply(lambda x: float(x)).sum()) if not combined_income_df.empty else 0.0
                total_allocated = float(combined_alloc_df["Allocated Amount"].sum()) if not combined_alloc_df.empty else 0.0
                total_spent = float(combined_alloc_df["Spent Amount"].sum()) if not combined_alloc_df.empty else 0.0
                total_balance = float(combined_alloc_df["Balance"].sum()) if not combined_alloc_df.empty else 0.0
                remaining_liquidity = total_income - total_allocated
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("💰 Total Income", f"{config.CURRENCY_SYMBOL}{total_income:,.2f}")
                with col2:
                    st.metric("🎯 Total Allocated", f"{config.CURRENCY_SYMBOL}{total_allocated:,.2f}")
                with col3:
                    st.metric("💸 Total Spent", f"{config.CURRENCY_SYMBOL}{total_spent:,.2f}")
                with col4:
                    st.metric("💵 Liquidity", f"{config.CURRENCY_SYMBOL}{remaining_liquidity:,.2f}")
                
                st.divider()
                
                # Charts
                if not combined_alloc_df.empty:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Allocation Breakdown")
                        # Aggregate by category if multi-period
                        if len(selected_years) > 1 or len(selected_months) > 1:
                            agg_alloc = combined_alloc_df.groupby('Category').agg({
                                'Allocated Amount': 'sum'
                            }).reset_index()
                            fig_pie = px.pie(
                                agg_alloc,
                                values="Allocated Amount",
                                names="Category",
                                hole=0.4
                            )
                        else:
                            fig_pie = px.pie(
                                combined_alloc_df,
                                values="Allocated Amount",
                                names="Category",
                                hole=0.4
                            )
                        fig_pie.update_layout(height=350)
                        st.plotly_chart(fig_pie, use_container_width=True)
                    
                    with col2:
                        st.subheader("Spent vs Allocated")
                        # Aggregate by category if multi-period
                        if len(selected_years) > 1 or len(selected_months) > 1:
                            agg_alloc = combined_alloc_df.groupby('Category').agg({
                                'Allocated Amount': 'sum',
                                'Spent Amount': 'sum'
                            }).reset_index()
                            fig_bar = go.Figure()
                            fig_bar.add_trace(go.Bar(
                                name="Allocated",
                                x=agg_alloc["Category"],
                                y=agg_alloc["Allocated Amount"],
                                marker_color='lightblue'
                            ))
                            fig_bar.add_trace(go.Bar(
                                name="Spent",
                                x=agg_alloc["Category"],
                                y=agg_alloc["Spent Amount"],
                                marker_color='coral'
                            ))
                        else:
                            fig_bar = go.Figure()
                            fig_bar.add_trace(go.Bar(
                                name="Allocated",
                                x=combined_alloc_df["Category"],
                                y=combined_alloc_df["Allocated Amount"],
                                marker_color='lightblue'
                            ))
                            fig_bar.add_trace(go.Bar(
                                name="Spent",
                                x=combined_alloc_df["Category"],
                                y=combined_alloc_df["Spent Amount"],
                                marker_color='coral'
                            ))
                        fig_bar.update_layout(barmode='group', height=350)
                        st.plotly_chart(fig_bar, use_container_width=True)
                
                # Allocation status table
                st.subheader(f"📋 Allocation Status")
                if not combined_alloc_df.empty:
                    display_df = combined_alloc_df.copy()
                    display_df["Allocated Amount"] = display_df["Allocated Amount"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
                    display_df["Spent Amount"] = display_df["Spent Amount"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
                    display_df["Balance"] = display_df["Balance"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
                    
                    # Show relevant columns based on selection
                    if len(selected_years) > 1 or len(selected_months) > 1:
                        # Show year/month columns for multi-period view
                        display_cols = ['Category', 'year', 'month', 'Allocated Amount', 'Spent Amount', 'Balance']
                    else:
                        # Single period - hide year/month
                        display_cols = ['Category', 'Allocated Amount', 'Spent Amount', 'Balance']
                    
                    display_df_filtered = display_df[[col for col in display_cols if col in display_df.columns]]
                    st.dataframe(display_df_filtered, use_container_width=True, hide_index=True)
                else:
                    st.info("ℹ️ No allocation data found for selected period(s). Try different years/months or create allocations first!")
    
    # TAB 5: Savings
    elif selected_tab == "💰 Savings":
        st.header("💰 Savings Tracker")
        st.caption("Track your household's liquid funds (Income - Allocations)")
        
        st.subheader("📊 Savings History - Liquidity by Year")
        
        # Get user info from session state (same as other tabs)
        current_user = st.session_state.user
        is_admin = current_user['role'] == 'admin'  # Role is 'admin' not 'family_admin'
        household_id = current_user['household_id']

        
        # Get all years with data
        years = db.get_savings_years(user_id, is_admin, household_id)

        
        if not years:
            st.info("💡 No income/allocation data found. Add income in the Income tab to see liquidity here!")
        else:
            st.caption(f"**Liquidity** = Income - Total Allocations for each month")

            
            # Display year-wise expandable sections
            for year in years:
                
                # Get monthly liquidity data for this year
                try:
                    liquidity_df = db.get_monthly_liquidity_by_member_simple(household_id, year, is_admin, user_id)

                except Exception as e:
                    st.error(f"Error getting liquidity for {year}: {str(e)}")
                    continue
                
                if liquidity_df.empty:
                    continue
                
                # Calculate year total for family
                year_total = liquidity_df['liquidity'].sum()
                
                # Create expandable section
                # For admin: show Family Total, for member: show My Personal Liquidity
                expander_label = f"📅 **{year}** - Family Total Liquidity: {config.CURRENCY_SYMBOL}{year_total:,.2f}" if is_admin else f"👤 **My Personal Liquidity - {year}**: {config.CURRENCY_SYMBOL}{year_total:,.2f}"
                
                with st.expander(expander_label, expanded=False):
                    if is_admin:
                        # For admin: Pivot to show members as columns
                        # Create pivot table: Month x Members
                        pivot_df = liquidity_df.pivot(
                            index='month',
                            columns='member',
                            values='liquidity'
                        ).fillna(0)
                        
                        # Add Total column (sum across all members)
                        pivot_df['Total'] = pivot_df.sum(axis=1)
                        
                        # Format month names
                        import calendar
                        pivot_df.index = pivot_df.index.map(lambda x: calendar.month_name[x])
                        pivot_df.index.name = 'Month'
                        
                        # Format currency
                        styled_df = pivot_df.copy()
                        for col in styled_df.columns:
                            styled_df[col] = styled_df[col].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
                        
                        st.dataframe(styled_df, use_container_width=True)
                    else:
                        # For member: Show only Month and Liquidity
                        try:
                            display_df = liquidity_df.copy()
                            
                            # Convert month (handle both int and float)
                            import calendar
                            display_df['Month'] = display_df['month'].apply(lambda x: calendar.month_name[int(float(x))])
                            
                            # Format liquidity
                            display_df['Liquidity'] = display_df['liquidity'].apply(lambda x: f"{config.CURRENCY_SYMBOL}{float(x):,.2f}")
                            
                            # Display only Month and Liquidity
                            st.dataframe(
                                display_df[['Month', 'Liquidity']],
                                use_container_width=True,
                                hide_index=True
                            )
                        except Exception as e:
                            st.error(f"Error displaying member liquidity: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())
                
                # Add personal liquidity section for admin (outside expander)
                if is_admin:
                    st.divider()
                    
                    # Get admin's personal liquidity
                    admin_liquidity_df = db.get_monthly_liquidity_by_member_simple(household_id, year, False, user_id)
                    
                    if not admin_liquidity_df.empty:
                        # Calculate personal total
                        personal_total = admin_liquidity_df['liquidity'].sum()
                        
                        # Create expander for personal liquidity
                        with st.expander(f"👤 **My Personal Liquidity - {year}**: {config.CURRENCY_SYMBOL}{personal_total:,.2f}", expanded=False):
                            display_df = admin_liquidity_df.copy()
                            
                            # Convert month and format liquidity
                            import calendar
                            display_df['Month'] = display_df['month'].apply(lambda x: calendar.month_name[int(float(x))])
                            display_df['Liquidity'] = display_df['liquidity'].apply(lambda x: f"{config.CURRENCY_SYMBOL}{float(x):,.2f}")
                            
                            # Display only Month and Liquidity
                            st.dataframe(
                                display_df[['Month', 'Liquidity']],
                                use_container_width=True,
                                hide_index=True
                            )
                    else:
                        st.info("💡 No personal liquidity data for this year")
            
            st.divider()
            st.caption("💡 **Tip:** Liquidity shows unallocated funds. Positive values mean you have extra money, negative means you over-allocated!")




# ==================== SUPER ADMIN DASHBOARD ====================

#superadmin superpower - START
# Login as Family feature
# Comment out this entire block to disable family name hyperlinks
ENABLE_LOGIN_AS_FAMILY = True
#superadmin superpower - END

def show_super_admin_dashboard():
    """Super admin dashboard for managing multiple households"""
    user = st.session_state.user
    
    # Check if logged in as family via superadmin
    is_superadmin_impersonating = st.session_state.get('original_superadmin') is not None
    
    # Header with logout and optional return button
    if is_superadmin_impersonating:
        col1, col2, col3 = st.columns([5, 1, 1])
    else:
        col1, col2 = st.columns([6, 1])
    
    with col1:
        st.title("🔱 Super Admin Dashboard")
        st.caption(f"Welcome, {user['full_name']}")
    with col2:
        st.write("")  # Spacer for alignment
        if st.button("Logout", key="super_logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.original_superadmin = None  # Clear impersonation
            st.rerun()
    
    #superadmin superpower - START
    if is_superadmin_impersonating:
        with col3:
            st.write("")  # Spacer
            if st.button("↩️ Return", key="return_to_superadmin", use_container_width=True, help="Return to Super Admin"):
                # Restore original superadmin user
                st.session_state.user = st.session_state.original_superadmin
                st.session_state.original_superadmin = None
                st.success("Returned to Super Admin")
                st.rerun()
    #superadmin superpower - END
    
    st.divider()
    
    # Main tabs - now with 4 tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🏠 Manage Families", "👥 Manage Members", "📋 All Users"])
    
    # TAB 1: Overview
    with tab1:
        st.header("System Overview")
        
        # Get statistics
        stats = db.get_system_statistics()
        
        # Display metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Households", stats.get('total_households', 0))
        with col2:
            st.metric("Active Households", stats.get('active_households', 0))
        with col3:
            st.metric("Total Users", stats.get('total_users', 0))
        with col4:
            st.metric("Family Admins", stats.get('total_admins', 0))
        with col5:
            st.metric("Members", stats.get('total_members', 0))
        
        st.divider()
        
        # Recent households
        st.subheader("Recent Households")
        households_df = db.get_all_households()
        if not households_df.empty:
            display_df = households_df[['name', 'admin_name', 'admin_email', 'member_count', 'is_active', 'created_at']].copy()
            # Handle both PostgreSQL (True/False) and SQLite (1/0)
            display_df['is_active'] = display_df['is_active'].apply(lambda x: '✅ Active' if x else '❌ Inactive')
            # Format created_at only if dataframe has rows
            if len(display_df) > 0 and 'created_at' in display_df.columns:
                try:
                    display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d')
                except:
                    pass  # Keep original format if parsing fails
            display_df.columns = ['Family Name', 'Admin Name', 'Admin Email', 'Members', 'Status', 'Created']
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("No households created yet")
    
    # TAB 2: Manage Families
    with tab2:
        st.header("Family Household Management")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("➕ Create New Family")
            
            with st.form("create_household_form", clear_on_submit=True):
                household_name = st.text_input("Family/Household Name", placeholder="e.g., Smith Family")
                admin_name = st.text_input("Family Admin Name")
                admin_email = st.text_input("Family Admin Email")
                
                create_btn = st.form_submit_button("Create Family", use_container_width=True)
                
                if create_btn:
                    if not all([household_name, admin_name, admin_email]):
                        st.error("Please fill all fields")
                    else:
                        success, household_id, invite_token, message = db.create_household_with_admin(
                            household_name, admin_email, admin_name
                        )
                        if success:
                            st.success(f"✅ {message}")
                            with st.expander("📧 Admin Invite Token - Click to view", expanded=True):
                                st.info(f"**Share this token with {admin_name}:**")
                                st.code(invite_token, language=None)
                                st.caption("💡 Admin needs this token to set up their password")
                                st.markdown("""
                                **Instructions to share:**
                                1. Share the app URL with the admin
                                2. Click 'Password Setup' on landing page
                                3. Select 'New Password'
                                4. Paste token and create password
                                """)
                            st.cache_data.clear()
                            # Don't auto-rerun so user can copy token
                        else:
                            st.error(f"❌ {message}")
        
        with col2:
            st.subheader("📋 All Families")
            
            households_df = db.get_all_households()
            
            if not households_df.empty:
                for idx, household in households_df.iterrows():
                    # Skip if ID is not valid (e.g., header row)
                    try:
                        household_id = int(household['id'])
                    except (ValueError, TypeError):
                        continue  # Skip this row if ID is not a number
                    
                    with st.container():
                        col_info, col_actions = st.columns([3, 1])
                        
                        with col_info:
                            # Handle both PostgreSQL (True/False) and SQLite (1/0)
                            status_icon = "✅" if household['is_active'] else "❌"
                            
                            #superadmin superpower - START
                            # Make family name clickable to login as that family
                            if ENABLE_LOGIN_AS_FAMILY:
                                if st.button(f"{status_icon} {household['name']}", key=f"login_{household_id}", type="secondary"):
                                    st.session_state.show_password_modal = household_id
                                    st.session_state.selected_household_name = household['name']
                                st.caption(f"👤 Admin: {household['admin_name']} ({household['admin_email']})  |  👥 Members: {household['member_count']} | 📅 Created: {str(household['created_at'])[:10]}")
                            else:
                            #superadmin superpower - END
                                st.markdown(f"""
                                **{household['name']}** {status_icon}  
                                👤 Admin: {household['admin_name']} ({household['admin_email']})  
                                👥 Members: {household['member_count']} | 📅 Created: {str(household['created_at'])[:10]}
                                """)
                        
                        with col_actions:
                            col_toggle, col_delete = st.columns(2)
                            
                            with col_toggle:
                                # Handle both PostgreSQL (True/False) and SQLite (1/0)
                                toggle_label = "❌" if household['is_active'] else "✅"
                                if st.button(toggle_label, key=f"toggle_{household_id}", help="Enable/Disable"):
                                    if db.toggle_household_status(household_id):
                                        st.cache_data.clear()
                                        st.rerun()
                            
                            with col_delete:
                                if st.button("🗑️", key=f"del_{household_id}", help="Delete"):
                                    st.session_state[f'confirm_del_h_{household_id}'] = True
                                    st.rerun()
                            
                            # Confirmation dialog
                            if st.session_state.get(f'confirm_del_h_{household_id}', False):
                                st.warning(f"Delete '{household['name']}'?")
                                col_yes, col_no = st.columns(2)
                                with col_yes:
                                    if st.button("Yes", key=f"yes_h_{household_id}"):
                                        success, msg = db.delete_household(household_id)
                                        if success:
                                            st.success(msg)
                                            st.session_state.pop(f'confirm_del_h_{household_id}')
                                            st.cache_data.clear()
                                            st.rerun()
                                        else:
                                            st.error(msg)
                                with col_no:
                                    if st.button("No", key=f"no_h_{household_id}"):
                                        st.session_state.pop(f'confirm_del_h_{household_id}')
                                        st.rerun()
                        
                        st.divider()
            else:
                st.info("No families created yet. Create one using the form on the left.")
            
            #superadmin superpower - START
            # Password verification modal for "Login as Family"
            if st.session_state.get('show_password_modal'):
                household_id = st.session_state.show_password_modal
                household_name = st.session_state.get('selected_household_name', 'Unknown')
                
                st.divider()
                
                # Step 1: Password verification (if not yet verified)
                if not st.session_state.get('password_verified'):
                    with st.expander(f"🔐 Verify Password to Login as {household_name}", expanded=True):
                        st.warning(f"You are about to log in as a member of **{household_name}**")
                        
                        password = st.text_input(
                            "Super Admin Password", 
                            type="password", 
                            key="verify_pwd",
                            placeholder="Enter your superadmin password"
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Verify", use_container_width=True, type="primary"):
                                if password:
                                    # Verify superadmin password
                                    success, super_user = db.authenticate_user(st.session_state.user['email'], password)
                                    
                                    if success and super_user and super_user.get('role') == 'superadmin':
                                        st.session_state.password_verified = True
                                        st.success("✅ Password verified! Select a member below.")
                                        st.rerun()
                                    else:
                                        st.error("❌ Invalid password")
                                else:
                                    st.error("Please enter your password")
                        
                        with col2:
                            if st.button("❌ Cancel", use_container_width=True):
                                st.session_state.show_password_modal = None
                                st.session_state.selected_household_name = None
                                st.session_state.password_verified = False
                                st.rerun()
                
                # Step 2: Member selection (after password is verified)
                else:
                    with st.expander(f"👥 Select Member from {household_name}", expanded=True):
                        st.success("✅ Password verified")
                        st.info(f"Select which member of **{household_name}** to log in as:")
                        
                        # Get all household members
                        cursor = db.conn.cursor()
                        db._execute(cursor, '''
                            SELECT id, full_name, email, role, relationship
                            FROM users
                            WHERE household_id = %s
                            ORDER BY 
                                CASE WHEN role = 'admin' THEN 0 ELSE 1 END,
                                full_name
                        ''', (household_id,))
                        
                        members = cursor.fetchall()
                        
                        if members:
                            # Display members as buttons
                            for member in members:
                                member_id = member['id'] if isinstance(member, dict) else member[0]
                                member_name = member['full_name'] if isinstance(member, dict) else member[1]
                                member_email = member['email'] if isinstance(member, dict) else member[2]
                                member_role = member['role'] if isinstance(member, dict) else member[3]
                                member_relationship = member['relationship'] if isinstance(member, dict) else member[4]
                                
                                # Icon based on role
                                icon = "👑" if member_role == 'admin' else "👤"
                                role_badge = "Admin" if member_role == 'admin' else "Member"
                                
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.markdown(f"{icon} **{member_name}** ({role_badge})")
                                    st.caption(f"📧 {member_email} | {member_relationship}")
                                
                                with col2:
                                    if st.button("Login", key=f"login_as_{member_id}", use_container_width=True, type="primary"):
                                        # Create user dict for selected member
                                        selected_member = {
                                            'id': member_id,
                                            'full_name': member_name,
                                            'email': member_email,
                                            'role': member_role,
                                            'household_id': household_id,
                                            'relationship': member_relationship
                                        }
                                        
                                        # Store original superadmin
                                        st.session_state.original_superadmin = st.session_state.user.copy()
                                        # Switch to selected member
                                        st.session_state.user = selected_member
                                        st.session_state.show_password_modal = None
                                        st.session_state.selected_household_name = None
                                        st.session_state.password_verified = False
                                        st.success(f"✅ Logged in as {member_name} ({household_name})")
                                        st.rerun()
                                
                                st.divider()
                            
                            # Cancel button at bottom
                            if st.button("❌ Cancel", key="cancel_member_selection", use_container_width=True):
                                st.session_state.show_password_modal = None
                                st.session_state.selected_household_name = None
                                st.session_state.password_verified = False
                                st.rerun()
                        else:
                            st.error(f"❌ No members found in {household_name}")
            #superadmin superpower - END
    
    # TAB 3: Manage Members (Family-Filtered)
    with tab3:
        st.header("Member Management")
        
        households_df = db.get_all_households()
        
        if households_df.empty:
            st.info("📋 No families created yet. Go to 'Manage Families' tab to create one.")
        else:
            # Family Selector
            family_options = {row['name']: row['id'] for _, row in households_df.iterrows()}
            
            selected_family_name = st.selectbox(
                "🏠 Select Family",
                options=["-- Choose a family --"] + list(family_options.keys()),
                help="Select a family to view and manage its members"
            )
            
            if selected_family_name == "-- Choose a family --":
                st.info("👆 Please select a family from the dropdown above to manage its members.")
            else:
                selected_household_id = family_options[selected_family_name]
                
                st.divider()
                
                # Two column layout
                col1, col2 = st.columns([1, 2])
                
                # LEFT COLUMN: Add Member Form
                with col1:
                    st.subheader("➕ Add Member")
                    
                    with st.form("add_member_super_form", clear_on_submit=True):
                        member_name = st.text_input("Member Name")
                        member_email = st.text_input("Member Email")
                        member_relationship = st.selectbox("Relationship", 
                            ["Spouse", "Parent", "Child", "Sibling", "Other"])
                        
                        add_member_btn = st.form_submit_button("Add Member", use_container_width=True)
                        
                        if add_member_btn:
                            if not all([member_name, member_email]):
                                st.error("Please fill all fields")
                            else:
                                success, member_id, invite_token = db.add_member_to_family_super_admin(
                                    selected_household_id, member_email, member_name, member_relationship
                                )
                                if success:
                                    st.success(f"✅ Member added to {selected_family_name}")
                                    with st.expander("📧 Member Invite Token - Click to view", expanded=True):
                                        st.info(f"**Share this token with {member_name}:**")
                                        st.code(invite_token, language=None)
                                        st.caption("💡 Member needs this token to set up their password")
                                        st.markdown("""
                                        **Instructions to share:**
                                        1. Share the app URL with the member
                                        2. Click 'Password Setup' on landing page
                                        3. Select 'New Password'
                                        4. Paste token and create password
                                        """)
                                    st.cache_data.clear()
                                    # Don't auto-rerun so user can copy token
                                else:
                                    st.error(f"❌ {invite_token}")
                
                # RIGHT COLUMN: Members List
                with col2:
                    st.subheader(f"👥 Members of {selected_family_name}")
                    
                    # Get members for selected family
                    all_users_df = db.get_all_users_super_admin()
                    
                    if not all_users_df.empty:
                        family_members = all_users_df[all_users_df['household_name'] == selected_family_name]
                        
                        if not family_members.empty:
                            # Count admins for this family
                            admin_count = db.count_household_admins(selected_household_id)
                            
                            st.caption(f"Total: {len(family_members)} members | Admins: {admin_count}")
                            st.divider()
                            
                            # Display each member
                            for _, user in family_members.iterrows():
                                with st.container():
                                    col_info, col_actions = st.columns([3, 2])
                                    
                                    with col_info:
                                        role_icon = "👑" if user['role'] == 'admin' else "👤"
                                        status_icon = "✅" if user['is_active'] else "❌"
                                        st.markdown(f"""
                                        {role_icon} **{user['full_name']}** {status_icon}  
                                        📧 {user['email']} | Role: {user['role'].title()}
                                        """)
                                    
                                    with col_actions:
                                        is_admin = user['role'] == 'admin'
                                        user_id = user['id']
                                        
                                        if is_admin:
                                            # ADMIN USER: Show Remove Admin + Delete (disabled)
                                            can_remove_admin = admin_count > 1
                                            
                                            # Remove Admin Button
                                            if st.button(
                                                "⬇️ Remove Admin", 
                                                key=f"demote_{user_id}",
                                                disabled=(not can_remove_admin),
                                                help="Cannot demote the only admin" if not can_remove_admin else "Demote to member role",
                                                use_container_width=True
                                            ):
                                                success, msg = db.demote_admin_to_member(user_id, selected_household_id)
                                                if success:
                                                    st.success(msg)
                                                    st.cache_data.clear()
                                                    st.rerun()
                                                else:
                                                    st.error(msg)
                                            
                                            # Delete Member Button (always disabled for admins)
                                            st.button(
                                                "🗑️ Delete Member",
                                                key=f"delete_{user_id}",
                                                disabled=True,
                                                help="Demote admin first before deletion",
                                                use_container_width=True
                                            )
                                            
                                            # Reset Password Button
                                            if st.button("🔄 Reset Password", key=f"reset_pwd_{user_id}", use_container_width=True):
                                                success, new_token, message = db.reset_user_password(user_id)
                                                if success:
                                                    st.success("✅ Password reset successfully!")
                                                    with st.expander("🔑 New Invite Token - Click to view", expanded=True):
                                                        st.info(f"**Share this token with {user['full_name']}:**")
                                                        st.code(new_token, language=None)
                                                        st.caption("💡 User must use Password Setup → New Password to set their password")
                                                        st.markdown("""
                                                        **Instructions:**
                                                        1. Share token with user
                                                        2. User clicks Password Setup → New Password
                                                        3. User pastes token and creates new password
                                                        """)
                                                    st.cache_data.clear()
                                                else:
                                                    st.error(f"❌ {message}")
                                        else:
                                            # REGULAR MEMBER: Show Make Admin + Delete (enabled)
                                            
                                            # Make Admin Button
                                            if st.button("⬆️ Make Admin", key=f"promote_{user_id}", use_container_width=True):
                                                success, msg = db.promote_member_to_admin(user_id, selected_household_id)
                                                if success:
                                                    st.success(msg)
                                                    st.cache_data.clear()
                                                    st.rerun()
                                                else:
                                                    st.error(msg)
                                            
                                            # Delete Member Button (with confirmation)
                                            if st.button("🗑️ Delete Member", key=f"delete_{user_id}", use_container_width=True):
                                                st.session_state[f'confirm_delete_member_{user_id}'] = True
                                                st.rerun()
                                            
                                            # Confirmation dialog
                                            if st.session_state.get(f'confirm_delete_member_{user_id}', False):
                                                st.warning(f"⚠️ Delete {user['full_name']}? This action cannot be undone.")
                                                col_yes, col_no = st.columns(2)
                                                with col_yes:
                                                    if st.button("✓ Yes", key=f"yes_del_{user_id}"):
                                                        if db.delete_member(user_id):
                                                            st.success(f"Deleted {user['full_name']}")
                                                            st.session_state.pop(f'confirm_delete_member_{user_id}')
                                                            st.cache_data.clear()
                                                            st.rerun()
                                                        else:
                                                            st.error("Failed to delete member")
                                                with col_no:
                                                    if st.button("✗ No", key=f"no_del_{user_id}"):
                                                        st.session_state.pop(f'confirm_delete_member_{user_id}')
                                                        st.rerun()
                                            
                                            # Reset Password Button
                                            if st.button("🔄 Reset Password", key=f"reset_pwd_member_{user_id}", use_container_width=True):
                                                success, new_token, message = db.reset_user_password(user_id)
                                                if success:
                                                    st.success("✅ Password reset successfully!")
                                                    with st.expander("🔑 New Invite Token - Click to view", expanded=True):
                                                        st.info(f"**Share this token with {user['full_name']}:**")
                                                        st.code(new_token, language=None)
                                                        st.caption("💡 User must use Password Setup → New Password to set their password")
                                                        st.markdown("""
                                                        **Instructions:**
                                                        1. Share token with user
                                                        2. User clicks Password Setup → New Password
                                                        3. User pastes token and creates new password
                                                        """)
                                                    st.cache_data.clear()
                                                else:
                                                    st.error(f"❌ {message}")
                                    
                                    st.divider()
                        else:
                            st.info("No members in this family yet.")
                    else:
                        st.info("No users found in the system.")
    
    # TAB 4: All Users
    with tab4:
        st.header("All Users Across Families")
        
        users_df = db.get_all_users_super_admin()
        
        if not users_df.empty:
            display_df = users_df[['full_name', 'email', 'household_name', 'role', 'is_active', 'created_at']].copy()
            # Handle both PostgreSQL (True/False) and SQLite (1/0)
            display_df['is_active'] = display_df['is_active'].apply(lambda x: '✅' if x else '❌')
            display_df['role'] = display_df['role'].str.title()
            # Only parse datetime if the dataframe has rows
            if len(display_df) > 0 and 'created_at' in display_df.columns:
                try:
                    display_df['created_at'] = pd.to_datetime(display_df['created_at']).dt.strftime('%Y-%m-%d')
                except:
                    pass  # Keep original format if parsing fails
            display_df.columns = ['Name', 'Email', 'Family', 'Role', 'Active', 'Joined']
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                family_filter = st.multiselect(
                    "Filter by Family",
                    options=display_df['Family'].unique().tolist(),
                    default=[]
                )
            with col2:
                role_filter = st.multiselect(
                    "Filter by Role",
                    options=display_df['Role'].unique().tolist(),
                    default=[]
                )
            
            # Apply filters
            filtered_df = display_df.copy()
            if family_filter:
                filtered_df = filtered_df[filtered_df['Family'].isin(family_filter)]
            if role_filter:
                filtered_df = filtered_df[filtered_df['Role'].isin(role_filter)]
            
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
            st.caption(f"Showing {len(filtered_df)} of {len(display_df)} users")
        else:
            st.info("No users found")

# ==================== MAIN APPLICATION FLOW ====================

def main():
    """Main application logic"""
    
    if not st.session_state.logged_in:
        show_login_page()
    else:
        user = st.session_state.user
        
        # VERSION MARKER - to confirm new code is deployed
        # st.write("🔴 **CODE VERSION: 2026-01-01-03:06 - FULL AI CHATBOT ACTIVE**")
        
        # CHATBOT in MAIN area (sidebar workaround)
        with st.expander("🤖 **Budget Assistant Chatbot** (Click to expand)", expanded=False):
            st.write("**Welcome to your AI Budget Assistant!**")
            st.write("Ask me about your expenses, income, allocations, or how to use the tracker.")
            st.write("")
            
            # Initialize chat state
            if 'chat_msgs' not in st.session_state:
                st.session_state.chat_msgs = []
            
            # Display chat history in scrollable container FIRST
            st.markdown("---")
            
            # Build chat HTML with scrollable container
            chat_html = '''
            <style>
            #chat-container {
                height: 50vh;
                max-height: 400px;
                overflow-y: auto;
                padding: 20px;
                background: linear-gradient(to bottom, #f0f2f5, #ffffff);
                border-radius: 10px;
                margin-bottom: 0px;
                border: 1px solid #e0e0e0;
            }
            #chat-container::-webkit-scrollbar {
                width: 8px;
            }
            #chat-container::-webkit-scrollbar-track {
                background: #f1f1f1;
                border-radius: 10px;
            }
            #chat-container::-webkit-scrollbar-thumb {
                background: #888;
                border-radius: 10px;
            }
            #chat-container::-webkit-scrollbar-thumb:hover {
                background: #555;
            }
            .user-message {
                text-align: right;
                margin: 10px 0;
                clear: both;
            }
            .user-bubble {
                display: inline-block;
                background: #0084ff;
                color: white;
                padding: 12px 16px;
                border-radius: 18px 18px 4px 18px;
                max-width: 70%;
                text-align: left;
                word-wrap: break-word;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
            .assistant-message {
                text-align: left;
                margin: 10px 0;
                clear: both;
            }
            .assistant-bubble {
                display: inline-block;
                background: #e4e6eb;
                color: #050505;
                padding: 12px 16px;
                border-radius: 18px 18px 18px 4px;
                max-width: 70%;
                text-align: left;
                word-wrap: break-word;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }
            .empty-chat {
                text-align: center;
                color: #888;
                margin-top: 30vh;
                font-style: italic;
            }
            </style>
            <div id="chat-container">
            '''
            
            if st.session_state.chat_msgs:
                for role, msg in st.session_state.chat_msgs:
                    # Escape HTML in message
                    msg_escaped = msg.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
                    
                    if role == "You":
                        chat_html += f'''
                        <div class="user-message">
                            <div class="user-bubble">{msg_escaped}</div>
                        </div>
                        '''
                    else:
                        chat_html += f'''
                        <div class="assistant-message">
                            <div class="assistant-bubble">🤖 {msg_escaped}</div>
                        </div>
                        '''
            else:
                chat_html += '<div class="empty-chat">💬 No messages yet. Ask me a question to get started!</div>'
            
            chat_html += '</div>'
            
            # Auto-scroll JavaScript
            chat_html += '''
            <script>
            setTimeout(function() {
                var container = document.getElementById('chat-container');
                if (container) {
                    container.scrollTop = container.scrollHeight;
                }
            }, 100);
            </script>
            '''
            
            # Render using components for better HTML support
            import streamlit.components.v1 as components
            components.html(chat_html, height=350, scrolling=False)
            
            
            # Minimal spacing instead of divider (no blank space)
            st.markdown('<div style="margin-top: 5px;"></div>', unsafe_allow_html=True)
            user_question = st.text_input("💬 Type your message:", key="chat_input", placeholder="e.g., How much did I spend on groceries?")
            
            col1, col2 = st.columns([1, 5])
            with col1:
                send_clicked = st.button("📤 Send", key="send_btn", use_container_width=True, type="primary")
            with col2:
                if st.button("🗑️ Clear Chat", key="clear_btn"):
                    st.session_state.chat_msgs = []
                    st.rerun()
            
            if send_clicked and user_question:
                # Add user message
                st.session_state.chat_msgs.append(("You", user_question))
                
                # Get AI response
                try:
                    # Import and initialize chatbot engine
                    from chatbot_engine import ChatbotEngine
                    
                    with st.spinner("🤔 Thinking..."):
                        chatbot = ChatbotEngine(
                            docs_directory=config.CHATBOT_DOCS_DIR,
                            api_key=config.GEMINI_API_KEY
                        )
                        
                        response = chatbot.process_query(
                            query=user_question,
                            user_id=user['id'],
                            family_id=user['household_id'],
                            role=user['role'],
                            full_name=user['full_name'],
                            db_connection=db
                        )
                    
                    # Add AI response
                    st.session_state.chat_msgs.append(("Assistant", response))
                    
                except Exception as e:
                    error_msg = f"⚠️ Error: {str(e)}"
                    st.session_state.chat_msgs.append(("Assistant", error_msg))
                
                st.rerun()
        
        # Route to appropriate dashboard
        if user['role'] == 'superadmin':
            show_super_admin_dashboard()
        elif user['role'] == 'admin':
            show_admin_dashboard()
        elif user['role'] == 'member':
            show_member_dashboard()

if __name__ == "__main__":
    main()
