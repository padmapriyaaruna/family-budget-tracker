    def get_monthly_liquidity_by_member_simple(self, household_id, year, is_admin, user_id=None):
        """Get monthly liquidity - simplified version that works reliably"""
        try:
            cursor = self.conn.cursor()
            
            # Get income data
            if is_admin:
                self._execute(cursor, '''
                    SELECT u.full_name as member, u.id as user_id,
                           EXTRACT(MONTH FROM i.date::date)::integer as month,
                           SUM(i.amount::numeric) as total_income
                    FROM income i
                    JOIN users u ON i.user_id = u.id
                    WHERE u.household_id = %s
                      AND EXTRACT(YEAR FROM i.date::date)::integer = %s
                    GROUP BY u.full_name, u.id, EXTRACT(MONTH FROM i.date::date)::integer
                ''', (household_id, year))
            else:
                self._execute(cursor, '''
                    SELECT EXTRACT(MONTH FROM date::date)::integer as month,
                           SUM(amount::numeric) as total_income
                    FROM income
                    WHERE user_id = %s
                      AND EXTRACT(YEAR FROM date::date)::integer = %s
                    GROUP BY EXTRACT(MONTH FROM date::date)::integer
                ''', (user_id, year))
            
            income_rows = cursor.fetchall()
            
            # Get allocation data
            if is_admin:
                self._execute(cursor, '''
                    SELECT u.full_name as member, u.id as user_id, a.month,
                           SUM(a.allocated_amount::numeric) as total_allocated
                    FROM allocations a
                    JOIN users u ON a.user_id = u.id
                    WHERE u.household_id = %s AND a.year = %s
                    GROUP BY u.full_name, u.id, a.month
                ''', (household_id, year))
            else:
                self._execute(cursor, '''
                    SELECT month, SUM(allocated_amount::numeric) as total_allocated
                    FROM allocations
                    WHERE user_id = %s AND year = %s
                    GROUP BY month
                ''', (user_id, year))
            
            alloc_rows = cursor.fetchall()
            
            # Build data structure
            data = []
            
            if is_admin:
                # Create dict of {(member, month): income}
                income_dict = {}
                for row in income_rows:
                    member = row['member'] if isinstance(row, dict) else row[0]
                    month = row['month'] if isinstance(row, dict) else row[2]
                    income = row['total_income'] if isinstance(row, dict) else row[3]
                    income_dict[(member, month)] = float(income or 0)
                
                # Create dict of {(member, month): allocated}
                alloc_dict = {}
                for row in alloc_rows:
                    member = row['member'] if isinstance(row, dict) else row[0]
                    month = row['month'] if isinstance(row, dict) else row[2]
                    allocated = row['total_allocated'] if isinstance(row, dict) else row[3]
                    alloc_dict[(member, month)] = float(allocated or 0)
                
                # Combine to calculate liquidity
                all_keys = set(income_dict.keys()) | set(alloc_dict.keys())
                for (member, month) in all_keys:
                    income = income_dict.get((member, month), 0)
                    allocated = alloc_dict.get((member, month), 0)
                    liquidity = income - allocated
                    data.append({'month': month, 'member': member, 'liquidity': liquidity})
            else:
                # For members
                income_dict = {row['month'] if isinstance(row, dict) else row[0]: 
                             float((row['total_income'] if isinstance(row, dict) else row[1]) or 0) 
                             for row in income_rows}
                alloc_dict = {row['month'] if isinstance(row, dict) else row[0]: 
                            float((row['total_allocated'] if isinstance(row, dict) else row[1]) or 0) 
                            for row in alloc_rows}
                
                all_months = set(income_dict.keys()) | set(alloc_dict.keys())
                for month in all_months:
                    income = income_dict.get(month, 0)
                    allocated = alloc_dict.get(month, 0)
                    liquidity = income - allocated
                    data.append({'month': month, 'liquidity': liquidity})
            
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error in get_monthly_liquidity_by_member_simple: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
