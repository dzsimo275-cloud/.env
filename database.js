import Database from 'better-sqlite3';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dbPath = process.env.DATABASE_PATH || path.join(__dirname, 'data', 'events.db');

// التأكد من وجود مجلد البيانات
if (!fs.existsSync(path.dirname(dbPath))) {
  fs.mkdirSync(path.dirname(dbPath), { recursive: true });
}

class EventsDatabase {
  constructor() {
    this.db = new Database(dbPath);
    this.db.pragma('journal_mode = WAL');
    this.initDb();
  }

  initDb() {
    // جدول إحصائيات المستخدمين
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS user_stats (
        user_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        points INTEGER DEFAULT 0,
        events_participated INTEGER DEFAULT 0,
        events_won INTEGER DEFAULT 0,
        achievements TEXT DEFAULT '[]',
        last_event DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // جدول الفعاليات
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        event_type TEXT NOT NULL,
        creator_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        participants TEXT DEFAULT '{}',
        winners TEXT DEFAULT '[]',
        status TEXT DEFAULT 'active',
        data TEXT DEFAULT '{}',
        ended_at DATETIME
      )
    `);

    // جدول الإنجازات
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS achievements (
        achievement_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        emoji TEXT NOT NULL,
        requirement TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // جدول سجل الأحداث
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS event_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER,
        action TEXT NOT NULL,
        user_id INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        details TEXT
      )
    `);
  }

  // ===== إحصائيات المستخدمين =====
  getUserStats(userId) {
    const stmt = this.db.prepare('SELECT * FROM user_stats WHERE user_id = ?');
    const row = stmt.get(userId);
    if (row) {
      return {
        userId: row.user_id,
        username: row.username,
        points: row.points,
        eventsParticipated: row.events_participated,
        eventsWon: row.events_won,
        achievements: JSON.parse(row.achievements),
        lastEvent: row.last_event,
      };
    }
    return null;
  }

  addUserStats(userId, username) {
    const stmt = this.db.prepare('INSERT OR IGNORE INTO user_stats (user_id, username) VALUES (?, ?)');
    stmt.run(userId, username);
    return this.getUserStats(userId);
  }

  updateUserPoints(userId, points, action = 'add') {
    const stmt = this.db.prepare('SELECT points FROM user_stats WHERE user_id = ?');
    const current = stmt.get(userId);
    if (current) {
      const newPoints = action === 'add' ? current.points + points : points;
      const updateStmt = this.db.prepare('UPDATE user_stats SET points = ? WHERE user_id = ?');
      updateStmt.run(newPoints, userId);
    }
  }

  getLeaderboard(limit = 10) {
    const stmt = this.db.prepare('SELECT * FROM user_stats ORDER BY points DESC LIMIT ?');
    const rows = stmt.all(limit);
    return rows.map(row => ({
      userId: row.user_id,
      username: row.username,
      points: row.points,
      eventsParticipated: row.events_participated,
      eventsWon: row.events_won,
      achievements: JSON.parse(row.achievements),
    }));
  }

  // ===== الفعاليات =====
  createEvent(title, description, eventType, creatorId, data = {}) {
    const stmt = this.db.prepare(
      'INSERT INTO events (title, description, event_type, creator_id, data) VALUES (?, ?, ?, ?, ?)'
    );
    const info = stmt.run(title, description, eventType, creatorId, JSON.stringify(data));
    return this.getEvent(info.lastInsertRowid);
  }

  getEvent(eventId) {
    const stmt = this.db.prepare('SELECT * FROM events WHERE event_id = ?');
    const row = stmt.get(eventId);
    if (row) {
      return {
        eventId: row.event_id,
        title: row.title,
        description: row.description,
        eventType: row.event_type,
        creatorId: row.creator_id,
        createdAt: row.created_at,
        participants: JSON.parse(row.participants),
        winners: JSON.parse(row.winners),
        status: row.status,
        data: JSON.parse(row.data),
      };
    }
    return null;
  }

  addParticipant(eventId, userId, username) {
    const event = this.getEvent(eventId);
    if (event) {
      event.participants[userId] = username;
      const stmt = this.db.prepare('UPDATE events SET participants = ? WHERE event_id = ?');
      stmt.run(JSON.stringify(event.participants), eventId);
    }
  }

  endEvent(eventId, winners = []) {
    const stmt = this.db.prepare(
      'UPDATE events SET status = ?, winners = ?, ended_at = CURRENT_TIMESTAMP WHERE event_id = ?'
    );
    stmt.run('ended', JSON.stringify(winners), eventId);
  }

  getActiveEvents() {
    const stmt = this.db.prepare('SELECT * FROM events WHERE status = ? ORDER BY created_at DESC');
    const rows = stmt.all('active');
    return rows.map(row => ({
      eventId: row.event_id,
      title: row.title,
      description: row.description,
      eventType: row.event_type,
      creatorId: row.creator_id,
      createdAt: row.created_at,
      participants: JSON.parse(row.participants),
      winners: JSON.parse(row.winners),
      status: row.status,
      data: JSON.parse(row.data),
    }));
  }

  // ===== الإنجازات =====
  addAchievementToUser(userId, achievementId) {
    const stats = this.getUserStats(userId);
    if (stats && !stats.achievements.includes(achievementId)) {
      stats.achievements.push(achievementId);
      const stmt = this.db.prepare('UPDATE user_stats SET achievements = ? WHERE user_id = ?');
      stmt.run(JSON.stringify(stats.achievements), userId);
      return true;
    }
    return false;
  }

  close() {
    this.db.close();
  }
}

export default new EventsDatabase();
