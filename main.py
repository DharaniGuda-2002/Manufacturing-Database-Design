"""
main.py
Main entry point for Inventory Management System
CSC540 Project - Deliverable 2
"""

import sys
from database import init_database, close_database

def print_header():
    """Print application header"""
    print("\n" + "="*60)
    print(" "*15 + "INVENTORY MANAGEMENT SYSTEM")
    print(" "*10 + "Prepared/Frozen Meals Manufacturer")
    print("="*60)

def main_menu():
    """Display main menu and handle role selection"""
    while True:
        print("\n" + "-"*60)
        print("SELECT ROLE:")
        print("-"*60)
        print("1. Manufacturer")
        print("2. Supplier")
        print("3. General Viewer")
        print("4. View Required Queries")
        print("5. Undo Recent Operations")
        print("6. Exit")
        print("-"*60)
        
        choice = input("Enter choice (1-6): ").strip()
        
        if choice == '1':
            from manufacturer_menu import manufacturer_menu
            manufacturer_menu()
        elif choice == '2':
            from supplier_menu import supplier_menu
            supplier_menu()
        elif choice == '3':
            from viewer_menu import viewer_menu
            viewer_menu()
        elif choice == '4':
            from query_menu import query_menu
            query_menu()
        elif choice == '5':
            from undo_menu import undo_menu
            undo_menu()
        elif choice == '6':
            print("\n✓ Thank you for using Inventory Management System!")
            return
        else:
            print("\n✗ Invalid choice. Please enter 1-6.")

def main():
    """Main application entry point"""
    print_header()
    
    # Initialize database connection
    if not init_database():
        print("✗ Failed to connect to database. Exiting...")
        sys.exit(1)
    
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n✓ Application terminated by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
    finally:
        close_database()

if __name__ == "__main__":
    main()
