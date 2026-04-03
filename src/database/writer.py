# ============================================================
# Database Writer
# Saves generated samples + updates all tracking tables
# ============================================================

from datetime import datetime
from typing import Dict, Any, Optional
from .setup import get_db
from .checkpoint import CheckpointManager


class DataWriter:
    """
    Handles all database write operations.
    Every generated sample goes through this class.
    """
    
    def __init__(self, checkpoint_manager: CheckpointManager):
        self.db = get_db()
        self.checkpoint = checkpoint_manager
        self._session_count = 0
        self._session_passed = 0
        self._session_failed = 0
        self.CHECKPOINT_INTERVAL = 10  # Save every 10 samples
        
    def save_sample(self, sample: Dict[str, Any]) -> bool:
        """
        Save one generated sample to database.
        Auto-checkpoints every 10 saves.
        
        Args:
            sample: Complete sample dictionary
            
        Returns:
            True if saved successfully
        """
        query = """
            INSERT INTO training_samples (
                sample_id, batch_id, sprint, source_model,
                category, subcategory, industry, geography,
                business_stage, instruction,
                problem_breakdown, strategic_options,
                recommended_decision, execution_plan,
                risks_and_mitigation, full_output,
                word_count, has_india_context,
                quality_score, quality_flag,
                critique_output, improved_output,
                generated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, CURRENT_TIMESTAMP
            )
            ON CONFLICT (sample_id) DO NOTHING;
        """
        
        result = self.db.execute_query(
            query,
            (
                sample.get('sample_id'),
                sample.get('batch_id'),
                sample.get('sprint', 'SPRINT-1'),
                sample.get('source_model'),
                sample.get('category'),
                sample.get('subcategory'),
                sample.get('industry'),
                sample.get('geography'),
                sample.get('business_stage'),
                sample.get('instruction'),
                sample.get('problem_breakdown'),
                sample.get('strategic_options'),
                sample.get('recommended_decision'),
                sample.get('execution_plan'),
                sample.get('risks_and_mitigation'),
                sample.get('full_output'),
                sample.get('word_count', 0),
                sample.get('has_india_context', False),
                sample.get('quality_score', 0.0),
                sample.get('quality_flag', 'PENDING'),
                sample.get('critique_output'),
                sample.get('improved_output'),
            )
        )
        
        if result is not None:
            self._session_count += 1
            
            # Track pass/fail counts
            if sample.get('quality_flag') == 'PASS':
                self._session_passed += 1
            elif sample.get('quality_flag') == 'FAIL':
                self._session_failed += 1
            
            # Update category stats
            self._update_category_stats(sample)
            
            # Auto-checkpoint every N samples
            if self._session_count % self.CHECKPOINT_INTERVAL == 0:
                self.checkpoint.save_checkpoint(
                    last_sample_id=sample.get('sample_id'),
                    last_sample_index=self._session_count,
                    succeeded=self._session_passed,
                    failed=self._session_failed
                )
                print(f"  💾 Checkpoint saved @ {self._session_count} samples")
            
            return True
        return False
    
    def _update_category_stats(self, sample: Dict[str, Any]):
        """Update running stats for this category."""
        flag = sample.get('quality_flag', 'PENDING')
        score = sample.get('quality_score', 0.0)
        
        query = """
            INSERT INTO category_stats (
                category, subcategory,
                total_generated, total_passed, 
                total_failed, total_review,
                avg_quality_score, last_updated
            )
            VALUES (%s, %s, 1,
                CASE WHEN %s = 'PASS' THEN 1 ELSE 0 END,
                CASE WHEN %s = 'FAIL' THEN 1 ELSE 0 END,
                CASE WHEN %s = 'REVIEW' THEN 1 ELSE 0 END,
                %s, CURRENT_TIMESTAMP
            )
            ON CONFLICT (category, subcategory) DO UPDATE SET
                total_generated  = category_stats.total_generated + 1,
                total_passed     = category_stats.total_passed + 
                    CASE WHEN %s = 'PASS' THEN 1 ELSE 0 END,
                total_failed     = category_stats.total_failed + 
                    CASE WHEN %s = 'FAIL' THEN 1 ELSE 0 END,
                total_review     = category_stats.total_review + 
                    CASE WHEN %s = 'REVIEW' THEN 1 ELSE 0 END,
                avg_quality_score = (
                    category_stats.avg_quality_score * 
                    category_stats.total_generated + %s
                ) / (category_stats.total_generated + 1),
                last_updated     = CURRENT_TIMESTAMP;
        """
        
        self.db.execute_query(
            query,
            (
                sample.get('category'),
                sample.get('subcategory'),
                flag, flag, flag, score,
                flag, flag, flag, score
            )
        )
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Return stats for current session."""
        return {
            'session_total':    self._session_count,
            'session_passed':   self._session_passed,
            'session_failed':   self._session_failed,
            'pass_rate':        (
                round(self._session_passed / self._session_count * 100, 1)
                if self._session_count > 0 else 0
            )
        }