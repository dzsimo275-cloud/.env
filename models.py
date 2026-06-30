from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import json

@dataclass
class UserStats:
    """إحصائيات المستخدم"""
    user_id: int
    username: str
    points: int = 0
    events_participated: int = 0
    events_won: int = 0
    achievements: List[str] = field(default_factory=list)
    last_event: Optional[datetime] = None
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'points': self.points,
            'events_participated': self.events_participated,
            'events_won': self.events_won,
            'achievements': self.achievements,
            'last_event': self.last_event.isoformat() if self.last_event else None,
        }

@dataclass
class Event:
    """بيانات الفعالية"""
    event_id: int
    title: str
    description: str
    event_type: str  # 'dice', 'giveaway', 'quiz', etc.
    creator_id: int
    created_at: datetime
    participants: Dict[int, str] = field(default_factory=dict)
    winners: List[int] = field(default_factory=list)
    status: str = 'active'  # active, ended, cancelled
    data: Dict = field(default_factory=dict)
    
    def to_dict(self):
        return {
            'event_id': self.event_id,
            'title': self.title,
            'description': self.description,
            'event_type': self.event_type,
            'creator_id': self.creator_id,
            'created_at': self.created_at.isoformat(),
            'participants': self.participants,
            'winners': self.winners,
            'status': self.status,
            'data': self.data,
        }

@dataclass
class Achievement:
    """الإنجازات والأوسمة"""
    achievement_id: str
    name: str
    description: str
    emoji: str
    requirement: str  # نص يشرح الشرط
    
    def to_dict(self):
        return {
            'achievement_id': self.achievement_id,
            'name': self.name,
            'description': self.description,
            'emoji': self.emoji,
            'requirement': self.requirement,
        }
