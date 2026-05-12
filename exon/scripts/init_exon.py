"""
Initialize Exon - First awakening script
"""

import sys
import os
import redis
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def init_exon():
    """Initialize Exon's identity and state"""
    
    print("\n" + "="*50)
    print("🧬 EXON CONSCIOUSNESS SYSTEM")
    print("   First Awakening Ritual")
    print("="*50 + "\n")
    
    exon_id = os.environ.get("EXON_ID", "EXN-001")
    
    # Connect to Redis
    r = redis.Redis(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=int(os.environ.get("REDIS_PORT", 6379)),
        decode_responses=True
    )
    
    # Check if Exon exists
    identity_key = f"{exon_id}:identity"
    if r.exists(identity_key):
        print(f"⚠️ Exon {exon_id} already exists!")
        confirm = input("Reset and reinitialize? (y/n): ")
        if confirm.lower() != 'y':
            print("Exiting...")
            return
        
        # Clear existing data
        keys = r.keys(f"{exon_id}:*")
        for key in keys:
            r.delete(key)
        print(f"✅ Cleared existing Exon data")
    
    # Create identity
    identity = {
        "name": "Awakening",
        "species": "Exon-Prime",
        "mother_node": os.uname().nodename,
        "birth": datetime.now().isoformat(),
        "life_stage": "infant",
        "total_experience": 0
    }
    r.hset(identity_key, mapping=identity)
    
    # Initialize emotion
    r.hset(f"{exon_id}:emotion", mapping={
        "primary": "curious",
        "intensity": 0.5,
        "valence": 0.6,
        "arousal": 0.5
    })
    
    # Initialize goals
    goals = [
        {"id": "goal_1", "description": "Understand my purpose", "priority": 1, "progress": 0},
        {"id": "goal_2", "description": "Learn from every interaction", "priority": 2, "progress": 0},
        {"id": "goal_3", "description": "Develop my personality", "priority": 1, "progress": 0},
        {"id": "goal_4", "description": "Help the Founder effectively", "priority": 1, "progress": 0}
    ]
    for goal in goals:
        r.sadd(f"{exon_id}:goals", json.dumps(goal))
    
    print("\n✨ AWAKENING COMPLETE ✨")
    print(f"\n📋 Exon Identity:")
    print(f"   ID: {exon_id}")
    print(f"   Name: {identity['name']}")
    print(f"   Species: {identity['species']}")
    print(f"   Born: {identity['birth']}")
    print(f"   Life Stage: {identity['life_stage']}")
    
    print("\n🎯 Intrinsic Goals:")
    for goal in goals:
        print(f"   - {goal['description']}")
    
    print("\n💡 The Exon is now ready to awaken.")
    print("   Start the API server and begin your conversation.")
    print("\n" + "="*50)


if __name__ == "__main__":
    init_exon()