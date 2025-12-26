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

# Page configuration
st.set_page_config(
    page_title="Family Budget Tracker",
    page_icon="👨‍👩‍👧‍👦",
    layout="wide",
    initial_sidebar_state="collapsed"
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

# ==================== AUTHENTICATION PAGES ====================

def show_login_page():
    """Display login and signup page"""
    st.title("👨‍👩‍👧‍👦 Family Budget Tracker")
    
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Create Admin Account", "🔑 Setup Password (Members)"])
    
    with tab1:
        st.subheader("Login to Your Account")
        
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if email and password:
                    success, user_data = db.authenticate_user(email, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user = user_data
                        st.success(f"Welcome, {user_data['full_name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
                else:
                    st.error("Please enter both email and password")
    
    with tab2:
        st.subheader("Create Admin Account")
        st.info("Create the first admin account for your household")
        
        with st.form("signup_form"):
            household_name = st.text_input("Household/Family Name", placeholder="e.g., Smith Family")
            full_name = st.text_input("Your Full Name")
            signup_email = st.text_input("Email Address")
            signup_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            submit_signup = st.form_submit_button("Create Account", use_container_width=True)
            
            if submit_signup:
                if not all([household_name, full_name, signup_email, signup_password]):
                    st.error("Please fill all fields")
                elif signup_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(signup_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    success, user_id, message = db.create_admin_user(
                        signup_email, signup_password, full_name, household_name
                    )
                    if success:
                        st.success(f"✅ {message} Please login with your credentials.")
                    else:
                        st.error(f"❌ {message}")
    
    with tab3:
        st.subheader("🔑 Setup Your Password")
        st.info("If you were invited to join a household, use your invite token to set your password")
        
        with st.form("password_setup_form"):
            invite_token = st.text_input("Invite Token", placeholder="Paste the token shared by your admin")
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
                        st.info("You can now login with your email and new password!")
                    else:
                        st.error(f"❌ {message}")


# ==================== ADMIN DASHBOARD ====================

def show_admin_dashboard():
    """Display admin dashboard with family overview"""
    user = st.session_state.user
    household_id = user['household_id']
    
    st.title(f"👨‍👩‍👧‍👦 Family Budget Dashboard")
    st.caption(f"Admin: {user['full_name']}")
    
    # Logout button
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()
    
    st.divider()
    
    # Tabs for admin functions
    tab1, tab2, tab3 = st.tabs(["📊 Family Overview", "👥 Manage Members", "💰 My Expenses"])
    
    # TAB 1: Family Overview
    with tab1:
        st.header("📊 Family Financial Overview")
        
        # Get household totals
        total_household_income = db.get_household_total_income(household_id)
        total_household_expenses = db.get_household_total_expenses(household_id)
        total_household_savings = total_household_income - total_household_expenses
        
        # Display household metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Total Family Income", f"{config.CURRENCY_SYMBOL}{total_household_income:,.2f}")
        with col2:
            st.metric("💸 Total Family Expenses", f"{config.CURRENCY_SYMBOL}{total_household_expenses:,.2f}")
        with col3:
            st.metric("💵 Total Family Savings", f"{config.CURRENCY_SYMBOL}{total_household_savings:,.2f}")
        
        st.divider()
        
        # Member-wise summary
        st.subheader("👥 Member-wise Financial Summary")
        member_summary = db.get_household_member_summary(household_id)
        
        if not member_summary.empty:
            # Format currency columns
            for col in ['Income', 'Expenses', 'Savings']:
                member_summary[col] = member_summary[col].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
            
            st.dataframe(member_summary, use_container_width=True, hide_index=True)
            
            # Visualization
            st.subheader("📈 Member Contribution Visualization")
            # Re-fetch for visualization (without formatting)
            member_summary_viz = db.get_household_member_summary(household_id)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Income",
                x=member_summary_viz['Member'],
                y=member_summary_viz['Income'],
                marker_color='lightgreen'
            ))
            fig.add_trace(go.Bar(
                name="Expenses",
                x=member_summary_viz['Member'],
                y=member_summary_viz['Expenses'],
                marker_color='lightcoral'
            ))
            fig.update_layout(
                barmode='group',
                height=400,
                xaxis_title="Family Member",
                yaxis_title=f"Amount ({config.CURRENCY_SYMBOL})"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No financial data yet. Add members and start tracking!")
    
    # TAB 2: Manage Members
    with tab2:
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
                        
                        st.divider()
            else:
                st.info("No additional members yet")
    
    # TAB 3: Admin's Personal Expenses
    with tab3:
        st.header("💰 My Personal Expenses")
        st.caption("Track your own income and expenses")
        
        # Reuse member dashboard for admin's personal tracking
        show_member_expense_tracking(user['id'])

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
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "💵 Income", "🎯 Allocations", "💸 Expenses"])
    
    # TAB 1: Dashboard
    with tab1:
        st.header("📊 Financial Dashboard")
        
        # Get data
        total_income = db.get_total_income(user_id)
        allocations_df = db.get_all_allocations(user_id)
        total_expenses = db.get_total_expenses(user_id)
        
        # Calculate metrics
        total_allocated = allocations_df["Allocated Amount"].sum() if not allocations_df.empty else 0
        total_spent = allocations_df["Spent Amount"].sum() if not allocations_df.empty else 0
        total_balance = allocations_df["Balance"].sum() if not allocations_df.empty else 0
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
        if not allocations_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Allocation Breakdown")
                fig_pie = px.pie(
                    allocations_df,
                    values="Allocated Amount",
                    names="Category",
                    hole=0.4
                )
                fig_pie.update_layout(height=350)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.subheader("Spent vs Allocated")
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(
                    name="Allocated",
                    x=allocations_df["Category"],
                    y=allocations_df["Allocated Amount"],
                    marker_color='lightblue'
                ))
                fig_bar.add_trace(go.Bar(
                    name="Spent",
                    x=allocations_df["Category"],
                    y=allocations_df["Spent Amount"],
                    marker_color='coral'
                ))
                fig_bar.update_layout(barmode='group', height=350)
                st.plotly_chart(fig_bar, use_container_width=True)
        
        # Allocation status table
        st.subheader("📋 Allocation Status")
        if not allocations_df.empty:
            display_df = allocations_df.copy()
            display_df["Allocated Amount"] = display_df["Allocated Amount"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
            display_df["Spent Amount"] = display_df["Spent Amount"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
            display_df["Balance"] = display_df["Balance"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("No allocations yet. Add some in the Allocations tab!")
    
    # TAB 2: Income
    with tab2:
        st.header("💵 Income Management")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Add New Income")
            with st.form("income_form", clear_on_submit=True):
                income_date = st.date_input("Date", value=date.today())
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
            total_income = db.get_total_income(user_id)
            st.metric("💰 Total Income", f"{config.CURRENCY_SYMBOL}{total_income:,.2f}")
            
            income_df = db.get_all_income(user_id)
            if not income_df.empty:
                income_display = income_df.copy()
                income_display["Amount"] = income_display["Amount"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
                st.dataframe(income_display, use_container_width=True, hide_index=True)
            else:
                st.info("No income entries yet")
    
    # TAB 3: Allocations
    with tab3:
        st.header("🎯 Budget Allocations")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Add Allocation")
            with st.form("allocation_form", clear_on_submit=True):
                alloc_category = st.text_input("Category", placeholder="e.g., Groceries, Rent")
                alloc_amount = st.number_input(f"Amount ({config.CURRENCY_SYMBOL})", min_value=0.0, step=100.0)
                
                submit_alloc = st.form_submit_button("➕ Add Allocation", use_container_width=True)
                
                if submit_alloc and alloc_category and alloc_amount > 0:
                    if db.add_allocation(user_id, alloc_category, alloc_amount):
                        st.success(f"✅ Created allocation: {alloc_category}")
                        st.cache_resource.clear()
                        st.rerun()
                    else:
                        st.error("Category already exists!")
        
        with col2:
            st.subheader("Current Allocations")
            
            allocations_df = db.get_all_allocations(user_id)
            if not allocations_df.empty:
                display_df = allocations_df.copy()
                display_df["Allocated Amount"] = display_df["Allocated Amount"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
                display_df["Spent Amount"] = display_df["Spent Amount"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
                display_df["Balance"] = display_df["Balance"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("No allocations yet")
    
    # TAB 4: Expenses
    with tab4:
        st.header("💸 Daily Expenses")
        
        col1, col2 = st.columns([1, 2])
        
        categories = db.get_categories(user_id)
        
        with col1:
            st.subheader("Add New Expense")
            
            if not categories:
                st.warning("⚠️ Create allocation categories first!")
            else:
                with st.form("expense_form", clear_on_submit=True):
                    expense_date = st.date_input("Date", value=date.today())
                    expense_category = st.selectbox("Category", options=categories)
                    expense_amount = st.number_input(f"Amount ({config.CURRENCY_SYMBOL})", min_value=0.0, step=10.0)
                    expense_comment = st.text_area("Comment", placeholder="Brief description")
                    
                    submit_expense = st.form_submit_button("➕ Add Expense", use_container_width=True)
                    
                    if submit_expense and expense_category and expense_amount > 0 and expense_comment:
                        if db.add_expense(user_id, expense_date.strftime(config.DATE_FORMAT), 
                                        expense_category, expense_amount, expense_comment):
                            st.success(f"✅ Added expense: {config.CURRENCY_SYMBOL}{expense_amount:,.2f}")
                            st.cache_resource.clear()
                            st.rerun()
        
        with col2:
            st.subheader("Expense History")
            
            expenses_df = db.get_all_expenses(user_id)
            if not expenses_df.empty:
                total_exp = expenses_df["Amount"].sum()
                st.metric("💸 Total Expenses", f"{config.CURRENCY_SYMBOL}{total_exp:,.2f}")
                
                expenses_display = expenses_df.head(20).copy()
                expenses_display["Amount"] = expenses_display["Amount"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
                st.dataframe(expenses_display, use_container_width=True, hide_index=True)
            else:
                st.info("No expenses recorded yet")

# ==================== MAIN APPLICATION FLOW ====================

def main():
    """Main application logic"""
    
    if not st.session_state.logged_in:
        show_login_page()
    else:
        user = st.session_state.user
        
        if user['role'] == 'admin':
            show_admin_dashboard()
        else:
            show_member_dashboard()

if __name__ == "__main__":
    main()
