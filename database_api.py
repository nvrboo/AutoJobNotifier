import json
import psycopg2
from psycopg2.extras import RealDictCursor

import config

class DatabaseAPI:

    @staticmethod
    def get_db_connection():
        return psycopg2.connect(config.DATABASE_URL, cursor_factory=RealDictCursor)

    @staticmethod
    def init_db():
        conn = DatabaseAPI.get_db_connection()
        cur = conn.cursor()
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS jobs (
                {", ".join(config.database_fields)}
            )
        """)
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def ensure_schema():
        conn = DatabaseAPI.get_db_connection()
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

    @staticmethod
    def job_exists(job_url):
        conn = DatabaseAPI.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM jobs WHERE url = %s", (job_url,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result is not None

    @staticmethod
    def get_job_field_value(url, field):
        conn = DatabaseAPI.get_db_connection()
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

        if field in ['details', 'attributes', 'original_search_titles'] and value:
            try:
                return json.loads(value)
            except:
                return value

        return value

    @staticmethod
    def add_job(url, apply_url, job_title, original_search_title, company, location, description, attributes, benefits,
                posted_time, search_time):
        conn = DatabaseAPI.get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO jobs (url, apply_url, job_title, original_search_titles, company, location, description, attributes, benefits, posted_time, search_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            url, apply_url, job_title, json.dumps([original_search_title]), company, location, description,
            json.dumps(attributes), json.dumps(benefits), posted_time, search_time
        ))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def is_processed(job_url):
        conn = DatabaseAPI.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT processed FROM jobs WHERE url = %s", (job_url,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return bool(result["processed"]) if result else False

    @staticmethod
    def mark_processed(job_url):
        conn = DatabaseAPI.get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE jobs SET processed = TRUE WHERE url = %s", (job_url,))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def get_unprocessed_jobs(limit=10):
        conn = DatabaseAPI.get_db_connection()
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

    @staticmethod
    def get_last_search_time_by_job_search_title(job_search_title):
        conn = DatabaseAPI.get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT search_time
                FROM jobs
                WHERE original_search_titles::jsonb ? %s
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

    @staticmethod
    def add_search_title(url, job_search_title):
        conn = DatabaseAPI.get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                UPDATE jobs
                SET original_search_titles =
                    CASE
                        WHEN original_search_titles IS NULL THEN jsonb_build_array(%s)::json
                        WHEN NOT (original_search_titles::jsonb ? %s) THEN
                            (original_search_titles::jsonb || jsonb_build_array(%s))::json
                        ELSE original_search_titles
                    END
                WHERE url = %s
                """,
                (job_search_title, job_search_title, job_search_title, url),
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            cur.close()
            conn.close()





