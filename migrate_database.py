#!/usr/bin/env python3
"""
Database Migration Script for Environment Management

This script adds the new environment-related columns to the existing database.
"""

import sqlite3
import os
from pathlib import Path

def migrate_database():
    """Add new environment columns to the tasks table"""
    
    db_path = "cronpilot.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    print(f"🔧 Migrating database: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Current columns: {columns}")
        
        # Add new columns if they don't exist
        new_columns = [
            ("environment_path", "TEXT"),
            ("requirements_path", "TEXT"), 
            ("python_executable", "TEXT")
        ]
        
        for column_name, column_type in new_columns:
            if column_name not in columns:
                print(f"Adding column: {column_name}")
                cursor.execute(f"ALTER TABLE tasks ADD COLUMN {column_name} {column_type}")
            else:
                print(f"Column already exists: {column_name}")
        
        # Commit changes
        conn.commit()
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(tasks)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        print(f"Updated columns: {updated_columns}")
        
        conn.close()
        
        print("✅ Database migration completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    if success:
        print("\n🎉 Migration successful! You can now restart the application.")
    else:
        print("\n⚠️  Migration failed. Please check the error messages above.")
