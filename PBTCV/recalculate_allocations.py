"""
Utility script to recalculate all allocation spent amounts based on actual expenses
This fixes any discrepancies from the old buggy logic that didn't filter by year/month
"""

from multi_user_database import MultiUserDB

def recalculate_all_allocations():
    """Recalculate spent amounts for all allocations based on actual expenses"""
    db = MultiUserDB()
    
    try:
        cursor = db.conn.cursor()
        
        # Get all allocations
        cursor.execute('SELECT id, user_id, category, year, month, allocated_amount FROM allocations')
        allocations = cursor.fetchall()
        
        print(f"Found {len(allocations)} allocations to recalculate")
        
        for allocation in allocations:
            alloc_id = allocation['id']
            user_id = allocation['user_id']
            category = allocation['category']
            year = allocation['year']
            month = allocation['month']
            allocated_amount = float(allocation['allocated_amount'])
            
            # Calculate actual spent amount from expenses for this category/year/month
            cursor.execute('''
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
            cursor.execute('''
                UPDATE allocations 
                SET spent_amount = ?, balance = ?
                WHERE id = ?
            ''', (actual_spent, new_balance, alloc_id))
            
            print(f"Updated allocation {alloc_id}: {category} {year}-{month:02d} - Spent: {actual_spent}, Balance: {new_balance}")
        
        db.conn.commit()
        print(f"\nSuccessfully recalculated {len(allocations)} allocations!")
        return True
        
    except Exception as e:
        print(f"Error recalculating allocations: {str(e)}")
        import traceback
        traceback.print_exc()
        db.conn.rollback()
        return False

if __name__ == "__main__":
    print("Starting allocation recalculation...")
    print("=" * 50)
    success = recalculate_all_allocations()
    print("=" * 50)
    if success:
        print("✅ Recalculation complete!")
    else:
        print("❌ Recalculation failed!")
