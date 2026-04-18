import os
import psycopg2
import psycopg2.extras
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")


def get_conn():
    return psycopg2.connect(DATABASE_URL, sslmode="disable")


def init_projects_table():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS scraped_projects (
                    id          SERIAL PRIMARY KEY,
                    platform    VARCHAR(50)  NOT NULL,
                    project_id  VARCHAR(200) DEFAULT '',
                    title       TEXT         NOT NULL,
                    brief       TEXT         DEFAULT '',
                    budget      VARCHAR(200) DEFAULT '',
                    link        TEXT         NOT NULL,
                    time_rel    VARCHAR(200) DEFAULT '',
                    posted_at   VARCHAR(200) DEFAULT '',
                    scraped_at  TIMESTAMP    DEFAULT NOW(),
                    UNIQUE(platform, link)
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_projects_platform
                ON scraped_projects(platform)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_projects_scraped_at
                ON scraped_projects(scraped_at DESC)
            """)
        conn.commit()


def upsert_projects(projects: list[dict]) -> int:
    """Insert or ignore duplicate projects. Returns count of new rows."""
    if not projects:
        return 0
    inserted = 0
    with get_conn() as conn:
        with conn.cursor() as cur:
            for p in projects:
                try:
                    cur.execute("""
                        INSERT INTO scraped_projects
                            (platform, project_id, title, brief, budget, link, time_rel, posted_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (platform, link) DO NOTHING
                    """, (
                        p.get("platform", ""),
                        p.get("project_id", ""),
                        p.get("title", ""),
                        p.get("brief", ""),
                        p.get("budget", ""),
                        p.get("link", ""),
                        p.get("time_rel", ""),
                        p.get("posted_at", ""),
                    ))
                    if cur.rowcount:
                        inserted += 1
                except Exception:
                    pass
        conn.commit()
    return inserted


def get_latest_projects(platform: str = None, limit: int = 30) -> list[dict]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if platform:
                cur.execute("""
                    SELECT * FROM scraped_projects
                    WHERE platform = %s
                    ORDER BY scraped_at DESC
                    LIMIT %s
                """, (platform, limit))
            else:
                cur.execute("""
                    SELECT * FROM scraped_projects
                    ORDER BY scraped_at DESC
                    LIMIT %s
                """, (limit,))
            return [dict(r) for r in cur.fetchall()]


def get_new_since(platform: str, last_link: str) -> list[dict]:
    """Return projects scraped after a given link (for dedup in monitor loop)."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM scraped_projects
                WHERE platform = %s
                  AND link NOT IN (
                      SELECT link FROM scraped_projects
                      WHERE link = %s
                  )
                ORDER BY scraped_at DESC
                LIMIT 50
            """, (platform, last_link))
            return [dict(r) for r in cur.fetchall()]


def get_stats_per_platform() -> list[dict]:
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    platform,
                    COUNT(*) AS total,
                    MAX(scraped_at) AS last_scraped
                FROM scraped_projects
                GROUP BY platform
                ORDER BY total DESC
            """)
            return [dict(r) for r in cur.fetchall()]
