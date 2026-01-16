import json
import psycopg2
from psycopg2.extras import RealDictCursor

import config

class DatabaseAPI:

    def __init__(self, database_url: str):
        self.database_url = database_url

    def get_db_connection(self):
        return psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)

    def init_db(self):
        conn = self.get_db_connection()
        cur = conn.cursor()
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS jobs (
                {", ".join(config.database_fields)}
            )
        """)
        conn.commit()
        cur.close()
        conn.close()

    def ensure_schema(self):
        conn = self.get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                    CREATE TABLE IF NOT EXISTS jobs (
                        id SERIAL PRIMARY KEY,
                        url TEXT UNIQUE
                    )
                """)

            for field in config.database_fields:
                cur.execute(f"ALTER TABLE jobs ADD COLUMN IF NOT EXISTS {field};")

            conn.commit()
        finally:
            cur.close()
            conn.close()

    def job_exists(self, job_url):
        conn = self.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM jobs WHERE url = %s", (job_url,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result is not None

    def get_job_field_value(self, url, field):
        conn = self.get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(f"""
            SELECT {field} FROM jobs WHERE url = %s
        """, (url,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if not result:
            return None

        value = result[field]  # Direct column access

        if field in ['details', 'attributes', 'search_titles'] and value:
            try:
                return json.loads(value)
            except:
                return value

        return value

    def add_job(self, url, apply_url, job_title, search_titles, company, location, description, attributes, benefits,
                posted_time, search_time):
        conn = self.get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO jobs (url, apply_url, job_title, search_titles, company, location, description, attributes, benefits, posted_time, search_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            url, apply_url, job_title, json.dumps(search_titles), company, location, description,
            json.dumps(attributes), json.dumps(benefits), posted_time, search_time
        ))
        conn.commit()
        cur.close()
        conn.close()

    def is_processed(self, job_url):
        conn = self.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT processed FROM jobs WHERE url = %s", (job_url,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return bool(result["processed"]) if result else False

    def mark_processed(self, job_url):
        conn = self.get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE jobs SET processed = TRUE WHERE url = %s", (job_url,))
        conn.commit()
        cur.close()
        conn.close()

    def get_unprocessed_jobs(self, limit=10):
        conn = self.get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT * FROM jobs 
            WHERE processed = FALSE 
            ORDER BY posted_date DESC 
            LIMIT %s
        """, (limit,))
        jobs = cur.fetchall()
        cur.close()
        conn.close()
        return jobs

    def get_last_search_time_by_job_search_title(self, job_search_title):
        conn = self.get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT search_time
                FROM jobs
                WHERE search_titles::jsonb ? %s
                  AND search_time IS NOT NULL
                ORDER BY search_time DESC
                LIMIT 1
                """,
                (job_search_title,),
            )
            row = cur.fetchone()
            return row["search_time"] if row else None
        finally:
            cur.close()
            conn.close()

    def add_search_title(self, url, search_title):
        conn = self.get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                UPDATE jobs
                SET search_titles =
                    CASE
                        WHEN search_titles IS NULL THEN jsonb_build_array(%s)::json
                        WHEN NOT (search_titles::jsonb ? %s) THEN
                            (search_titles::jsonb || jsonb_build_array(%s))::json
                        ELSE search_titles
                    END
                WHERE url = %s
                """,
                (search_title, search_title, search_title, url),
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            cur.close()
            conn.close()





