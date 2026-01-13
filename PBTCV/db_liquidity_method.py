
    def get_monthly_liquidity_by_member(self, household_id, year, is_admin, user_id=None):
        """Get monthly liquidity (Income - Allocations) grouped by member"""
        try:
            cursor = self.conn.cursor()
            
            if is_admin:
                self._execute(cursor, '''
                    SELECT 
                        CAST(strftime('%m', i.date) as INTEGER) as month,
                        u.full_name as member,
                        COALESCE(SUM(CAST(i.amount as REAL)), 0) as total_income,
                        COALESCE((SELECT SUM(CAST(a.allocated_amount as REAL))
                             FROM allocations a WHERE a.user_id = u.id
                             AND a.year = ? AND a.month = CAST(strftime('%m', i.date) as INTEGER)), 0) as total_allocated
                    FROM income i JOIN users u ON i.user_id = u.id
                    WHERE u.household_id = ? AND CAST(strftime('%Y', i.date) as INTEGER) = ?
                    GROUP BY CAST(strftime('%m', i.date) as INTEGER), u.full_name, u.id
                    ORDER BY month, u.full_name
                ''', (year, household_id, year))
            else:
                self._execute(cursor, '''
                    SELECT 
                        CAST(strftime('%m', i.date) as INTEGER) as month,
                        COALESCE(SUM(CAST(i.amount as REAL)), 0) as total_income,
                        COALESCE((SELECT SUM(CAST(a.allocated_amount as REAL))
                             FROM allocations a WHERE a.user_id = ?
                             AND a.year = ? AND a.month = CAST(strftime('%m', i.date) as INTEGER)), 0) as total_allocated
                    FROM income i
                    WHERE user_id = ? AND CAST(strftime('%Y', i.date) as INTEGER) = ?
                    GROUP BY CAST(strftime('%m', i.date) as INTEGER)
                    ORDER BY month
                ''', (user_id, year, user_id, year))
            
            results = cursor.fetchall()
            data = []
            for row in results:
                if is_admin:
                    month = row['month'] if isinstance(row, dict) else row[0]
                    member = row['member'] if isinstance(row, dict) else row[1]
                    total_income = row['total_income'] if isinstance(row, dict) else row[2]
                    total_allocated = row['total_allocated'] if isinstance(row, dict) else row[3]
                    liquidity = total_income - total_allocated
                    data.append({'month': month, 'member': member, 'liquidity': liquidity})
                else:
                    month = row['month'] if isinstance(row, dict) else row[0]
                    total_income = row['total_income'] if isinstance(row, dict) else row[1]
                    total_allocated = row['total_allocated'] if isinstance(row, dict) else row[2]
                    liquidity = total_income - total_allocated
                    data.append({'month': month, 'liquidity': liquidity})
            
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error getting monthly liquidity: {str(e)}")
            return pd.DataFrame()
