"""Database management for RepoRadar."""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class RepoRadarDB:
    """SQLite database manager for RepoRadar."""

    def __init__(self, db_path: str = "reporadar.db"):
        """Initialize database connection and create tables."""
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS repo_transfers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repo TEXT NOT NULL,
                    old_owner TEXT NOT NULL,
                    new_owner TEXT NOT NULL,
                    date TEXT NOT NULL,
                    stars INTEGER DEFAULT 0,
                    language TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(repo, old_owner, new_owner, date)
                )
            """)
            conn.commit()
            logger.info("Database initialized successfully")

    def add_transfer(self, repo: str, old_owner: str, new_owner: str, 
                    date: str, stars: int = 0, language: str = None) -> bool:
        """Add a repository transfer to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT OR IGNORE INTO repo_transfers 
                       (repo, old_owner, new_owner, date, stars, language)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (repo, old_owner, new_owner, date, stars, language)
                )
                conn.commit()
                logger.info(f"Added transfer: {repo} from {old_owner} to {new_owner}")
                return True
        except Exception as e:
            logger.error(f"Error adding transfer: {e}")
            return False

    def get_transfers(self, limit: int = 100) -> List[Dict]:
        """Get recent repository transfers."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """SELECT * FROM repo_transfers 
                       ORDER BY created_at DESC LIMIT ?""",
                    (limit,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting transfers: {e}")
            return []

    def get_stats(self) -> Dict:
        """Get transfer statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_transfers,
                        COUNT(DISTINCT new_owner) as unique_buyers,
                        COUNT(DISTINCT old_owner) as unique_sellers,
                        AVG(stars) as avg_stars,
                        MAX(stars) as max_stars
                    FROM repo_transfers
                """)
                stats = dict(cursor.fetchone())
                
                # Get top buyers
                cursor = conn.execute("""
                    SELECT new_owner, COUNT(*) as count
                    FROM repo_transfers 
                    GROUP BY new_owner 
                    ORDER BY count DESC 
                    LIMIT 10
                """)
                stats['top_buyers'] = [dict(row) for row in cursor.fetchall()]
                
                return stats
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}