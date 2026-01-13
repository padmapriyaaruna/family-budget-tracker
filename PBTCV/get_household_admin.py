    
    def get_household_admin(self, household_id):
        \"\"\"Get the admin user for a household\"\"\"
        try:
            cursor = self.conn.cursor()
            self._execute(cursor, '''
                SELECT id, full_name, email, role, household_id, relationship
                FROM users
                WHERE household_id = %s AND role = 'admin'
                LIMIT 1
            ''', (household_id,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'id': result['id'] if isinstance(result, dict) else result[0],
                    'full_name': result['full_name'] if isinstance(result, dict) else result[1],
                    'email': result['email'] if isinstance(result, dict) else result[2],
                    'role': result['role'] if isinstance(result, dict) else result[3],
                    'household_id': result['household_id'] if isinstance(result, dict) else result[4],
                    'relationship': result['relationship'] if isinstance(result, dict) else result[5]
                }
            return None
        except Exception as e:
            print(f\"Error getting household admin: {str(e)}\")
            return None
