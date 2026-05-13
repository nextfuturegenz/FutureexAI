"""
File: /opt/futureex/exon/scripts/health_check.py
Author: Ashish Pal
Purpose: Validate all Exon dependencies (PostgreSQL, Redis, Ollama).
"""

import sys
import os
import redis
import psycopg2
import requests

def check_health():
    print("\n🏥 EXON HEALTH CHECK\n")
    issues = []

    # Redis
    try:
        r = redis.Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", 6379)),
            decode_responses=True
        )
        r.ping()
        print("✅ Redis: Connected")
    except Exception as e:
        print(f"❌ Redis: {e}")
        issues.append("Redis connection failed")

    # PostgreSQL
    try:
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            port=os.environ.get("DB_PORT", "5432"),
            dbname=os.environ.get("DB_NAME", "futureex"),
            user=os.environ.get("DB_USER", "futureex"),
            password=os.environ.get("DB_PASSWORD", "futureex123")
        )
        conn.close()
        print("✅ PostgreSQL: Connected")
    except Exception as e:
        print(f"❌ PostgreSQL: {e}")
        issues.append("PostgreSQL connection failed")

    # Ollama
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        if resp.status_code == 200:
            print("✅ Ollama: Running")
        else:
            print(f"❌ Ollama: Status {resp.status_code}")
            issues.append("Ollama not responding")
    except Exception as e:
        print(f"❌ Ollama: {e}")
        issues.append("Ollama connection failed")

    print("\n" + "="*30)
    if issues:
        print(f"⚠️ Issues found: {len(issues)}")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ All systems healthy!")
    print("="*30 + "\n")
    return len(issues) == 0

if __name__ == "__main__":
    sys.exit(0 if check_health() else 1)