import sqlite3
import json
from typing import Dict, List, Optional
from datetime import datetime
from models import UserStats, Event, Achievement
from config import DATABASE_PATH
import os

class Database:
    """إدارة قاعدة البيانات"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """إنشاء جداول قاعدة البيانات"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # جدول إحصائيات المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                points INTEGER DEFAULT 0,
                events_participated INTEGER DEFAULT 0,
                events_won INTEGER DEFAULT 0,
                achievements TEXT DEFAULT '[]',
                last_event TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول الفعاليات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                event_type TEXT NOT NULL,
                creator_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                participants TEXT DEFAULT '{}',
                winners TEXT DEFAULT '[]',
                status TEXT DEFAULT 'active',
                data TEXT DEFAULT '{}',
                ended_at TIMESTAMP
            )
        ''')
        
        # جدول الإنجازات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                achievement_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                emoji TEXT NOT NULL,
                requirement TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول سجل الأحداث
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                action TEXT NOT NULL,
                user_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ===== إحصائيات المستخدمين =====
    def get_user_stats(self, user_id: int) -> Optional[UserStats]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_stats WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return UserStats(
                user_id=row[0],
                username=row[1],
                points=row[2],
                events_participated=row[3],
                events_won=row[4],
                achievements=json.loads(row[5]),
                last_event=datetime.fromisoformat(row[6]) if row[6] else None,
            )
        return None
    
    def add_user_stats(self, user_id: int, username: str) -> UserStats:
        """إضافة مستخدم جديد"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO user_stats (user_id, username)
            VALUES (?, ?)
        ''', (user_id, username))
        
        conn.commit()
        conn.close()
        
        return self.get_user_stats(user_id)
    
    def update_user_points(self, user_id: int, points: int, action: str = 'add'):
        """تحديث نقاط المستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        current = cursor.execute('SELECT points FROM user_stats WHERE user_id = ?', (user_id,)).fetchone()
        if current:
            new_points = current[0] + points if action == 'add' else points
            cursor.execute('UPDATE user_stats SET points = ? WHERE user_id = ?', (new_points, user_id))
        
        conn.commit()
        conn.close()
    
    def get_leaderboard(self, limit: int = 10) -> List[UserStats]:
        """الحصول على لوحة الترتيب"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_stats
            ORDER BY points DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        stats = []
        for row in rows:
            stats.append(UserStats(
                user_id=row[0],
                username=row[1],
                points=row[2],
                events_participated=row[3],
                events_won=row[4],
                achievements=json.loads(row[5]),
                last_event=datetime.fromisoformat(row[6]) if row[6] else None,
            ))
        
        return stats
    
    # ===== الفعاليات =====
    def create_event(self, title: str, description: str, event_type: str, creator_id: int, data: Dict = None) -> Event:
        """إنشاء فعالية جديدة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO events (title, description, event_type, creator_id, data)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, event_type, creator_id, json.dumps(data or {})))
        
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return self.get_event(event_id)
    
    def get_event(self, event_id: int) -> Optional[Event]:
        """الحصول على فعالية"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM events WHERE event_id = ?', (event_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Event(
                event_id=row[0],
                title=row[1],
                description=row[2],
                event_type=row[3],
                creator_id=row[4],
                created_at=datetime.fromisoformat(row[5]),
                participants=json.loads(row[6]),
                winners=json.loads(row[7]),
                status=row[8],
                data=json.loads(row[9]),
            )
        return None
    
    def add_participant(self, event_id: int, user_id: int, username: str):
        """إضافة مشارك للفعالية"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        event = self.get_event(event_id)
        if event:
            event.participants[str(user_id)] = username
            cursor.execute('UPDATE events SET participants = ? WHERE event_id = ?',
                         (json.dumps(event.participants), event_id))
            conn.commit()
        
        conn.close()
    
    def end_event(self, event_id: int, winners: List[int] = None):
        """إنهاء الفعالية"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE events
            SET status = 'ended', winners = ?, ended_at = CURRENT_TIMESTAMP
            WHERE event_id = ?
        ''', (json.dumps(winners or []), event_id))
        
        conn.commit()
        conn.close()
    
    def get_active_events(self) -> List[Event]:
        """الحصول على الفعاليات النشطة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM events WHERE status = ? ORDER BY created_at DESC', ('active',))
        rows = cursor.fetchall()
        conn.close()
        
        events = []
        for row in rows:
            events.append(Event(
                event_id=row[0],
                title=row[1],
                description=row[2],
                event_type=row[3],
                creator_id=row[4],
                created_at=datetime.fromisoformat(row[5]),
                participants=json.loads(row[6]),
                winners=json.loads(row[7]),
                status=row[8],
                data=json.loads(row[9]),
            ))
        
        return events
    
    # ===== الإنجازات =====
    def add_achievement_to_user(self, user_id: int, achievement_id: str):
        """إضافة إنجاز للمستخدم"""
        stats = self.get_user_stats(user_id)
        if stats and achievement_id not in stats.achievements:
            stats.achievements.append(achievement_id)
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE user_stats SET achievements = ? WHERE user_id = ?',
                         (json.dumps(stats.achievements), user_id))
            conn.commit()
            conn.close()
            
            return True
        return False
