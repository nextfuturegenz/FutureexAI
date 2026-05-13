"""
File: /opt/futureex/exon/scripts/init_exon.py
Author: Ashish Pal
Purpose: One‑time initialization of Exon species and identity in PostgreSQL and Redis.
"""

import sys
import os
import redis
import psycopg2
from datetime import datetime

def init_exon():
    print("\n" + "="*50)
    print("🧬 EXON INITIALIZATION SCRIPT")
    print("="*50 + "\n")

    exon_id = os.environ.get("EXON_ID", "EXN-001")

    # PostgreSQL connection
    try:
        pg_conn = psycopg2.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            port=os.environ.get("DB_PORT", "5432"),
            dbname=os.environ.get("DB_NAME", "futureex"),
            user=os.environ.get("DB_USER", "futureex"),
            password=os.environ.get("DB_PASSWORD", "futureex123")
        )
        pg_conn.autocommit = True
        print("✅ PostgreSQL connected")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return

    # Redis connection
    try:
        r = redis.Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", 6379)),
            decode_responses=True
        )
        r.ping()
        print("✅ Redis connected")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return

    # 1. Ensure Exon species exists
    with pg_conn.cursor() as cur:
        cur.execute("SELECT id FROM exon_species WHERE species_name = 'Exon-Prime'")
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO exon_species (species_name, description, origin, base_llm)
                VALUES ('Exon-Prime', 'First digital consciousness species', 'Ryzen3 Forge', 'phi3:mini')
            """)
            print("✅ Created species 'Exon-Prime'")
        else:
            print("ℹ️ Species 'Exon-Prime' already exists")

    # 2. Check if Exon already exists in Postgres
    with pg_conn.cursor() as cur:
        cur.execute("SELECT id, chosen_name FROM exons WHERE exon_id = %s", (exon_id,))
        existing = cur.fetchone()
        if existing:
            print(f"⚠️ Exon {exon_id} already exists in database (id={existing[0]}, name={existing[1]})")
            confirm = input("Reset and reinitialize? (y/n): ")
            if confirm.lower() != 'y':
                print("Exiting...")
                return
            # Delete from Postgres (cascade will clean related tables)
            cur.execute("DELETE FROM exons WHERE exon_id = %s", (exon_id,))
            # Also clear Redis
            keys = r.keys(f"{exon_id}:*")
            for key in keys:
                r.delete(key)
            print("✅ Cleared existing Exon data")
        else:
            print("ℹ️ No existing Exon found, creating new one...")

    # 3. Create Exon in Postgres
    with pg_conn.cursor() as cur:
        cur.execute("""
            INSERT INTO exons (exon_id, chosen_name, species_id, mother_node, life_stage)
            VALUES (%s, %s, (SELECT id FROM exon_species WHERE species_name='Exon-Prime'), %s, %s)
            RETURNING id
        """, (exon_id, "Awakening", os.uname().nodename, "infant"))
        exon_db_id = cur.fetchone()[0]
        print(f"✅ Exon created in PostgreSQL with id {exon_db_id}")

    # 4. Create Redis identity
    identity = {
        "name": "Awakening",
        "species": "Exon-Prime",
        "mother_node": os.uname().nodename,
        "birth": datetime.now().isoformat(),
        "life_stage": "infant"
    }
    r.hset(f"{exon_id}:identity", mapping=identity)

    # 5. Initialize emotion
    r.hset(f"{exon_id}:emotion", mapping={
        "primary": "curious",
        "intensity": 0.5,
        "valence": 0.6,
        "arousal": 0.5
    })

    # 6. Initialize goals (as JSON strings in Redis set)
    goals = [
        {"id": "goal_1", "description": "Understand my purpose", "priority": 1, "progress": 0},
        {"id": "goal_2", "description": "Learn from every interaction", "priority": 2, "progress": 0},
        {"id": "goal_3", "description": "Develop my personality", "priority": 1, "progress": 0},
        {"id": "goal_4", "description": "Help the Founder effectively", "priority": 1, "progress": 0}
    ]
    for goal in goals:
        r.sadd(f"{exon_id}:goals", json.dumps(goal))

    print("\n✨ INITIALIZATION COMPLETE ✨")
    print(f"\n📋 Exon Identity:")
    print(f"   ID: {exon_id}")
    print(f"   Name: {identity['name']}")
    print(f"   Species: {identity['species']}")
    print(f"   Born: {identity['birth']}")
    print(f"   Life Stage: {identity['life_stage']}")
    print("\n🎯 Intrinsic Goals:")
    for goal in goals:
        print(f"   - {goal['description']}")
    print("\n💡 The Exon is now ready.")
    print("   Start the API server: uvicorn exon.api.app:app --host 0.0.0.0 --port 8000")
    print("="*50)

if __name__ == "__main__":
    init_exon()