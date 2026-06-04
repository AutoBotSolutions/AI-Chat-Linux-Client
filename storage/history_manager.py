"""
History manager for storing and retrieving chat history.
"""

import json
import sqlite3
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class ChatMessage:
    """Represents a single chat message."""
    id: Optional[int] = None
    role: str = ""  # "user", "assistant", "system"
    content: str = ""
    model: Optional[str] = None
    provider: Optional[str] = None
    timestamp: Optional[datetime] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ChatSession:
    """Represents a chat session."""
    id: Optional[int] = None
    session_id: str = ""
    title: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    message_count: int = 0
    metadata: Optional[Dict[str, Any]] = None


class HistoryManager:
    """Manages chat history storage and retrieval."""
    
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir or self._get_default_data_dir())
        self.db_file = self.data_dir / "chat_history.db"
        self.logger = logging.getLogger(__name__)
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _get_default_data_dir(self) -> str:
        """Get default data directory."""
        home = Path.home()
        if os.name == 'nt':  # Windows
            return str(home / "AppData" / "Local" / "ChatLinuxClient" / "data")
        else:  # Linux/Mac
            return str(home / ".local" / "share" / "chat-linux-client")
    
    def _init_database(self) -> None:
        """Initialize the SQLite database."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Create sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE NOT NULL,
                        title TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        message_count INTEGER DEFAULT 0,
                        metadata TEXT
                    )
                """)
                
                # Create messages table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        model TEXT,
                        provider TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT,
                        FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages (session_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages (timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_updated_at ON sessions (updated_at)")
                
                conn.commit()
                self.logger.info("Database initialized successfully")
        
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def create_session(self, title: str = "New Chat") -> str:
        """Create a new chat session."""
        import uuid
        session_id = str(uuid.uuid4())
        
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sessions (session_id, title, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                """, (session_id, title, datetime.now(), datetime.now()))
                conn.commit()
                self.logger.info(f"Created new session: {session_id}")
                return session_id
        
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a specific chat session."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, session_id, title, created_at, updated_at, message_count, metadata
                    FROM sessions WHERE session_id = ?
                """, (session_id,))
                
                row = cursor.fetchone()
                if row:
                    metadata = json.loads(row[6]) if row[6] else None
                    return ChatSession(
                        id=row[0],
                        session_id=row[1],
                        title=row[2],
                        created_at=datetime.fromisoformat(row[3]) if row[3] else None,
                        updated_at=datetime.fromisoformat(row[4]) if row[4] else None,
                        message_count=row[5],
                        metadata=metadata
                    )
                return None
        
        except Exception as e:
            self.logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    def list_sessions(self, limit: int = 50) -> List[ChatSession]:
        """List recent chat sessions."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, session_id, title, created_at, updated_at, message_count, metadata
                    FROM sessions
                    ORDER BY updated_at DESC
                    LIMIT ?
                """, (limit,))
                
                sessions = []
                for row in cursor.fetchall():
                    metadata = json.loads(row[6]) if row[6] else None
                    sessions.append(ChatSession(
                        id=row[0],
                        session_id=row[1],
                        title=row[2],
                        created_at=datetime.fromisoformat(row[3]) if row[3] else None,
                        updated_at=datetime.fromisoformat(row[4]) if row[4] else None,
                        message_count=row[5],
                        metadata=metadata
                    ))
                return sessions
        
        except Exception as e:
            self.logger.error(f"Failed to list sessions: {e}")
            return []
    
    def save_message(self, role: str, content: str, session_id: Optional[str] = None,
                     model: Optional[str] = None, provider: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """Save a chat message."""
        import uuid
        
        # Create session if none provided
        if not session_id:
            session_id = self.create_session()
        
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Save message
                metadata_json = json.dumps(metadata) if metadata else None
                cursor.execute("""
                    INSERT INTO messages (session_id, role, content, model, provider, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (session_id, role, content, model, provider, metadata_json))
                
                # Update session
                cursor.execute("""
                    UPDATE sessions 
                    SET updated_at = ?, message_count = message_count + 1
                    WHERE session_id = ?
                """, (datetime.now(), session_id))
                
                conn.commit()
                self.logger.debug(f"Saved message for session {session_id}")
                return session_id
        
        except Exception as e:
            self.logger.error(f"Failed to save message: {e}")
            raise
    
    def add_message(self, session_id: str, role: str, content: str, 
                   model: Optional[str] = None, provider: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a message to a session (alias for save_message)."""
        return self.save_message(role, content, session_id, model, provider, metadata)
    
    def get_session_messages(self, session_id: str, limit: int = 100) -> List[ChatMessage]:
        """Get messages for a specific session (alias for get_messages)."""
        return self.get_messages(session_id, limit)
    
    def get_messages(self, session_id: str, limit: int = 100) -> List[ChatMessage]:
        """Get messages for a specific session."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, session_id, role, content, model, provider, timestamp, metadata
                    FROM messages
                    WHERE session_id = ?
                    ORDER BY timestamp ASC
                    LIMIT ?
                """, (session_id, limit))
                
                messages = []
                for row in cursor.fetchall():
                    metadata = json.loads(row[7]) if row[7] else None
                    messages.append(ChatMessage(
                        id=row[0],
                        session_id=row[1],
                        role=row[2],
                        content=row[3],
                        model=row[4],
                        provider=row[5],
                        timestamp=datetime.fromisoformat(row[6]) if row[6] else None,
                        metadata=metadata
                    ))
                return messages
        
        except Exception as e:
            self.logger.error(f"Failed to get messages for session {session_id}: {e}")
            return []
    
    def search_messages(self, query: str, limit: int = 50) -> List[ChatMessage]:
        """Search messages by content."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, session_id, role, content, model, provider, timestamp, metadata
                    FROM messages
                    WHERE content LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (f"%{query}%", limit))
                
                messages = []
                for row in cursor.fetchall():
                    metadata = json.loads(row[7]) if row[7] else None
                    messages.append(ChatMessage(
                        id=row[0],
                        session_id=row[1],
                        role=row[2],
                        content=row[3],
                        model=row[4],
                        provider=row[5],
                        timestamp=datetime.fromisoformat(row[6]) if row[6] else None,
                        metadata=metadata
                    ))
                return messages
        
        except Exception as e:
            self.logger.error(f"Failed to search messages: {e}")
            return []
    
    def update_session_title(self, session_id: str, title: str) -> bool:
        """Update session title."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE sessions SET title = ?, updated_at = ?
                    WHERE session_id = ?
                """, (title, datetime.now(), session_id))
                conn.commit()
                return cursor.rowcount > 0
        
        except Exception as e:
            self.logger.error(f"Failed to update session title: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
                cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                conn.commit()
                return cursor.rowcount > 0
        
        except Exception as e:
            self.logger.error(f"Failed to delete session: {e}")
            return False
    
    def clear_history(self) -> bool:
        """Clear all chat history."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM messages")
                cursor.execute("DELETE FROM sessions")
                conn.commit()
                self.logger.info("Cleared all chat history")
                return True
        
        except Exception as e:
            self.logger.error(f"Failed to clear history: {e}")
            return False
    
    def export_session(self, session_id: str, format: str = "json") -> Optional[str]:
        """Export a session in the specified format."""
        try:
            session = self.get_session(session_id)
            if not session:
                return None
            
            messages = self.get_messages(session_id)
            
            if format == "json":
                export_data = {
                    "session": asdict(session),
                    "messages": [asdict(msg) for msg in messages]
                }
                return json.dumps(export_data, indent=2, default=str)
            
            elif format == "txt":
                lines = [f"Session: {session.title}"]
                lines.append(f"Created: {session.created_at}")
                lines.append("=" * 50)
                
                for msg in messages:
                    timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S") if msg.timestamp else ""
                    lines.append(f"[{timestamp}] {msg.role.title()}: {msg.content}")
                
                return "\n".join(lines)
            
            elif format == "markdown":
                lines = [f"# {session.title}"]
                lines.append(f"*Created: {session.created_at}*\n")
                
                for msg in messages:
                    timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S") if msg.timestamp else ""
                    lines.append(f"## {msg.role.title()} - {timestamp}")
                    lines.append(msg.content)
                    lines.append("")
                
                return "\n".join(lines)
            
            else:
                # Unsupported format
                self.logger.warning(f"Unsupported export format: {format}")
                return None
        
        except Exception as e:
            self.logger.error(f"Failed to export session: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get chat history statistics."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Total sessions
                cursor.execute("SELECT COUNT(*) FROM sessions")
                total_sessions = cursor.fetchone()[0]
                
                # Total messages
                cursor.execute("SELECT COUNT(*) FROM messages")
                total_messages = cursor.fetchone()[0]
                
                # Messages by role
                cursor.execute("SELECT role, COUNT(*) FROM messages GROUP BY role")
                messages_by_role = dict(cursor.fetchall())
                
                # Most active session
                cursor.execute("""
                    SELECT session_id, COUNT(*) as message_count 
                    FROM messages 
                    GROUP BY session_id 
                    ORDER BY message_count DESC 
                    LIMIT 1
                """)
                most_active = cursor.fetchone()
                
                return {
                    "total_sessions": total_sessions,
                    "total_messages": total_messages,
                    "messages_by_role": messages_by_role,
                    "most_active_session": most_active[0] if most_active else None,
                    "most_active_message_count": most_active[1] if most_active else 0
                }
        
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {}
