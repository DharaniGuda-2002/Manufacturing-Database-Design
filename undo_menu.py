"""
undo_menu.py
Undo functionality for recent operations
CSC540 Project - Deliverable 2

CRITICAL: This feature is tested by the professor!
"""

from database import db
from datetime import datetime

def undo_menu():
    """Undo operations menu"""
    while True:
        print("\n" + "="*60)
        print(" "*18 + "UNDO OPERATIONS MENU")
        print("="*60)
        print("1. View Recent Operations")
        print("2. Undo Specific Operation")
        print("3. View All Transaction History")
        print("4. Back to Main Menu")
        print("-"*60)
        
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == '1':
            view_recent_operations()
        elif choice == '2':
            undo_operation()
        elif choice == '3':
            view_all_history()
        elif choice == '4':
            return
        else:
            print("\n✗ Invalid choice. Please enter 1-4.")

def view_recent_operations():
    """View recent 20 operations"""
    print("\n" + "="*60)
    print("RECENT OPERATIONS (Last 20)")
    print("="*60)
    
    operations = db.fetch_all("""
        SELECT 
            transaction_id,
            operation_type,
            table_name,
            record_id,
            user_name,
            transaction_date,
            is_undone
        FROM TransactionLog
        ORDER BY transaction_date DESC
        LIMIT 20
    """)
    
    if not operations:
        print("\n✗ No operations found in transaction log.")
        print("Perform some operations (create product, batch, etc.) first.")
        return
    
    print(f"\nShowing {len(operations)} most recent operations:\n")
    
    for op in operations:
        status = "❌ UNDONE" if op['is_undone'] else "✓ Active"
        date = op['transaction_date'].strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"ID: {op['transaction_id']} | {status}")
        print(f"  Type: {op['operation_type']}")
        print(f"  Table: {op['table_name']}")
        print(f"  Record: {op['record_id']}")
        print(f"  User: {op['user_name']}")
        print(f"  Date: {date}\n")
    
    print("="*60)
    print("TIP: Use 'Undo Specific Operation' to reverse any active operation")
    print("="*60)

def undo_operation():
    """Undo a specific operation"""
    print("\n" + "="*60)
    print("UNDO OPERATION")
    print("="*60)
    
    # Show recent undoable operations
    operations = db.fetch_all("""
        SELECT 
            transaction_id,
            operation_type,
            table_name,
            record_id,
            user_name,
            transaction_date
        FROM TransactionLog
        WHERE is_undone = FALSE
        ORDER BY transaction_date DESC
        LIMIT 10
    """)
    
    if not operations:
        print("\n✗ No operations available to undo.")
        print("All recent operations have already been undone.")
        return
    
    print(f"\nUndoable Operations (Last 10):\n")
    
    for op in operations:
        date = op['transaction_date'].strftime('%Y-%m-%d %H:%M:%S')
        print(f"ID: {op['transaction_id']}")
        print(f"  {op['operation_type']} on {op['table_name']}")
        print(f"  Record: {op['record_id']}")
        print(f"  Date: {date}\n")
    
    transaction_id = input("Enter Transaction ID to undo (or 'cancel'): ").strip()
    
    if transaction_id.lower() == 'cancel':
        print("\n✓ Undo cancelled.")
        return
    
    try:
        transaction_id = int(transaction_id)
    except ValueError:
        print("\n✗ Invalid transaction ID. Must be a number.")
        return
    
    # Verify transaction exists and is not already undone
    transaction = db.fetch_one("""
        SELECT transaction_id, operation_type, table_name, record_id, is_undone
        FROM TransactionLog
        WHERE transaction_id = %s
    """, (transaction_id,))
    
    if not transaction:
        print(f"\n✗ Transaction {transaction_id} not found.")
        return
    
    if transaction['is_undone']:
        print(f"\n✗ Transaction {transaction_id} has already been undone.")
        return
    
    print(f"\n⚠️  You are about to undo:")
    print(f"  Operation: {transaction['operation_type']}")
    print(f"  Table: {transaction['table_name']}")
    print(f"  Record: {transaction['record_id']}")
    
    confirm = input("\nAre you sure? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("\n✓ Undo cancelled.")
        return
    
    # Call the stored procedure to undo
    try:
        # Prepare parameters: transaction_id (IN), success (OUT), message (OUT)
        params = [transaction_id, 0, '']
        result = db.call_procedure('UndoLastOperation', params)
        
        success = result[1]
        message = result[2]
        
        if success:
            print(f"\n✓ {message}")
            print(f"  Transaction {transaction_id} has been undone successfully!")
            print(f"  The {transaction['operation_type']} on {transaction['table_name']} has been reversed.")
        else:
            print(f"\n✗ Undo failed: {message}")
            
    except Exception as e:
        print(f"\n✗ Error during undo operation: {e}")
        print("This may happen if:")
        print("  - Related records depend on this data")
        print("  - The stored procedure encountered an error")
        print("  - Database constraints prevent deletion")

def view_all_history():
    """View complete transaction history"""
    print("\n" + "="*60)
    print("COMPLETE TRANSACTION HISTORY")
    print("="*60)
    
    # Get filter options
    print("\nFilter Options:")
    print("1. All transactions")
    print("2. Only active (not undone)")
    print("3. Only undone")
    print("4. By operation type")
    
    filter_choice = input("\nEnter choice (1-4): ").strip()
    
    where_clause = ""
    params = None
    
    if filter_choice == '2':
        where_clause = "WHERE is_undone = FALSE"
    elif filter_choice == '3':
        where_clause = "WHERE is_undone = TRUE"
    elif filter_choice == '4':
        print("\nOperation Types:")
        types = db.fetch_all("SELECT DISTINCT operation_type FROM TransactionLog")
        for t in types:
            print(f"  - {t['operation_type']}")
        op_type = input("\nEnter operation type: ").strip()
        where_clause = "WHERE operation_type = %s"
        params = (op_type,)
    
    query = f"""
        SELECT 
            transaction_id,
            operation_type,
            table_name,
            record_id,
            user_name,
            transaction_date,
            is_undone
        FROM TransactionLog
        {where_clause}
        ORDER BY transaction_date DESC
    """
    
    operations = db.fetch_all(query, params)
    
    if not operations:
        print("\n✗ No transactions found matching your criteria.")
        return
    
    print(f"\n{'='*60}")
    print(f"Found {len(operations)} transaction(s)")
    print(f"{'='*60}\n")
    
    # Statistics
    active_count = sum(1 for op in operations if not op['is_undone'])
    undone_count = sum(1 for op in operations if op['is_undone'])
    
    print(f"Active: {active_count} | Undone: {undone_count}\n")
    print(f"{'='*60}\n")
    
    for i, op in enumerate(operations, 1):
        status = "❌ UNDONE" if op['is_undone'] else "✓ Active"
        date = op['transaction_date'].strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"{i}. ID: {op['transaction_id']} | {status}")
        print(f"   Type: {op['operation_type']}")
        print(f"   Table: {op['table_name']}")
        print(f"   Record: {op['record_id']}")
        print(f"   User: {op['user_name']}")
        print(f"   Date: {date}\n")
        
        # Pause every 10 records
        if i % 10 == 0 and i < len(operations):
            cont = input("Press Enter to continue or 'q' to quit: ").strip()
            if cont.lower() == 'q':
                break
    
    print("="*60)
    print(f"Displayed {min(i, len(operations))} of {len(operations)} total transactions")
    print("="*60)
