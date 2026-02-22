import asyncio
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def run_migrations():
    print("[*] Initializing Rant AI Database Schema...")
    
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "cyberrant")

    try:
        # Connect to default postgres to create the DB if it doesn't exist
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database="postgres"
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
        exists = cur.fetchone()
        if not exists:
            print(f"[+] Creating database: {DB_NAME}")
            cur.execute(f"CREATE DATABASE {DB_NAME}")
        else:
            print(f"[*] Database {DB_NAME} already exists.")
        
        cur.close()
        conn.close()

        # Connect to the target DB to run the schema
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cur = conn.cursor()
        
        schema_path = os.path.join(os.path.dirname(__file__), "community_intel_schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, "r") as f:
                schema_sql = f.read()
                print("[+] Executing schema migration...")
                cur.execute(schema_sql)
                conn.commit()
                print("[!] Database schema is now UP-TO-DATE.")
        else:
            print(f"[!] Migration file not found at {schema_path}")
            
        cur.close()
        conn.close()

    except Exception as e:
        print(f"[!] Database setup failed: {e}")
        print("[*] Ensure PostgreSQL is running and credentials in .env are correct.")

if __name__ == "__main__":
    run_migrations()
