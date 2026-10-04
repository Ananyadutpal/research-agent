"""Long-term memory: SQLite store of past reports, searchable by keyword."""
import sqlite3
from datetime import datetime


class Memory:
    def __init__(self, path: str = "memory.db"):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY, topic TEXT, "
            "report TEXT, created TEXT)"
        )

    def save(self, topic: str, report: str) -> None:
        self.db.execute("INSERT INTO reports (topic, report, created) VALUES (?,?,?)",
                        (topic, report, datetime.now().isoformat(timespec="seconds")))
        self.db.commit()

    def search(self, query: str, limit: int = 3) -> list[dict]:
        words = [w for w in query.lower().split() if len(w) > 3]
        if not words:
            return []
        clause = " OR ".join(["lower(topic) LIKE ? OR lower(report) LIKE ?"] * len(words))
        params = [p for w in words for p in (f"%{w}%", f"%{w}%")]
        rows = self.db.execute(
            f"SELECT topic, report, created FROM reports WHERE {clause} "
            f"ORDER BY id DESC LIMIT {int(limit)}", params).fetchall()
        return [{"topic": t, "excerpt": r[:800], "created": c} for t, r, c in rows]
