# Helper Functions for Advanced Filtering

def get_user_available_periods(db, user_ids):
    """
    Get available year/month combinations for selected user(s).
    Returns dict with available years and months with data.
    
    Args:
        db: Database instance
        user_ids: List of user IDs to check
        
    Returns:
        dict: {
            'years': set of years with data,
            'months_by_year': dict {year: set of months},
            'all_periods': set of (year, month) tuples
        }
    """
    if not user_ids:
        return {'years': set(), 'months_by_year': {}, 'all_periods': set()}
    
    all_periods = set()
    
    # Check each user
    for user_id in user_ids:
        # Get allocations (have year/month columns)
        try:
            cursor = db.conn.cursor()
            db._execute(cursor, 
                'SELECT DISTINCT year, month FROM allocations WHERE user_id = ?',
                (user_id,)
            )
            alloc_periods = cursor.fetchall()
            for row in alloc_periods:
                all_periods.add((int(row['year']), int(row['month'])))
        except:
            pass
        
        # Get income (parse date)
        try:
            income_df = db.get_income_with_ids(user_id)
            if not income_df.empty:
                income_df['date_parsed'] = pd.to_datetime(income_df['date'])
                for _, row in income_df.iterrows():
                    year = row['date_parsed'].year
                    month = row['date_parsed'].month
                    all_periods.add((year, month))
        except:
            pass
        
        # Get expenses (parse date)
        try:
            expense_df = db.get_expenses_with_ids(user_id)
            if not expense_df.empty:
                expense_df['date_parsed'] = pd.to_datetime(expense_df['date'])
                for _, row in expense_df.iterrows():
                    year = row['date_parsed'].year
                    month = row['date_parsed'].month
                    all_periods.add((year, month))
        except:
            pass
    
    # Process periods into usable structure
    years = set()
    months_by_year = {}
    
    for year, month in all_periods:
        years.add(year)
        if year not in months_by_year:
            months_by_year[year] = set()
        months_by_year[year].add(month)
    
    return {
        'years': years,
        'months_by_year': months_by_year,
        'all_periods': all_periods
    }


def format_period_options(years, available_years, months, available_months):
    """
    Format year/month options with (No Data) suffix for unavailable periods.
    
    Args:
        years: List of all years to show
        available_years: Set of years with data
        months: List of all months (1-12)
        available_months: Set of months with data
        
    Returns:
        tuple: (formatted_year_options, formatted_month_options)
    """
    import calendar
    
    year_options = []
    for year in years:
        if year in available_years:
            year_options.append(str(year))
        else:
            year_options.append(f"{year} (No Data)")
    
    month_options = []
    for month in months:
        month_name = calendar.month_name[month]
        if month in available_months:
            month_options.append(month_name)
        else:
            month_options.append(f"{month_name} (No Data)")
    
    return year_options, month_options


def parse_selected_options(selected_items):
    """
    Parse selected options, removing (No Data) suffix and converting to int where needed.
    
    Args:
        selected_items: List of selected option strings
        
    Returns:
        list: Cleaned values
    """
    cleaned = []
    for item in selected_items:
        # Remove (No Data) suffix if present
        cleaned_item = item.replace(' (No Data)', '').strip()
        cleaned.append(cleaned_item)
    return cleaned


