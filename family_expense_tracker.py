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
    """Display login page with separate tabs for different user types"""
    st.title("👨‍👩‍👧‍👦 Family Budget Tracker")
    st.caption("Multi-Family Budget Management System")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔱 Super Admin Login", 
        "👨‍👩‍👧 Family Admin Login", 
        "👤 Member Login",
        "🔑 Setup Password"
    ])
    
    # TAB 1: Super Admin Login
    with tab1:
        st.subheader("🔱 Super Admin Login")
        st.info("For system administrators only. Manage multiple families and users.")
        
        with st.form("superadmin_login_form"):
            super_email = st.text_input("Email", placeholder="superadmin", key="super_email")
            super_password = st.text_input("Password", type="password", key="super_password")
            super_submit = st.form_submit_button("Login as Super Admin", use_container_width=True)
            
            if super_submit:
                if super_email and super_password:
                    success, user_data = db.authenticate_user(super_email, super_password)
                    if success and user_data.get('role') == 'superadmin':
                        st.session_state.logged_in = True
                        st.session_state.user = user_data
                        st.success(f"Welcome, {user_data['full_name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid super admin credentials or account not found")
                else:
                    st.error("Please enter both email and password")
    
    # TAB 2: Family Admin Login
    with tab2:
        st.subheader("👨‍👩‍👧 Family Admin Login")
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
                        st.success(f"Welcome, {user_data['full_name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials or not a family admin account")
                else:
                    st.error("Please enter both email and password")
    
    # TAB 3: Member Login
    with tab3:
        st.subheader("👤 Family Member Login")
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
                        st.success(f"Welcome, {user_data['full_name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials or not a member account")
                else:
                    st.error("Please enter both email and password")
    
    # TAB 4: Setup Password (for new members)
    with tab4:
        st.subheader("🔑 Setup Your Password")
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
                        st.info("You can now login with your email using the 'Member Login' tab!")
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
        
        if not member_summary.empty and len(member_summary.columns) > 0:
            # Format currency columns - check if columns exist first
            for col in ['Income', 'Expenses', 'Savings']:
                if col in member_summary.columns:
                    member_summary[col] = member_summary[col].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
            
            st.dataframe(member_summary, use_container_width=True, hide_index=True)
            
            # Visualization
            st.subheader("📈 Member Contribution Visualization")
            
            # Use original data for visualization (before formatting)
            member_summary_viz = db.get_household_member_summary(household_id)
            
            # Check if we have the required columns
            if not member_summary_viz.empty and all(col in member_summary_viz.columns for col in ['Member', 'Income', 'Expenses', 'Savings']):
                fig = go.Figure(data=[
                    go.Bar(name='Income', x=member_summary_viz['Member'], y=member_summary_viz['Income']),
                    go.Bar(name='Expenses', x=member_summary_viz['Member'], y=member_summary_viz['Expenses']),
                    go.Bar(name='Savings', x=member_summary_viz['Member'], y=member_summary_viz['Savings'])
                ])
                
                fig.update_layout(
                    barmode='group',
                    title='Financial Overview by Member',
                    xaxis_title='Member',
                    yaxis_title='Amount (₹)',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No member financial data available yet. Add members and start tracking!")
    
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
        
        # Calculate metrics - convert to float to handle PostgreSQL Decimal types
        total_allocated = float(allocations_df["Allocated Amount"].sum()) if not allocations_df.empty else 0.0
        total_spent = float(allocations_df["Spent Amount"].sum()) if not allocations_df.empty else 0.0
        total_balance = float(allocations_df["Balance"].sum()) if not allocations_df.empty else 0.0
        remaining_liquidity = float(total_income) - total_allocated
        
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
            
            # Add recalculate button
            st.caption("💡 If spent amounts show as zero, click below to recalculate from expense data")
            if st.button("🔄 Recalculate Spent Amounts", help="Recalculate spent amounts from actual expenses"):
                with st.spinner("Recalculating..."):
                    try:
                        # Get all allocations for this user
                        cursor = db.conn.cursor()
                        db._execute(cursor, 'SELECT id, category, allocated_amount FROM allocations WHERE user_id = ?', (user_id,))
                        user_allocations = cursor.fetchall()
                        
                        fixed_count = 0
                        for alloc in user_allocations:
                            alloc_id = alloc['id']
                            category = alloc['category']
                            allocated_amount = float(alloc['allocated_amount'])
                            
                            # Calculate total spent for this category
                            db._execute(cursor, 
                                'SELECT SUM(amount) as total_spent FROM expenses WHERE user_id = ? AND category = ?',
                                (user_id, category)
                            )
                            result = cursor.fetchone()
                            total_spent = float(result['total_spent']) if result['total_spent'] else 0.0
                            
                            # Calculate new balance
                            new_balance = allocated_amount - total_spent
                            
                            # Update allocation
                            db._execute(cursor,
                                'UPDATE allocations SET spent_amount = ?, balance = ? WHERE id = ?',
                                (total_spent, new_balance, alloc_id)
                            )
                            fixed_count += 1
                        
                        # Commit changes
                        db.conn.commit()
                        st.success(f"✅ Successfully recalculated {fixed_count} allocations! Refreshing...")
                        st.cache_resource.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error recalculating: {str(e)}")
                        db.conn.rollback()
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
            
            income_df = db.get_income_with_ids(user_id)
            if not income_df.empty:
                # Header row
                header_cols = st.columns([2, 2, 2, 1.5])
                header_cols[0].markdown("**Date**")
                header_cols[1].markdown("**Source**")
                header_cols[2].markdown("**Amount**")
                header_cols[3].markdown("**Actions**")
                
                st.divider()
                
                # Render each row
                for idx, row in income_df.iterrows():
                    income_id = int(row['id'])
                    edit_key = f'edit_income_{income_id}'
                    is_editing = st.session_state.get(edit_key, False)
                    
                    cols = st.columns([2, 2, 2, 1.5])
                    
                    if is_editing:
                        # Edit mode: show input fields
                        with cols[0]:
                            new_date = st.date_input("", value=pd.to_datetime(row['date']).date(), key=f"date_{income_id}", label_visibility="collapsed")
                        with cols[1]:
                            new_source = st.text_input("", value=row['source'], key=f"source_{income_id}", label_visibility="collapsed")
                        with cols[2]:
                            new_amount = st.number_input("", value=float(row['amount']), min_value=0.0, step=100.0, key=f"amount_{income_id}", label_visibility="collapsed")
                        
                        with cols[3]:
                            btn_cols = st.columns(3)
                            with btn_cols[0]:
                                st.button("✏️", key=f"edit_income_btn_{income_id}", disabled=True, help="Edit", use_container_width=True)
                            with btn_cols[1]:
                                if st.button("💾", key=f"update_income_{income_id}", help="Update", use_container_width=True):
                                    # Validation
                                    if not new_source or new_source.strip() == "":
                                        st.error("Source cannot be empty")
                                    elif new_amount <= 0:
                                        st.error("Amount must be greater than 0")
                                    else:
                                        # Update in database
                                        if db.update_income(income_id, user_id, new_date.strftime(config.DATE_FORMAT), new_source, new_amount):
                                            st.session_state[edit_key] = False
                                            st.cache_resource.clear()
                                            st.rerun()
                                        else:
                                            st.error("Failed to update income")
                            with btn_cols[2]:
                                st.button("🗑️", key=f"delete_income_btn_{income_id}", disabled=True, help="Delete", use_container_width=True)
                    else:
                        # View mode: show text
                        cols[0].write(row['date'])
                        cols[1].write(row['source'])
                        cols[2].write(f"{config.CURRENCY_SYMBOL}{float(row['amount']):,.2f}")
                        
                        with cols[3]:
                            btn_cols = st.columns(3)
                            with btn_cols[0]:
                                if st.button("✏️", key=f"edit_income_btn_{income_id}", help="Edit", use_container_width=True):
                                    st.session_state[edit_key] = True
                                    st.rerun()
                            with btn_cols[1]:
                                st.button("💾", key=f"update_income_{income_id}", disabled=True, help="Update", use_container_width=True)
                            with btn_cols[2]:
                                delete_key = f'confirm_delete_income_{income_id}'
                                if st.button("🗑️", key=f"delete_income_btn_{income_id}", help="Delete", use_container_width=True):
                                    st.session_state[delete_key] = True
                                    st.rerun()
                                
                                # Confirmation dialog
                                if st.session_state.get(delete_key, False):
                                    st.warning(f"Delete this income entry?")
                                    conf_cols = st.columns(2)
                                    with conf_cols[0]:
                                        if st.button("Yes", key=f"yes_del_income_{income_id}"):
                                            if db.delete_income(income_id, user_id):
                                                st.session_state.pop(delete_key, None)
                                                st.cache_resource.clear()
                                                st.rerun()
                                            else:
                                                st.error("Failed to delete")
                                    with conf_cols[1]:
                                        if st.button("No", key=f"no_del_income_{income_id}"):
                                            st.session_state.pop(delete_key, None)
                                            st.rerun()
                    
                    st.divider()
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
            
            allocations_df = db.get_allocations_with_ids(user_id)
            if not allocations_df.empty:
                # Header row
                header_cols = st.columns([2, 2, 2, 2, 1.5])
                header_cols[0].markdown("**Category**")
                header_cols[1].markdown("**Allocated**")
                header_cols[2].markdown("**Spent**")
                header_cols[3].markdown("**Balance**")
                header_cols[4].markdown("**Actions**")
                
                st.divider()
                
                # Render each row
                for idx, row in allocations_df.iterrows():
                    alloc_id = int(row['id'])
                    edit_key = f'edit_alloc_{alloc_id}'
                    is_editing = st.session_state.get(edit_key, False)
                    
                    cols = st.columns([2, 2, 2, 2, 1.5])
                    
                    if is_editing:
                        # Edit mode: show input fields
                        with cols[0]:
                            new_category = st.text_input("", value=row['category'], key=f"cat_{alloc_id}", label_visibility="collapsed")
                        with cols[1]:
                            new_allocated = st.number_input("", value=float(row['allocated_amount']), min_value=0.0, step=100.0, key=f"alloc_{alloc_id}", label_visibility="collapsed")
                        with cols[2]:
                            # Spent amount is read-only (calculated from expenses)
                            cols[2].write(f"{config.CURRENCY_SYMBOL}{float(row['spent_amount']):,.2f}")
                        with cols[3]:
                            # Balance is calculated
                            new_balance = new_allocated - float(row['spent_amount'])
                            cols[3].write(f"{config.CURRENCY_SYMBOL}{new_balance:,.2f}")
                        
                        with cols[4]:
                            btn_cols = st.columns(3)
                            with btn_cols[0]:
                                st.button("✏️", key=f"edit_alloc_btn_{alloc_id}", disabled=True, help="Edit", use_container_width=True)
                            with btn_cols[1]:
                                if st.button("💾", key=f"update_alloc_{alloc_id}", help="Update", use_container_width=True):
                                    # Validation
                                    if not new_category or new_category.strip() == "":
                                        st.error("Category cannot be empty")
                                    elif new_allocated <= 0:
                                        st.error("Allocated amount must be greater than 0")
                                    else:
                                        # Update in database
                                        if db.update_allocation(alloc_id, user_id, new_category, new_allocated):
                                            st.session_state[edit_key] = False
                                            st.cache_resource.clear()
                                            st.rerun()
                                        else:
                                            st.error("Failed to update allocation")
                            with btn_cols[2]:
                                st.button("🗑️", key=f"delete_alloc_btn_{alloc_id}", disabled=True, help="Delete", use_container_width=True)
                    else:
                        # View mode: show text
                        cols[0].write(row['category'])
                        cols[1].write(f"{config.CURRENCY_SYMBOL}{float(row['allocated_amount']):,.2f}")
                        cols[2].write(f"{config.CURRENCY_SYMBOL}{float(row['spent_amount']):,.2f}")
                        cols[3].write(f"{config.CURRENCY_SYMBOL}{float(row['balance']):,.2f}")
                        
                        with cols[4]:
                            btn_cols = st.columns(3)
                            with btn_cols[0]:
                                if st.button("✏️", key=f"edit_alloc_btn_{alloc_id}", help="Edit", use_container_width=True):
                                    st.session_state[edit_key] = True
                                    st.rerun()
                            with btn_cols[1]:
                                st.button("💾", key=f"update_alloc_{alloc_id}", disabled=True, help="Update", use_container_width=True)
                            with btn_cols[2]:
                                delete_key = f'confirm_delete_alloc_{alloc_id}'
                                if st.button("🗑️", key=f"delete_alloc_btn_{alloc_id}", help="Delete", use_container_width=True):
                                    st.session_state[delete_key] = True
                                    st.rerun()
                                
                                # Confirmation dialog
                                if st.session_state.get(delete_key, False):
                                    st.warning(f"Delete allocation '{row['category']}'?")
                                    conf_cols = st.columns(2)
                                    with conf_cols[0]:
                                        if st.button("Yes", key=f"yes_del_alloc_{alloc_id}"):
                                            if db.delete_allocation_by_id(alloc_id, user_id):
                                                st.session_state.pop(delete_key, None)
                                                st.cache_resource.clear()
                                                st.rerun()
                                            else:
                                                st.error("Failed to delete")
                                    with conf_cols[1]:
                                        if st.button("No", key=f"no_del_alloc_{alloc_id}"):
                                            st.session_state.pop(delete_key, None)
                                            st.rerun()
                    
                    st.divider()
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
            
            expenses_df = db.get_expenses_with_ids(user_id)
            if not expenses_df.empty:
                total_exp = expenses_df["amount"].sum()
                st.metric("💸 Total Expenses", f"{config.CURRENCY_SYMBOL}{total_exp:,.2f}")
                
                # Header row
                header_cols = st.columns([1.5, 2, 1.5, 3, 1.5])
                header_cols[0].markdown("**Date**")
                header_cols[1].markdown("**Category**")
                header_cols[2].markdown("**Amount**")
                header_cols[3].markdown("**Comment**")
                header_cols[4].markdown("**Actions**")
                
                st.divider()
                
                # Render each row (show first 20 for performance)
                for idx, row in expenses_df.head(20).iterrows():
                    expense_id = int(row['id'])
                    edit_key = f'edit_expense_{expense_id}'
                    is_editing = st.session_state.get(edit_key, False)
                    
                    cols = st.columns([1.5, 2, 1.5, 3, 1.5])
                    
                    if is_editing:
                        # Edit mode: show input fields
                        with cols[0]:
                            new_date = st.date_input("", value=pd.to_datetime(row['date']).date(), key=f"exp_date_{expense_id}", label_visibility="collapsed")
                        with cols[1]:
                            # Category must be from available categories
                            cat_options = categories if categories else [row['category']]
                            cat_index = cat_options.index(row['category']) if row['category'] in cat_options else 0
                            new_category = st.selectbox("", options=cat_options, index=cat_index, key=f"exp_cat_{expense_id}", label_visibility="collapsed")
                        with cols[2]:
                            new_amount = st.number_input("", value=float(row['amount']), min_value=0.0, step=10.0, key=f"exp_amt_{expense_id}", label_visibility="collapsed")
                        with cols[3]:
                            new_comment = st.text_input("", value=row['comment'], key=f"exp_cmt_{expense_id}", label_visibility="collapsed")
                        
                        with cols[4]:
                            btn_cols = st.columns(3)
                            with btn_cols[0]:
                                st.button("✏️", key=f"edit_exp_btn_{expense_id}", disabled=True, help="Edit", use_container_width=True)
                            with btn_cols[1]:
                                if st.button("💾", key=f"update_exp_{expense_id}", help="Update", use_container_width=True):
                                    # Validation
                                    if not new_comment or new_comment.strip() == "":
                                        st.error("Comment cannot be empty")
                                    elif new_amount <= 0:
                                        st.error("Amount must be greater than 0")
                                    elif new_category not in categories:
                                        st.error("Invalid category selected")
                                    else:
                                        # Update in database - need old values for allocation adjustment
                                        old_category = row['category']
                                        old_amount = float(row['amount'])
                                        if db.update_expense(expense_id, user_id, new_date.strftime(config.DATE_FORMAT), 
                                                           new_category, new_amount, old_category, old_amount, new_comment):
                                            st.session_state[edit_key] = False
                                            st.cache_resource.clear()
                                            st.rerun()
                                        else:
                                            st.error("Failed to update expense")
                            with btn_cols[2]:
                                st.button("🗑️", key=f"delete_exp_btn_{expense_id}", disabled=True, help="Delete", use_container_width=True)
                    else:
                        # View mode: show text
                        cols[0].write(row['date'])
                        cols[1].write(row['category'])
                        cols[2].write(f"{config.CURRENCY_SYMBOL}{float(row['amount']):,.2f}")
                        cols[3].write(row['comment'])
                        
                        with cols[4]:
                            btn_cols = st.columns(3)
                            with btn_cols[0]:
                                if st.button("✏️", key=f"edit_exp_btn_{expense_id}", help="Edit", use_container_width=True):
                                    st.session_state[edit_key] = True
                                    st.rerun()
                            with btn_cols[1]:
                                st.button("💾", key=f"update_exp_{expense_id}", disabled=True, help="Update", use_container_width=True)
                            with btn_cols[2]:
                                delete_key = f'confirm_delete_expense_{expense_id}'
                                if st.button("🗑️", key=f"delete_exp_btn_{expense_id}", help="Delete", use_container_width=True):
                                    st.session_state[delete_key] = True
                                    st.rerun()
                                
                                # Confirmation dialog
                                if st.session_state.get(delete_key, False):
                                    st.warning(f"Delete this expense?")
                                    conf_cols = st.columns(2)
                                    with conf_cols[0]:
                                        if st.button("Yes", key=f"yes_del_exp_{expense_id}"):
                                            # Need category and amount for allocation adjustment
                                            if db.delete_expense(expense_id, user_id, row['category'], float(row['amount'])):
                                                st.session_state.pop(delete_key, None)
                                                st.cache_resource.clear()
                                                st.rerun()
                                            else:
                                                st.error("Failed to delete")
                                    with conf_cols[1]:
                                        if st.button("No", key=f"no_del_exp_{expense_id}"):
                                            st.session_state.pop(delete_key, None)
                                            st.rerun()
                    
                    st.divider()
                
                if len(expenses_df) > 20:
                    st.caption(f"Showing 20 of {len(expenses_df)} expenses")
            else:
                st.markdown("**No expenses recorded yet**")


# ==================== SUPER ADMIN DASHBOARD ====================


def show_super_admin_dashboard():
    """Super admin dashboard for managing multiple households"""
    user = st.session_state.user
    
    # Header with logout
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("🔱 Super Admin Dashboard")
        st.caption(f"Welcome, {user['full_name']}")
    with col2:
        st.write("")  # Spacer for alignment
        if st.button("Logout", key="super_logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()
    
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
            
            with st.form("create_household_form"):
                household_name = st.text_input("Family/Household Name", placeholder="e.g., Smith Family")
                admin_name = st.text_input("Family Admin Name")
                admin_email = st.text_input("Family Admin Email")
                admin_password = st.text_input("Admin Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                
                create_btn = st.form_submit_button("Create Family", use_container_width=True)
                
                if create_btn:
                    if not all([household_name, admin_name, admin_email, admin_password]):
                        st.error("Please fill all fields")
                    elif admin_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(admin_password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        success, household_id, message = db.create_household_with_admin(
                            household_name, admin_email, admin_name, admin_password
                        )
                        if success:
                            st.success(f"✅ {message}")
                            st.info(f"📧 Family admin can now login with:\nEmail: {admin_email}\nPassword: {admin_password}")
                            st.cache_data.clear()
                            st.rerun()
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
    
    # TAB 3: Manage Members
    with tab3:
        st.header("Member Management Across Families")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("➕ Add Member to Family")
            
            # Get list of families for dropdown
            households_df = db.get_all_households()
            if not households_df.empty:
                with st.form("add_member_super_form"):
                    household_options = {row['name']: row['id'] for _, row in households_df.iterrows()}
                    selected_family = st.selectbox("Select Family", options=list(household_options.keys()))
                    
                    member_name = st.text_input("Member Name")
                    member_email = st.text_input("Member Email")
                    member_relationship = st.selectbox("Relationship", 
                        ["Spouse", "Parent", "Child", "Sibling", "Other"])
                    
                    add_member_btn = st.form_submit_button("Add Member", use_container_width=True)
                    
                    if add_member_btn:
                        if not all([selected_family, member_name, member_email]):
                            st.error("Please fill all fields")
                        else:
                            household_id = household_options[selected_family]
                            success, member_id, invite_token = db.add_member_to_family_super_admin(
                                household_id, member_email, member_name, member_relationship
                            )
                            if success:
                                st.success(f"✅ Member added to {selected_family}")
                                st.info(f"📧 Invite Token:\n`{invite_token}`")
                                st.caption("Share this token with the member")
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error(f"❌ {invite_token}")
            else:
                st.info("Create families first before adding members")
        
        with col2:
            st.subheader("👤 Members by Family")
            
            users_df = db.get_all_users_super_admin()
            
            if not users_df.empty:
                # Group by family
                families = users_df['household_name'].unique()
                
                for family in families:
                    if pd.isna(family):
                        continue
                        
                    st.markdown(f"### {family}")
                    family_users = users_df[users_df['household_name'] == family]
                    
                    for _, user in family_users.iterrows():
                        with st.container():
                            col_info, col_action = st.columns([3, 1])
                            
                            with col_info:
                                role_icon = "👑" if user['role'] == 'admin' else "👤"
                                # Handle both PostgreSQL (True/False) and SQLite (1/0)
                                status_icon = "✅" if user['is_active'] else "❌"
                                st.markdown(f"""
                                {role_icon} **{user['full_name']}** {status_icon}  
                                📧 {user['email']} | Role: {user['role'].title()}
                                """)
                            
                            with col_action:
                                # Only show promote button for members
                                if user['role'] == 'member':
                                    if st.button("👑 Make Admin", key=f"promote_{user['id']}", help="Promote to family admin"):
                                        # Get household_id from household_name
                                        household_row = households_df[households_df['name'] == family]
                                        if not household_row.empty:
                                            household_id = household_row.iloc[0]['id']
                                            success, msg = db.promote_member_to_admin(user['id'], household_id)
                                            if success:
                                                st.success(msg)
                                                st.cache_data.clear()
                                                st.rerun()
                                            else:
                                                st.error(msg)
                        
                        st.divider()
            else:
                st.info("No users found")
    
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
        
        if user['role'] == 'superadmin':
            show_super_admin_dashboard()
        elif user['role'] == 'admin':
            show_admin_dashboard()
        else:
            show_member_dashboard()

if __name__ == "__main__":
    main()
