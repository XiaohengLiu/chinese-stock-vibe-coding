"""
Database models and operations for the China Stock Analysis app.
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional
import os

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations for starred stocks."""
    
    def __init__(self, db_path: str = "stocks.db"):
        """
        Initialize the database manager.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create starred_stocks table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS starred_stocks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        stock_code TEXT UNIQUE NOT NULL,
                        stock_name TEXT NOT NULL,
                        user_id TEXT DEFAULT 'default_user',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create index for faster queries
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_stock_code 
                    ON starred_stocks(stock_code)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_user_id 
                    ON starred_stocks(user_id)
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def add_starred_stock(self, stock_code: str, stock_name: str, user_id: str = "default_user") -> bool:
        """
        Add a stock to the starred list.
        
        Args:
            stock_code (str): Stock code
            stock_name (str): Stock name
            user_id (str): User identifier
            
        Returns:
            bool: True if added successfully, False if already exists
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if stock is already starred
                cursor.execute('''
                    SELECT id FROM starred_stocks 
                    WHERE stock_code = ? AND user_id = ?
                ''', (stock_code, user_id))
                
                if cursor.fetchone():
                    logger.info(f"Stock {stock_code} already starred for user {user_id}")
                    return False
                
                # Add new starred stock
                cursor.execute('''
                    INSERT INTO starred_stocks (stock_code, stock_name, user_id)
                    VALUES (?, ?, ?)
                ''', (stock_code, stock_name, user_id))
                
                conn.commit()
                logger.info(f"Added starred stock: {stock_code} ({stock_name})")
                return True
                
        except Exception as e:
            logger.error(f"Error adding starred stock {stock_code}: {str(e)}")
            return False
    
    def remove_starred_stock(self, stock_code: str, user_id: str = "default_user") -> bool:
        """
        Remove a stock from the starred list.
        
        Args:
            stock_code (str): Stock code
            user_id (str): User identifier
            
        Returns:
            bool: True if removed successfully, False if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM starred_stocks 
                    WHERE stock_code = ? AND user_id = ?
                ''', (stock_code, user_id))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Removed starred stock: {stock_code}")
                    return True
                else:
                    logger.info(f"Stock {stock_code} not found in starred list")
                    return False
                    
        except Exception as e:
            logger.error(f"Error removing starred stock {stock_code}: {str(e)}")
            return False
    
    def get_starred_stocks(self, user_id: str = "default_user") -> List[Dict]:
        """
        Get all starred stocks for a user.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            List[Dict]: List of starred stocks with their details
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT stock_code, stock_name, created_at 
                    FROM starred_stocks 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                ''', (user_id,))
                
                results = cursor.fetchall()
                
                starred_stocks = []
                for row in results:
                    starred_stocks.append({
                        'code': row[0],
                        'name': row[1],
                        'addedAt': row[2]
                    })
                
                logger.info(f"Retrieved {len(starred_stocks)} starred stocks for user {user_id}")
                return starred_stocks
                
        except Exception as e:
            logger.error(f"Error getting starred stocks: {str(e)}")
            return []
    
    def is_stock_starred(self, stock_code: str, user_id: str = "default_user") -> bool:
        """
        Check if a stock is starred by a user.
        
        Args:
            stock_code (str): Stock code
            user_id (str): User identifier
            
        Returns:
            bool: True if starred, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id FROM starred_stocks 
                    WHERE stock_code = ? AND user_id = ?
                ''', (stock_code, user_id))
                
                return cursor.fetchone() is not None
                
        except Exception as e:
            logger.error(f"Error checking if stock {stock_code} is starred: {str(e)}")
            return False
    
    def clear_all_starred(self, user_id: str = "default_user") -> bool:
        """
        Clear all starred stocks for a user.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            bool: True if cleared successfully
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM starred_stocks WHERE user_id = ?
                ''', (user_id,))
                
                conn.commit()
                logger.info(f"Cleared all starred stocks for user {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error clearing starred stocks: {str(e)}")
            return False
    
    def get_starred_count(self, user_id: str = "default_user") -> int:
        """
        Get the count of starred stocks for a user.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            int: Number of starred stocks
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT COUNT(*) FROM starred_stocks WHERE user_id = ?
                ''', (user_id,))
                
                count = cursor.fetchone()[0]
                return count
                
        except Exception as e:
            logger.error(f"Error getting starred count: {str(e)}")
            return 0
    
    def backup_database(self, backup_path: str = None) -> bool:
        """
        Create a backup of the database.
        
        Args:
            backup_path (str): Path for backup file
            
        Returns:
            bool: True if backup successful
        """
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"stocks_backup_{timestamp}.db"
        
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error backing up database: {str(e)}")
            return False

# Global database instance
db_manager = DatabaseManager()
