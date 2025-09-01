#!/usr/bin/env python3
"""
Database management script for China Stock Analysis app.
Provides utilities to manage the SQLite database.
"""

import argparse
import sys
from database import db_manager

def list_starred_stocks(user_id='default_user'):
    """List all starred stocks for a user."""
    stocks = db_manager.get_starred_stocks(user_id)
    
    if not stocks:
        print(f"No starred stocks found for user: {user_id}")
        return
    
    print(f"\nStarred stocks for user '{user_id}':")
    print("-" * 50)
    print(f"{'Stock Code':<12} {'Stock Name':<20} {'Added At'}")
    print("-" * 50)
    
    for stock in stocks:
        print(f"{stock['code']:<12} {stock['name']:<20} {stock['addedAt']}")
    
    print(f"\nTotal: {len(stocks)} stocks")

def add_stock(stock_code, stock_name, user_id='default_user'):
    """Add a stock to starred list."""
    success = db_manager.add_starred_stock(stock_code, stock_name, user_id)
    
    if success:
        print(f"✅ Added {stock_code} ({stock_name}) to starred list")
    else:
        print(f"❌ Failed to add {stock_code} - may already exist")

def remove_stock(stock_code, user_id='default_user'):
    """Remove a stock from starred list."""
    success = db_manager.remove_starred_stock(stock_code, user_id)
    
    if success:
        print(f"✅ Removed {stock_code} from starred list")
    else:
        print(f"❌ Failed to remove {stock_code} - not found")

def clear_all_stocks(user_id='default_user'):
    """Clear all starred stocks for a user."""
    count = db_manager.get_starred_count(user_id)
    
    if count == 0:
        print(f"No starred stocks to clear for user: {user_id}")
        return
    
    confirm = input(f"Are you sure you want to clear {count} starred stocks for user '{user_id}'? (y/N): ")
    
    if confirm.lower() == 'y':
        success = db_manager.clear_all_starred(user_id)
        if success:
            print(f"✅ Cleared all starred stocks for user: {user_id}")
        else:
            print(f"❌ Failed to clear starred stocks")
    else:
        print("Operation cancelled")

def backup_database(backup_path=None):
    """Create a backup of the database."""
    success = db_manager.backup_database(backup_path)
    
    if success:
        print(f"✅ Database backed up successfully")
    else:
        print(f"❌ Failed to backup database")

def init_database():
    """Initialize the database."""
    try:
        db_manager.init_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize database: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Manage China Stock Analysis database')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List starred stocks')
    list_parser.add_argument('--user', default='default_user', help='User ID')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add starred stock')
    add_parser.add_argument('code', help='Stock code')
    add_parser.add_argument('name', help='Stock name')
    add_parser.add_argument('--user', default='default_user', help='User ID')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove starred stock')
    remove_parser.add_argument('code', help='Stock code')
    remove_parser.add_argument('--user', default='default_user', help='User ID')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear all starred stocks')
    clear_parser.add_argument('--user', default='default_user', help='User ID')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Backup database')
    backup_parser.add_argument('--path', help='Backup file path')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize database')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'list':
            list_starred_stocks(args.user)
        elif args.command == 'add':
            add_stock(args.code, args.name, args.user)
        elif args.command == 'remove':
            remove_stock(args.code, args.user)
        elif args.command == 'clear':
            clear_all_stocks(args.user)
        elif args.command == 'backup':
            backup_database(args.path)
        elif args.command == 'init':
            init_database()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
