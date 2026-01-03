"""
Personal Expense Tracker - Offline First with Advanced Features
A Streamlit application for tracking income, allocations, and expenses in INR (₹)
Works completely offline with local SQLite database
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from database import LocalDB
import config
import calendar

# Page configuration
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better mobile experience
st.markdown("""
<style>
    /* Mobile-friendly adjustments */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Better table display */
    .dataframe {
        font-size: 14px;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 24px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
    }
    
    /* Offline indicator */
    .offline-badge {
        background-color: #28a745;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        display: inline-block;
    }
    
    /* Month buttons */
    .month-button {
        background-color: #f0f2f6;
        padding: 10px 15px;
        margin: 5px;
        border-radius: 8px;
        display: inline-block;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .month-button:hover {
        background-color: #e0e2e6;
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

# Initialize database connection
@st.cache_resource
def get_database():
    """Get cached database connection"""
    return LocalDB()

try:
    db = get_database()
except Exception as e:
    st.error("⚠️ Failed to connect to local database.")
    st.error(f"Error: {str(e)}")
    st.stop()

# Helper function to get month name
def get_month_name(month_num):
    return calendar.month_name[month_num]

# Header
st.title("💰 Personal Expense Tracker")
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"Track your finances in **{config.CURRENCY_SYMBOL} INR**")
with col2:
    st.markdown('<div class="offline-badge">✅ Offline Ready</div>', unsafe_allow_html=True)

# Create tabs for different sections
tab_overall, tab1, tab2, tab3, tab4 = st.tabs(["📈 Overall Dashboard", "📊 Dashboard", "💵 Income", "🎯 Allocations", "💸 Expenses"])

# ==================== OVERALL DASHBOARD TAB ====================
with tab_overall:
    st.header("📈 Overall Dashboard - Year/Month Analysis")
    
    # Year selector
    years = db.get_years_with_data()
    selected_year = st.selectbox("Select Year", years, key="year_selector")
    
    # Get yearly data
    yearly_income = db.get_income_for_period(selected_year)
    yearly_expenses = db.get_expenses_for_period(selected_year)
    yearly_savings = yearly_income - yearly_expenses
    
    # Display yearly metrics
    st.subheader(f"📅 Year {selected_year} Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Total Income", f"{config.CURRENCY_SYMBOL}{yearly_income:,.2f}")
    with col2:
        st.metric("💸 Total Expenses", f"{config.CURRENCY_SYMBOL}{yearly_expenses:,.2f}")
    with col3:
        delta_color = "normal" if yearly_savings >= 0 else "inverse"
        st.metric("💵 Yearly Savings", f"{config.CURRENCY_SYMBOL}{yearly_savings:,.2f}", 
                 delta=f"{(yearly_savings/yearly_income*100) if yearly_income > 0 else 0:.1f}%")
    
    st.divider()
    
    # Monthly breakdown
    st.subheader("📊 Monthly Breakdown")
    monthly_summary = db.get_all_settled_data(selected_year)
    

    if not monthly_summary.empty:
        # Create month columns for better visualization
        month_nums = monthly_summary['month'].tolist()
        
        # Display months with data
        st.write("**Months with Data:**")
        month_cols = st.columns(len(month_nums) if len(month_nums) <= 6 else 6)
        
        for idx, month_num in enumerate(month_nums):
            col_idx = idx % 6
            with month_cols[col_idx]:
                month_data = monthly_summary[monthly_summary['month'] == month_num].iloc[0]
                month_income = month_data['income']
                month_expenses = month_data['expenses']
                month_savings = month_data['savings']
                
                with st.expander(f"📅 {get_month_name(month_num)}", expanded=False):
                    st.metric("Income", f"{config.CURRENCY_SYMBOL}{month_income:,.2f}")
                    st.metric("Expenses", f"{config.CURRENCY_SYMBOL}{month_expenses:,.2f}")
                    st.metric("Savings", f"{config.CURRENCY_SYMBOL}{month_savings:,.2f}")
        
        st.divider()
        
        # Monthly savings chart
        st.subheader("💹 Monthly Savings Trend")
        monthly_summary['month_name'] = monthly_summary['month'].apply(lambda x: get_month_name(x))
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Income",
            x=monthly_summary['month_name'],
            y=monthly_summary['income'],
            marker_color='lightgreen'
        ))
        fig.add_trace(go.Bar(
            name="Expenses",
            x=monthly_summary['month_name'],
            y=monthly_summary['expenses'],
            marker_color='lightcoral'
        ))
        fig.add_trace(go.Scatter(
            name="Savings",
            x=monthly_summary['month_name'],
            y=monthly_summary['savings'],
            mode='lines+markers',
            line=dict(color='blue', width=3),
            marker=dict(size=10)
        ))
        fig.update_layout(
            barmode='group',
            height=400,
            xaxis_title="Month",
            yaxis_title=f"Amount ({config.CURRENCY_SYMBOL})",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Monthly summary table
        st.subheader("📋 Monthly Summary Table")
        display_summary = monthly_summary[['month_name', 'income', 'expenses', 'savings']].copy()
        display_summary.columns = ['Month', 'Income', 'Expenses', 'Savings']
        display_summary['Income'] = display_summary['Income'].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
        display_summary['Expenses'] = display_summary['Expenses'].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
        display_summary['Savings'] = display_summary['Savings'].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
        st.dataframe(display_summary, use_container_width=True, hide_index=True)
    else:
        st.info(f"No expense data found for {selected_year}. Start logging expenses!")

# ==================== DASHBOARD TAB ====================
with tab1:
    st.header("📊 Financial Dashboard")
    
    # Buttons row
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
    
    with col_btn1:
        if st.button("🔄 Refresh Data", key="refresh_dashboard", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()
    
    with col_btn2:
        if st.button("📅 Settle Month", key="settle_month_btn", type="primary", use_container_width=True):
            st.session_state.show_settle_confirm = True
    
    # Settle confirmation dialog
    if st.session_state.get('show_settle_confirm', False):
        with st.container():
            st.warning("⚠️ **Warning: Settle Current Month**")
            st.markdown("""
            **This action will:**
            - Archive current month's income and expenses to Overall Dashboard
            - **Clear ALL allocation categories** and their spent amounts
            - **Clear ALL expense entries**
            - Retain income entries for historical tracking
            
            **This action cannot be undone!**
            
            Are you sure you want to settle the current month?
            """)
            
            col_yes, col_no, col_spacer = st.columns([1, 1, 3])
            with col_yes:
                if st.button("✅ Yes, Settle", key="confirm_settle", type="primary", use_container_width=True):
                    # Get current month and year
                    current_date = datetime.now()
                    current_year = current_date.year
                    current_month = current_date.month
                    
                    # Settle the month
                    success, message = db.settle_current_month(current_year, current_month)
                    
                    if success:
                        st.success(message)
                        st.info("🎉 Your data has been archived! Dashboard will refresh now.")
                        st.session_state.show_settle_confirm = False
                        st.cache_resource.clear()
                        # Wait a moment to show the success message
                        import time
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(message)
                        st.session_state.show_settle_confirm = False
            
            with col_no:
                if st.button("❌ Cancel", key="cancel_settle", use_container_width=True):
                    st.session_state.show_settle_confirm = False
                    st.rerun()
    

    # Get data
    total_income = db.get_total_income()
    allocations_df = db.get_all_allocations()
    total_expenses = db.get_total_expenses()
    
    # Calculate metrics
    total_allocated = allocations_df["Allocated Amount"].sum() if not allocations_df.empty else 0
    total_spent = allocations_df["Spent Amount"].sum() if not allocations_df.empty else 0
    total_balance = allocations_df["Balance"].sum() if not allocations_df.empty else 0
    remaining_liquidity = total_income - total_allocated
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Total Income", f"{config.CURRENCY_SYMBOL}{total_income:,.2f}")
    with col2:
        st.metric("🎯 Total Allocated", f"{config.CURRENCY_SYMBOL}{total_allocated:,.2f}")
    with col3:
        st.metric("💸 Total Spent", f"{config.CURRENCY_SYMBOL}{total_spent:,.2f}")
    with col4:
        st.metric("💵 Remaining Liquidity", f"{config.CURRENCY_SYMBOL}{remaining_liquidity:,.2f}")
    
    st.divider()
    
    # Charts section
    if not allocations_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Allocation Breakdown")
            fig_pie = px.pie(
                allocations_df,
                values="Allocated Amount",
                names="Category",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.subheader("Spent vs. Allocated")
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
            fig_bar.update_layout(
                barmode='group',
                height=400,
                xaxis_title="Category",
                yaxis_title=f"Amount ({config.CURRENCY_SYMBOL})"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("📝 No allocations yet. Add some in the Allocations tab!")
    
    st.divider()
    
    # Allocation status table
    st.subheader("📋 Allocation Status")
    if not allocations_df.empty:
        display_df = allocations_df.copy()
        display_df["Allocated Amount"] = display_df["Allocated Amount"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
        display_df["Spent Amount"] = display_df["Spent Amount"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
        display_df["Balance"] = display_df["Balance"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No allocation data available.")
    
    st.divider()
    
    # Recent expenses
    st.subheader("📝 Recent Expenses")
    expenses_df = db.get_all_expenses()
    if not expenses_df.empty:
        recent_expenses = expenses_df.head(10)
        recent_expenses_display = recent_expenses.copy()
        recent_expenses_display["Amount"] = recent_expenses_display["Amount"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
        st.dataframe(recent_expenses_display, use_container_width=True, hide_index=True)
    else:
        st.info("No expenses recorded yet.")

# ==================== INCOME TAB ====================
with tab2:
    st.header("💵 Income Management")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Add New Income")
        with st.form("income_form", clear_on_submit=True):
            income_date = st.date_input(
                "Date",
                value=date.today(),
                format="YYYY-MM-DD"
            )
            income_source = st.text_input("Source", placeholder="e.g., Salary, Freelance")
            income_amount = st.number_input(
                f"Amount ({config.CURRENCY_SYMBOL})",
                min_value=0.0,
                step=100.0,
                format="%.2f"
            )
            
            submit_income = st.form_submit_button("➕ Add Income", use_container_width=True)
            
            if submit_income:
                if income_source and income_amount > 0:
                    if db.add_income(
                        income_date.strftime(config.DATE_FORMAT),
                        income_source,
                        income_amount
                    ):
                        st.success(f"✅ Added {config.CURRENCY_SYMBOL}{income_amount:,.2f} from {income_source}")
                        st.cache_resource.clear()
                        st.rerun()
                else:
                    st.error("Please fill all fields correctly")
    
    with col2:
        st.subheader("Income History")
        
        # Display total liquidity prominently
        total_income = db.get_total_income()
        st.metric("💰 Total Liquidity", f"{config.CURRENCY_SYMBOL}{total_income:,.2f}")
        
        # Income table with edit option
        income_df_with_ids = db.get_income_with_ids()
        if not income_df_with_ids.empty:
            # Edit income section
            with st.expander("✏️ Edit/Delete Income Entry"):
                edit_income_id = st.selectbox(
                    "Select entry to edit",
                    options=income_df_with_ids['id'].tolist(),
                    format_func=lambda x: f"{income_df_with_ids[income_df_with_ids['id']==x]['date'].values[0]} - {income_df_with_ids[income_df_with_ids['id']==x]['source'].values[0]} - ₹{income_df_with_ids[income_df_with_ids['id']==x]['amount'].values[0]:,.2f}",
                    key="edit_income_select"
                )
                
                if edit_income_id:
                    selected_income = income_df_with_ids[income_df_with_ids['id'] == edit_income_id].iloc[0]
                    
                    col_edit1, col_edit2 = st.columns(2)
                    with col_edit1:
                        edit_date = st.date_input("Date", value=pd.to_datetime(selected_income['date']), key="edit_income_date")
                        edit_source = st.text_input("Source", value=selected_income['source'], key="edit_income_source")
                    with col_edit2:
                        edit_amount = st.number_input("Amount", value=float(selected_income['amount']), min_value=0.0, step=100.0, key="edit_income_amount")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("💾 Update", key="update_income_btn", use_container_width=True):
                            if db.update_income(edit_income_id, edit_date.strftime(config.DATE_FORMAT), edit_source, edit_amount):
                                st.success("✅ Income updated!")
                                st.cache_resource.clear()
                                st.rerun()
                    with col_btn2:
                        if st.button("🗑️ Delete", key="delete_income_btn", type="secondary", use_container_width=True):
                            if db.delete_income(0):  # This will be fixed
                                st.success("✅ Income deleted!")
                                st.cache_resource.clear()
                                st.rerun()
            
            # Display income table
            income_display = income_df_with_ids[['date', 'source', 'amount']].copy()
            income_display.columns = ['Date', 'Source', 'Amount']
            income_display["Amount"] = income_display["Amount"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
            st.dataframe(income_display, use_container_width=True, hide_index=True)
        else:
            st.info("No income entries yet. Add your first income!")

# ==================== ALLOCATIONS TAB ====================
with tab3:
    st.header("🎯 Fixed Allocation System")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Manage Allocations")
        
        # Add new allocation
        with st.form("allocation_form", clear_on_submit=True):
            st.write("**Add New Category**")
            alloc_category = st.text_input("Category Name", placeholder="e.g., Stock, MF, House, Travel")
            alloc_amount = st.number_input(
                f"Allocated Amount ({config.CURRENCY_SYMBOL})",
                min_value=0.0,
                step=100.0,
                format="%.2f"
            )
            
            submit_alloc = st.form_submit_button("➕ Add Allocation", use_container_width=True)
            
            if submit_alloc:
                if alloc_category and alloc_amount > 0:
                    existing_categories = db.get_categories()
                    if alloc_category in existing_categories:
                        st.error(f"Category '{alloc_category}' already exists!")
                    else:
                        if db.add_allocation(alloc_category, alloc_amount):
                            st.success(f"✅ Created allocation: {alloc_category}")
                            st.cache_resource.clear()
                            st.rerun()
                else:
                    st.error("Please fill all fields correctly")
        
        st.divider()
        
        # Update existing allocation
        st.write("**Update Allocation Amount**")
        allocations_df = db.get_all_allocations()
        if not allocations_df.empty:
            update_category = st.selectbox(
                "Select Category",
                options=allocations_df["Category"].tolist(),
                key="update_category"
            )
            
            if update_category:
                current_amount = allocations_df[allocations_df["Category"] == update_category]["Allocated Amount"].values[0]
                st.info(f"Current: {config.CURRENCY_SYMBOL}{current_amount:,.2f}")
                
                new_amount = st.number_input(
                    f"New Amount ({config.CURRENCY_SYMBOL})",
                    min_value=0.0,
                    value=float(current_amount),
                    step=100.0,
                    format="%.2f",
                    key="new_alloc_amount"
                )
                
                if st.button("💾 Update Amount", use_container_width=True):
                    if db.update_allocation_amount(update_category, new_amount):
                        st.success(f"✅ Updated {update_category} allocation")
                        st.cache_resource.clear()
                        st.rerun()
        else:
            st.info("No allocations to update")
    
    with col2:
        st.subheader("Current Allocations")
        
        allocations_df = db.get_all_allocations()
        if not allocations_df.empty:
            # Display summary
            total_allocated = allocations_df["Allocated Amount"].sum()
            total_spent = allocations_df["Spent Amount"].sum()
            total_balance = allocations_df["Balance"].sum()
            
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            with metric_col1:
                st.metric("Total Allocated", f"{config.CURRENCY_SYMBOL}{total_allocated:,.2f}")
            with metric_col2:
                st.metric("Total Spent", f"{config.CURRENCY_SYMBOL}{total_spent:,.2f}")
            with metric_col3:
                st.metric("Total Balance", f"{config.CURRENCY_SYMBOL}{total_balance:,.2f}")
            
            # Display table with formatting
            display_df = allocations_df.copy()
            display_df["Allocated Amount"] = display_df["Allocated Amount"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
            display_df["Spent Amount"] = display_df["Spent Amount"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
            display_df["Balance"] = display_df["Balance"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Delete allocation
            st.divider()
            st.write("**⚠️ Delete Category**")
            delete_category = st.selectbox(
                "Select category to delete",
                options=allocations_df["Category"].tolist(),
                key="delete_category"
            )
            
            if st.button("🗑️ Delete Category", type="secondary"):
                if db.delete_allocation(delete_category):
                    st.success(f"✅ Deleted {delete_category}")
                    st.cache_resource.clear()
                    st.rerun()
        else:
            st.info("📝 No allocations yet. Create your first budget category!")

# ==================== EXPENSES TAB ====================
with tab4:
    st.header("💸 Daily Expense Logging")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Add New Expense")
        
        # Get categories for dropdown
        categories = db.get_categories()
        
        if not categories:
            st.warning("⚠️ Please create allocation categories first in the Allocations tab!")
        else:
            with st.form("expense_form", clear_on_submit=True):
                expense_date = st.date_input(
                    "Date",
                    value=date.today(),
                    format="YYYY-MM-DD"
                )
                expense_category = st.selectbox(
                    "Category",
                    options=categories,
                    help="Select from your allocation categories"
                )
                expense_amount = st.number_input(
                    f"Amount ({config.CURRENCY_SYMBOL})",
                    min_value=0.0,
                    step=10.0,
                    format="%.2f"
                )
                expense_comment = st.text_area(
                    "Comment/Reason",
                    placeholder="e.g., Petrol for trip, Groceries, etc.",
                    max_chars=200
                )
                
                submit_expense = st.form_submit_button("➕ Add Expense", use_container_width=True)
                
                if submit_expense:
                    if expense_category and expense_amount > 0 and expense_comment:
                        if db.add_expense(
                            expense_date.strftime(config.DATE_FORMAT),
                            expense_category,
                            expense_amount,
                            expense_comment
                        ):
                            st.success(f"✅ Added expense: {config.CURRENCY_SYMBOL}{expense_amount:,.2f} to {expense_category}")
                            st.info("📊 Allocation balance updated automatically!")
                            st.cache_resource.clear()
                            st.rerun()
                    else:
                        st.error("Please fill all fields correctly")
    
    with col2:
        st.subheader("Expense History & Filter")
        
        # Category filter
        categories_with_all = ["All"] + categories
        filter_category = st.selectbox(
            "Filter by Category",
            options=categories_with_all,
            key="filter_category"
        )
        
        # Get filtered expenses
        if filter_category == "All":
            filtered_expenses = db.get_all_expenses()
        else:
            filtered_expenses = db.get_expenses_by_category(filter_category)
        
        # Total for filtered view
        if not filtered_expenses.empty:
            filtered_total = filtered_expenses["Amount"].sum()
            st.metric(f"💸 Total {filter_category} Expenses", f"{config.CURRENCY_SYMBOL}{filtered_total:,.2f}")
            
            # Edit expense section
            expenses_with_ids = db.get_expenses_with_ids()
            if filter_category != "All":
                expenses_with_ids = expenses_with_ids[expenses_with_ids['category'] == filter_category]
            
            if not expenses_with_ids.empty:
                with st.expander("✏️ Edit/Delete Expense Entry"):
                    edit_expense_id = st.selectbox(
                        "Select entry to edit",
                        options=expenses_with_ids['id'].tolist(),
                        format_func=lambda x: f"{expenses_with_ids[expenses_with_ids['id']==x]['date'].values[0]} - {expenses_with_ids[expenses_with_ids['id']==x]['category'].values[0]} - ₹{expenses_with_ids[expenses_with_ids['id']==x]['amount'].values[0]:,.2f}",
                        key="edit_expense_select"
                    )
                    
                    if edit_expense_id:
                        selected_expense = expenses_with_ids[expenses_with_ids['id'] == edit_expense_id].iloc[0]
                        old_category = selected_expense['category']
                        old_amount = selected_expense['amount']
                        
                        col_edit1, col_edit2 = st.columns(2)
                        with col_edit1:
                            edit_exp_date = st.date_input("Date", value=pd.to_datetime(selected_expense['date']), key="edit_exp_date")
                            edit_exp_category = st.selectbox("Category", options=categories, index=categories.index(old_category), key="edit_exp_cat")
                        with col_edit2:
                            edit_exp_amount = st.number_input("Amount", value=float(old_amount), min_value=0.0, step=10.0, key="edit_exp_amt")
                        
                        edit_exp_comment = st.text_area("Comment", value=selected_expense['comment'], key="edit_exp_comment")
                        
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("💾 Update", key="update_expense_btn", use_container_width=True):
                                if db.update_expense(edit_expense_id, edit_exp_date.strftime(config.DATE_FORMAT), 
                                                    edit_exp_category, edit_exp_amount, edit_exp_comment,
                                                    old_category, old_amount):
                                    st.success("✅ Expense updated!")
                                    st.cache_resource.clear()
                                    st.rerun()
                        with col_btn2:
                            if st.button("🗑️ Delete", key="delete_expense_btn", type="secondary", use_container_width=True):
                                if db.delete_expense(edit_expense_id, old_category, old_amount):
                                    st.success("✅ Expense deleted!")
                                    st.cache_resource.clear()
                                    st.rerun()
            
            # Expense table
            expenses_display = filtered_expenses.copy()
            expenses_display["Amount"] = expenses_display["Amount"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
            st.dataframe(expenses_display, use_container_width=True, hide_index=True, height=300)
        else:
            st.info(f"No expenses recorded for {filter_category}.")
    
    st.divider()
    
    # Category-wise breakdown section (separate, cleaner layout)
    st.subheader("📊 Category-wise Expense Summary")
    
    all_expenses = db.get_all_expenses()
    if not all_expenses.empty:
        # Group by category
        category_summary = all_expenses.groupby("Category")["Amount"].agg(['sum', 'count']).reset_index()
        category_summary.columns = ['Category', 'Total Amount', 'Number of Expenses']
        category_summary = category_summary.sort_values("Total Amount", ascending=False)
        
        # Display as cards
        cols = st.columns(min(len(category_summary), 4))
        for idx, row in category_summary.iterrows():
            col_idx = idx % 4
            with cols[col_idx]:
                st.metric(
                    label=f"🏷️ {row['Category']}",
                    value=f"{config.CURRENCY_SYMBOL}{row['Total Amount']:,.2f}",
                    delta=f"{row['Number of Expenses']} expenses"
                )
        
        # Bar chart
        fig = px.bar(
            category_summary,
            x="Category",
            y="Total Amount",
            color="Total Amount",
            color_continuous_scale="Reds",
            labels={"Total Amount": f"Amount ({config.CURRENCY_SYMBOL})"},
            title="Total Spending by Category"
        )
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        with st.expander("📋 View Detailed Category Breakdown"):
            display_cat_summary = category_summary.copy()
            display_cat_summary['Total Amount'] = display_cat_summary['Total Amount'].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
            st.dataframe(display_cat_summary, use_container_width=True, hide_index=True)
    else:
        st.info("No expenses recorded yet. Add your first expense!")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; padding: 10px;'>
    <small>💾 Data stored locally in SQLite | Works completely offline!</small>
</div>
""", unsafe_allow_html=True)
