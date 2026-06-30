import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DATABASE_PATH = os.getenv('DATABASE_PATH', './data/events.db')

# الألوان
COLORS = {
    'primary': 0x5B9BD5,
    'success': 0x70AD47,
    'warning': 0xFFC000,
    'error': 0xC55A11,
    'info': 0x4472C4,
}

# الرموز
EMOJIS = {
    'dice': '🎲',
    'gift': '🎁',
    'brain': '🧠',
    'image': '🖼️',
    'lightning': '⚡',
    'game': '🎮',
    'target': '🎯',
    'trophy': '🏆',
    'chart': '📊',
    'timer': '⏰',
    'clipboard': '📝',
    'success': '✅',
    'error': '❌',
    'heart': '❤️',
    'star': '⭐',
    'laugh': '😂',
}

# إعدادات الفعاليات
EVENT_CONFIG = {
    'max_title_length': 100,
    'max_description_length': 2000,
    'default_timeout': 300,  # 5 minutes
    'points_per_win': 10,
    'points_per_participation': 1,
}
