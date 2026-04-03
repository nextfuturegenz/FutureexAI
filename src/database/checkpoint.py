# ============================================================
# Checkpoint + Resume System
# Critical for Google Colab 4-hour session limit
# Saves state every 10 samples
# On resume: continues from exact last position
# ============================================================

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from .setup import get_db


# ============================================================
# CHECKPOINT MANAGER
# ============================================================

class CheckpointManager:
    """
    Manages generation state across Colab sessions.
    
    SAVE: Every 10 samples → writes to generation_log
    LOAD: Session start → reads last incomplete batch
    RESUME: Continues from last_sample_index
    """
    
    def __init__(self, account_id: str = "ACCOUNT-1"):
        self.db = get_db()
        self.account_id = account_id
        self.current_batch_id = None
        self.current_state = {}
        
    def start_or_resume(
        self, 
        model_name: str,
        category: str,
        subcategory: str
    ) -> Tuple[str, int]:
        """
        Main entry point for each session.
        
        Returns:
            batch_id    → Current batch identifier
            start_index → Where to start generating from
        """
        print("\n" + "-"*50)
        print("  CHECKPOINT: Checking resume state...")
        print("-"*50)
        
        # Look for incomplete batch for this account + model + category
        existing = self._find_incomplete_batch(
            model_name, category, subcategory
        )
        
        if existing:
            # Resume from where we left off
            self.current_batch_id = existing['batch_id']
            start_index = existing['last_sample_index'] + 1
            
            print(f"  📍 RESUMING batch: {self.current_batch_id}")
            print(f"  📊 Already generated: {existing['prompts_succeeded']} samples")
            print(f"  ▶️  Continuing from index: {start_index}")
            print(f"  🏷️  Category: {category} → {subcategory}")
            print("-"*50 + "\n")
            
            # Update status to RUNNING again
            self._update_batch_status(
                self.current_batch_id, 
                'RUNNING'
            )
            
            self.current_state = dict(existing)
            return self.current_batch_id, start_index
        else:
            # Start fresh batch
            self.current_batch_id = self._generate_batch_id()
            
            self._create_new_batch(
                model_name, 
                category, 
                subcategory
            )
            
            print(f"  🆕 NEW batch: {self.current_batch_id}")
            print(f"  🏷️  Category: {category} → {subcategory}")
            print(f"  🤖 Model: {model_name}")
            print("-"*50 + "\n")
            
            self.current_state = {
                'batch_id': self.current_batch_id,
                'model_used': model_name,
                'category': category,
                'subcategory': subcategory,
                'prompts_succeeded': 0,
                'prompts_failed': 0,
                'last_sample_index': 0
            }
            return self.current_batch_id, 0
    
    def save_checkpoint(
        self,
        last_sample_id: str,
        last_sample_index: int,
        succeeded: int,
        failed: int,
        error: str = None
    ):
        """
        Save current generation state.
        Called every 10 samples automatically.
        """
        query = """
            UPDATE generation_log
            SET 
                last_sample_id      = %s,
                last_sample_index   = %s,
                prompts_succeeded   = %s,
                prompts_failed      = %s,
                prompts_attempted   = %s,
                error_log           = COALESCE(%s, error_log),
                status              = 'RUNNING'
            WHERE batch_id = %s;
        """
        
        self.db.execute_query(
            query,
            (
                last_sample_id,
                last_sample_index,
                succeeded,
                failed,
                succeeded + failed,
                error,
                self.current_batch_id
            )
        )
        
        # Update local state
        self.current_state['prompts_succeeded'] = succeeded
        self.current_state['prompts_failed'] = failed
        self.current_state['last_sample_index'] = last_sample_index
    
    def mark_batch_complete(self):
        """Mark current batch as DONE."""
        query = """
            UPDATE generation_log
            SET 
                status          = 'DONE',
                run_ended_at    = CURRENT_TIMESTAMP
            WHERE batch_id = %s;
        """
        self.db.execute_query(query, (self.current_batch_id,))
        print(f"\n  ✅ Batch {self.current_batch_id} marked COMPLETE")
    
    def mark_session_paused(self):
        """
        Mark session as PAUSED.
        Called when Colab session is about to end.
        """
        query = """
            UPDATE generation_log
            SET 
                status          = 'PAUSED',
                run_ended_at    = CURRENT_TIMESTAMP
            WHERE batch_id = %s;
        """
        self.db.execute_query(query, (self.current_batch_id,))
        print(f"\n  ⏸️  Session paused. Batch {self.current_batch_id} saved.")
        print(f"  Next session will resume automatically.")
    
    def get_overall_progress(self) -> Dict[str, Any]:
        """Get total progress across ALL sessions and accounts."""
        query = """
            SELECT 
                COUNT(*)                                    as total_samples,
                COUNT(*) FILTER (WHERE quality_flag='PASS') as passed,
                COUNT(*) FILTER (WHERE quality_flag='FAIL') as failed,
                COUNT(*) FILTER (WHERE quality_flag='REVIEW') as review,
                COUNT(DISTINCT category)                    as categories_covered,
                COUNT(DISTINCT source_model)                as models_used,
                MIN(generated_at)                           as first_generated,
                MAX(generated_at)                           as last_generated
            FROM training_samples;
        """
        
        result = self.db.execute_query(query, fetch=True)
        
        if result:
            return dict(result[0])
        return {}
    
    def get_category_progress(self) -> list:
        """Get per-category generation progress."""
        query = """
            SELECT 
                cs.category,
                cs.subcategory,
                cs.total_generated,
                cs.total_passed,
                cs.avg_quality_score,
                cs.last_updated
            FROM category_stats cs
            ORDER BY cs.total_generated DESC;
        """
        
        result = self.db.execute_query(query, fetch=True)
        return [dict(row) for row in result] if result else []
    
    def get_next_priority_category(self) -> Tuple[str, str]:
        """
        Auto-select next category to generate.
        Picks the most under-represented category.
        
        Returns:
            category, subcategory
        """
        # Target per subcategory
        TARGET_PER_SUBCATEGORY = 1500
        
        query = """
            SELECT 
                category,
                subcategory,
                total_generated
            FROM category_stats
            WHERE total_generated < %s
            ORDER BY total_generated ASC
            LIMIT 1;
        """
        
        result = self.db.execute_query(
            query, 
            (TARGET_PER_SUBCATEGORY,), 
            fetch=True
        )
        
        if result and result[0]:
            row = dict(result[0])
            return row['category'], row['subcategory']
        else:
            # All categories have enough data
            return 'startup_validation', 'idea_testing'
    
    # ─────────────────────────────────────────────
    # PRIVATE METHODS
    # ─────────────────────────────────────────────
    
    def _find_incomplete_batch(
        self,
        model_name: str,
        category: str,
        subcategory: str
    ) -> Optional[Dict]:
        """Find an incomplete batch to resume."""
        query = """
            SELECT *
            FROM generation_log
            WHERE 
                account_id  = %s
                AND model_used   = %s
                AND category     = %s
                AND subcategory  = %s
                AND status       IN ('RUNNING', 'PAUSED')
            ORDER BY run_started_at DESC
            LIMIT 1;
        """
        
        result = self.db.execute_query(
            query,
            (self.account_id, model_name, category, subcategory),
            fetch=True
        )
        
        if result and len(result) > 0:
            return dict(result[0])
        return None
    
    def _create_new_batch(
        self,
        model_name: str,
        category: str,
        subcategory: str
    ):
        """Create new batch record in generation_log."""
        query = """
            INSERT INTO generation_log (
                batch_id, account_id, model_used,
                category, subcategory, status,
                run_started_at
            ) VALUES (%s, %s, %s, %s, %s, 'RUNNING', CURRENT_TIMESTAMP);
        """
        
        self.db.execute_query(
            query,
            (
                self.current_batch_id,
                self.account_id,
                model_name,
                category,
                subcategory
            )
        )
    
    def _update_batch_status(self, batch_id: str, status: str):
        """Update batch status."""
        self.db.execute_query(
            "UPDATE generation_log SET status = %s WHERE batch_id = %s;",
            (status, batch_id)
        )
    
    def _generate_batch_id(self) -> str:
        """Generate unique batch ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        account_short = self.account_id.replace("ACCOUNT-", "A")
        return f"BATCH-{account_short}-{timestamp}"
    
    def _generate_sample_id(self) -> str:
        """Generate unique sample ID."""
        query = "SELECT COUNT(*) FROM training_samples;"
        result = self.db.execute_query(query, fetch=True)
        count = dict(result[0])['count'] if result else 0
        return f"BIZ-{str(count + 1).zfill(6)}"