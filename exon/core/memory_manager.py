"""
Memory Manager - Coordinates Redis (working) and PostgreSQL (long-term)
"""

import redis
import psycopg2
import os
import json
from typing import List, Dict, Optional
from datetime import datetime


class MemoryManager:
    def __init__(self, exon_id: str):
        self.exon_id = exon_id
        self.redis_client = redis.Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", 6379)),
            decode_responses=True
        )
        
        # PostgreSQL connection
        self.pg_conn = psycopg2.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            port=os.environ.get("DB_PORT", "5432"),
            dbname=os.environ.get("DB_NAME", "futureex"),
            user=os.environ.get("DB_USER", "futureex"),
            password=os.environ.get("DB_PASSWORD", "futureex123")
        )
    
    def store(self, user_message: str, ai_response: str, session_id: Optional[str], emotion: dict):
        """Store conversation in both Redis (recent) and PostgreSQL (permanent)"""
    
        memory_entry = {
            "user": user_message,
            "assistant": ai_response,
            "emotion": emotion.get("primary", "neutral"),
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id
        }
    
        # Store in Redis (working memory)
        redis_key = f"{self.exon_id}:memory:recent"
        self.redis_client.lpush(redis_key, json.dumps(memory_entry))
        self.redis_client.ltrim(redis_key, 0, 49)
        
        # Store in PostgreSQL (long-term) - use exon_str_id
        try:
            cursor = self.pg_conn.cursor()
            cursor.execute("""
                INSERT INTO exon_memories (exon_id, memory_type, content, emotion_at_time, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                self.exon_id,  # Now string "EXN-001"
                "conversation",
                json.dumps(memory_entry),
                emotion.get("primary"),
                datetime.now()
            ))
            self.pg_conn.commit()
            cursor.close()
        except Exception as e:
            print(f"[MEMORY] PG store error: {e}")
            # Rollback on error
            self.pg_conn.rollback()

    def recall(self, keyword: str, limit: int = 5) -> List[Dict]:
        """Recall relevant memories based on keyword"""
        memories = []
        
        # First try Redis (working memory)
        redis_memories = self.redis_client.lrange(f"{self.exon_id}:memory:recent", 0, limit - 1)
        for mem in redis_memories:
            try:
                memories.append(json.loads(mem))
            except:
                pass
        
        # Then try PostgreSQL if more needed
        if len(memories) < limit:
            try:
                cursor = self.pg_conn.cursor()
                cursor.execute("""
                    SELECT content FROM exon_memories 
                    WHERE exon_id = %s AND content::text LIKE %s
                    ORDER BY created_at DESC LIMIT %s
                """, (self.exon_id, f"%{keyword}%", limit - len(memories)))
                
                for row in cursor.fetchall():
                    memories.append(json.loads(row[0]))
                cursor.close()
            except Exception as e:
                print(f"[MEMORY] PG recall error: {e}")
                self.pg_conn.rollback()
    
        return memories
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict]:
        """Get recent memories from working memory"""
        memories = []
        redis_memories = self.redis_client.lrange(f"{self.exon_id}:memory:recent", 0, limit - 1)
        for mem in redis_memories:
            try:
                memories.append(json.loads(mem))
            except:
                pass
        return memories
    
    def get_memory_count(self) -> int:
        """Get total memory count"""
        return self.redis_client.llen(f"{self.exon_id}:memory:recent")
    
    def clear_working_memory(self):
        """Clear working memory"""
        self.redis_client.delete(f"{self.exon_id}:memory:recent")