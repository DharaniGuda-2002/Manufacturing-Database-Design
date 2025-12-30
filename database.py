"""
database.py
Database connection and utility functions
CSC540 Project - Deliverable 2
"""

import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager

class Database:
    """Database connection manager"""
    
    def __init__(self):
        self.connection = None
        self.host = 'localhost'
        self.database = 'inventory_db'
        self.user = 'root'
        self.password = '18Oct@2002'  # UPDATE THIS WITH YOUR MYSQL PASSWORD
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                autocommit=False
            )
            
            if self.connection.is_connected():
                db_info = self.connection.get_server_info()
                print(f"\n✓ Connected to MySQL Server version {db_info}")
                
                cursor = self.connection.cursor()
                cursor.execute("SELECT DATABASE();")
                record = cursor.fetchone()
                print(f"✓ Connected to database: {record[0]}\n")
                cursor.close()
                return True
                
        except Error as e:
            print(f"\n✗ Error connecting to MySQL: {e}\n")
            return False
            
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("\n✓ Database connection closed\n")
            
    def execute_query(self, query, params=None):
        """Execute INSERT, UPDATE, DELETE query"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            self.connection.rollback()
            print(f"✗ Error executing query: {e}")
            raise
        finally:
            cursor.close()
            
    def fetch_all(self, query, params=None):
        """Execute SELECT query and fetch all results"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            return results
        except Error as e:
            print(f"✗ Error fetching data: {e}")
            return []
        finally:
            cursor.close()
            
    def fetch_one(self, query, params=None):
        """Execute SELECT query and fetch one result"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            return result
        except Error as e:
            print(f"✗ Error fetching data: {e}")
            return None
        finally:
            cursor.close()
            
    def call_procedure(self, proc_name, params):
        """Call stored procedure with OUT parameters"""
        try:
            cursor = self.connection.cursor()
            result = cursor.callproc(proc_name, params)
            self.connection.commit()
            cursor.close()
            return result
        except Error as e:
            self.connection.rollback()
            print(f"✗ Error calling procedure: {e}")
            raise

# Global database instance
db = Database()

def init_database():
    """Initialize database connection"""
    return db.connect()

def close_database():
    """Close database connection"""
    db.disconnect()

def log_transaction(operation_type, table_name, record_id, old_values=None, new_values=None, user_name='system'):
    """Log transaction for undo feature"""
    try:
        query = """
            INSERT INTO TransactionLog 
            (operation_type, table_name, record_id, old_values, new_values, user_name)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        db.execute_query(query, (operation_type, table_name, record_id, old_values, new_values, user_name))
    except Exception as e:
        print(f"Warning: Could not log transaction: {e}")

@contextmanager
def get_cursor():
    """Context manager for database cursor"""
    cursor = db.connection.cursor(dictionary=True)
    try:
        yield cursor
        db.connection.commit()
    except Error as e:
        db.connection.rollback()
        raise
    finally:
        cursor.close()
