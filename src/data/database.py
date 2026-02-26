"""SQLite Database Manager."""
import sqlite3
from typing import List, Dict, Optional
from src.utils.constants import DATABASE_FILE


class DatabaseManager:
    """Singleton class to manage SQLite database operations."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_db()
        return cls._instance
    
    def _init_db(self) -> None:
        """Initialize database and create tables."""
        self.conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self) -> None:
        """Create required tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # History table - stores generated presentations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                prompt TEXT,
                outline_json TEXT,
                template_name TEXT,
                output_path TEXT,
                slide_count INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Templates table - stores custom templates
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                display_name TEXT,
                description TEXT,
                category TEXT,
                preview_path TEXT,
                config_json TEXT,
                is_builtin BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    # ============ History Operations ============
    
    def add_history(self, title: str, prompt: str, outline_json: str,
                    template_name: str, output_path: str, slide_count: int) -> int:
        """Add new history entry. Returns the new entry ID."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO history (title, prompt, outline_json, template_name, 
                                output_path, slide_count)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, prompt, outline_json, template_name, output_path, slide_count))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_history(self, limit: int = 20) -> List[Dict]:
        """Get recent history entries."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM history ORDER BY created_at DESC LIMIT ?
        ''', (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_history_by_id(self, history_id: int) -> Optional[Dict]:
        """Get single history entry by ID."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM history WHERE id = ?', (history_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def delete_history(self, history_id: int) -> None:
        """Delete history entry by ID."""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM history WHERE id = ?', (history_id,))
        self.conn.commit()
    
    def clear_history(self) -> None:
        """Delete all history entries."""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM history')
        self.conn.commit()
    
    # ============ Template Operations ============
    
    def get_templates(self, category: str = None) -> List[Dict]:
        """Get all templates, optionally filtered by category."""
        cursor = self.conn.cursor()
        if category:
            cursor.execute('SELECT * FROM templates WHERE category = ?', (category,))
        else:
            cursor.execute('SELECT * FROM templates')
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
