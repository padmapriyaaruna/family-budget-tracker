"""
Utility script to recalculate and fix allocation spent amounts.

This script recalculates the spent_amount and balance for all allocations
based on actual expenses in the database.

Usage:
    python fix_allocation_spent_amounts.py
"""

import os
import sys

# Import the database
from multi_user_database import MultiUserDB

def fix_allocation_spent_amounts():
    """Recalculate spent amounts for all allocations based on actual expenses"""
    
    print("🔧 Starting allocation spent amount fix...")
    
    # Get database instance
    db = MultiUserDB()
    
    try:
        cursor = db.conn.cursor()
        
        # Get all allocations
        db._execute(cursor, 'SELECT id, user_id, category, allocated_amount FROM allocations')
        allocations = cursor.fetchall()
        
        print(f"Found {len(allocations)} allocations to process")
        
        fixed_count = 0
        for alloc in allocations:
            alloc_id = alloc['id']
            user_id = alloc['user_id']
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
            
            print(f"  ✓ Fixed allocation '{category}' for user {user_id}: spent={total_spent:.2f}, balance={new_balance:.2f}")
            fixed_count += 1
        
        # Commit changes
        db.conn.commit()
        
        print(f"\n✅ Successfully fixed {fixed_count} allocations!")
        print("Please refresh your application to see the updated values.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.conn.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_allocation_spent_amounts()
