# ============================================================
# Main Pipeline Orchestrator
# Controls the full generation loop
# Handles model switching, checkpoints, and category rotation
# ============================================================

import time
from datetime import datetime
from typing import Optional, Dict, Any

from ..generators.qwen_generator     import QwenGenerator
from ..generators.deepseek_generator import DeepSeekGenerator
from ..generators.phi_generator      import PhiGenerator
from ..pipeline.quality_scorer       import QualityScorer
from ..pipeline.self_critique        import SelfCritiqueLoop
from ..pipeline.metadata_tagger      import MetadataTagger
from ..database.checkpoint           import CheckpointManager
from ..database.writer               import DataWriter
from ..prompts.templates             import PromptSelector
from ..prompts.categories            import (
    get_categories_for_model,
    get_next_underfilled_category
)
from ..utils.dashboard               import Dashboard


# ============================================================
# MODEL REGISTRY
# ============================================================

MODEL_REGISTRY = {
    "qwen":     QwenGenerator,
    "deepseek": DeepSeekGenerator,
    "phi":      PhiGenerator,
}


# ============================================================
# ORCHESTRATOR
# ============================================================

class GenerationOrchestrator:
    """
    Controls the complete data generation pipeline.

    Usage:
        orchestrator = GenerationOrchestrator(
            model_name="qwen",
            account_id="ACCOUNT-1"
        )
        orchestrator.run(max_samples=200)
    """

    # How often to checkpoint (in samples)
    CHECKPOINT_EVERY = 10

    # Run self-critique on this % of samples
    # 100 = every sample (slower but better quality)
    # 50  = every other sample (faster)
    CRITIQUE_RATE = 50

    def __init__(
        self,
        model_name: str,
        account_id: str = "ACCOUNT-1",
    ):
        if model_name not in MODEL_REGISTRY:
            raise ValueError(
                f"Unknown model: {model_name}. "
                f"Choose from: {list(MODEL_REGISTRY.keys())}"
            )

        self.model_name  = model_name
        self.account_id  = account_id

        # Initialize components
        self.generator   = MODEL_REGISTRY[model_name]()
        self.scorer      = QualityScorer()
        self.tagger      = MetadataTagger()
        self.selector    = PromptSelector()
        self.checkpoint  = CheckpointManager(account_id)
        self.writer      = DataWriter(self.checkpoint)
        self.dashboard   = Dashboard()
        self.critique    = None  # Initialized after model loads

        # Session tracking
        self._session_start     = datetime.now()
        self._samples_this_run  = 0
        self._global_counter    = 0

    # ─────────────────────────────────────────────
    # MAIN ENTRY POINT
    # ─────────────────────────────────────────────

    def run(self, max_samples: int = 200):
        """
        Run generation pipeline for this session.

        Args:
            max_samples: How many to generate this session
                         Default 200 = safe for 4hr Colab session
        """
        print("\n" + "="*60)
        print("  BUSINESS AI DATA GENERATOR")
        print(f"  Model    : {self.model_name.upper()}")
        print(f"  Account  : {self.account_id}")
        print(f"  Target   : {max_samples} samples this session")
        print(f"  Started  : {self._session_start.strftime('%H:%M:%S')}")
        print("="*60)

        try:
            # Step 1: Load model
            if not self._load_model():
                print("[ORCH] ❌ Model loading failed. Stopping.")
                return

            # Step 2: Initialize critique loop
            self.critique = SelfCritiqueLoop(self.generator)

            # Step 3: Get global counter from DB
            self._global_counter = self._get_global_count()

            # Step 4: Get categories for this model
            categories = get_categories_for_model(self.model_name)

            if not categories:
                print(f"[ORCH] ❌ No categories for {self.model_name}")
                return

            print(f"\n[ORCH] Categories for {self.model_name}: "
                  f"{len(categories)}")

            # Step 5: Main generation loop
            self._generation_loop(categories, max_samples)

        except KeyboardInterrupt:
            print("\n\n[ORCH] ⚠️  Interrupted by user")
            print("[ORCH] Saving checkpoint before exit...")

        except Exception as e:
            print(f"\n[ORCH] ❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()

        finally:
            # Always save state on exit
            self._shutdown()

    # ─────────────────────────────────────────────
    # GENERATION LOOP
    # ─────────────────────────────────────────────

    def _generation_loop(
        self,
        categories: list,
        max_samples: int
    ):
        """Core generation loop with checkpoint resume."""

        # Get current counts from DB
        current_counts = self._get_current_counts()

        samples_generated = 0

        while samples_generated < max_samples:

            # Find next underfilled category
            next_cat = get_next_underfilled_category(
                current_counts,
                model_filter=self.model_name
            )

            if next_cat is None:
                print("\n[ORCH] 🎉 All category targets met!")
                break

            category   = next_cat["category"]
            subcategory = next_cat["subcategory"]
            remaining  = next_cat["remaining"]

            print(
                f"\n[ORCH] 📂 Category: {category} → {subcategory}"
                f" | Remaining: {remaining:,}"
                f" | {next_cat['completion_pct']}% done"
            )

            # Start or resume batch for this category
            batch_id, start_idx = self.checkpoint.start_or_resume(
                model_name=self.model_name,
                category=category,
                subcategory=subcategory
            )

            # How many to generate for this category in this run
            # Don't exceed remaining or max_samples budget
            batch_budget = min(
                remaining,
                max_samples - samples_generated,
                50   # Max 50 per category before rotating
            )

            print(
                f"[ORCH] Generating {batch_budget} samples "
                f"for this category..."
            )

            # Generate samples for this category
            cat_generated = self._generate_for_category(
                category=category,
                subcategory=subcategory,
                batch_id=batch_id,
                count=batch_budget,
                start_idx=start_idx
            )

            samples_generated += cat_generated

            # Update current_counts
            key = f"{category}_{subcategory}"
            current_counts[key] = (
                current_counts.get(key, 0) + cat_generated
            )

            # Show dashboard every 50 samples
            if samples_generated % 50 == 0:
                self.dashboard.show(
                    self.checkpoint,
                    self.writer,
                    self._session_start
                )

        print(f"\n[ORCH] Session complete: {samples_generated} samples")

    def _generate_for_category(
        self,
        category: str,
        subcategory: str,
        batch_id: str,
        count: int,
        start_idx: int
    ) -> int:
        """
        Generate `count` samples for a specific category.
        Returns number of successfully generated samples.
        """
        generated = 0

        for i in range(count):
            current_idx = start_idx + i

            try:
                # ── Get prompt
                prompt, metadata = self.selector.get_structured_prompt(
                    category=category,
                    subcategory=subcategory
                )

                # The instruction is the prompt itself
                # (cleaned of system context)
                instruction = self._extract_instruction(prompt)

                # ── Generate initial output
                print(
                    f"  [{generated + 1}/{count}] Generating...",
                    end="", flush=True
                )

                t_start = time.time()
                raw_output = self.generator.generate(prompt)

                if not raw_output:
                    print(" ❌ Generation failed")
                    continue

                t_elapsed = round(time.time() - t_start, 1)

                # ── Parse sections
                sections = self.generator.parse_sections(raw_output)

                # ── Optionally run self-critique
                critique_result = {"critique_output": None,
                                   "improved_output": None}

                if (i % (100 // self.CRITIQUE_RATE) == 0):
                    final_output = sections.get(
                        "problem_breakdown", ""
                    ) + raw_output

                    critique_result = self.critique.run(
                        instruction=instruction,
                        initial_output=raw_output,
                        metadata=metadata
                    )

                    # Use improved output if available
                    if critique_result.get("improved_output"):
                        improved_sections = self.generator.parse_sections(
                            critique_result["improved_output"]
                        )
                        # Merge improved sections
                        for k, v in improved_sections.items():
                            if v:
                                sections[k] = v

                # ── Build sample dict
                self._global_counter += 1
                sample_id = self.generator.generate_sample_id(
                    self._global_counter
                )

                raw_sample = {
                    "sample_id":    sample_id,
                    "batch_id":     batch_id,
                    "source_model": self.model_name,
                    "instruction":  instruction,
                    **sections,
                    "critique_output": critique_result.get(
                        "critique_output"
                    ),
                    "improved_output": critique_result.get(
                        "improved_output"
                    ),
                }

                # ── Score quality
                full_out = (
                    sections.get("problem_breakdown", "") + " " +
                    sections.get("strategic_options", "") + " " +
                    sections.get("recommended_decision", "") + " " +
                    sections.get("execution_plan", "") + " " +
                    sections.get("risks_and_mitigation", "")
                )

                raw_sample["full_output"] = full_out
                raw_sample["word_count"]  = len(full_out.split())

                score, flag, breakdown = self.scorer.score(raw_sample)

                # ── Tag metadata
                tagged_sample = self.tagger.tag(
                    raw_sample=raw_sample,
                    prompt_metadata=metadata,
                    quality_score=score,
                    quality_flag=flag,
                    quality_breakdown=breakdown
                )

                # ── Save to DB
                saved = self.writer.save_sample(tagged_sample)

                if saved:
                    generated += 1
                    status_icon = (
                        "✅" if flag == "PASS"
                        else "⚠️" if flag == "REVIEW"
                        else "❌"
                    )
                    print(
                        f" {status_icon} "
                        f"Score:{score} | "
                        f"Words:{raw_sample['word_count']} | "
                        f"{t_elapsed}s"
                    )
                else:
                    print(" 💾 DB write failed")

            except Exception as e:
                print(f" ❌ Error: {e}")
                continue

        return generated

    # ─────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────

    def _load_model(self) -> bool:
        """Load model with memory check."""
        try:
            import torch
            if torch.cuda.is_available():
                free_gb = (
                    torch.cuda.get_device_properties(0).total_memory
                    - torch.cuda.memory_allocated()
                ) / 1024**3
                print(f"[ORCH] Available VRAM: {free_gb:.1f}GB")

                if free_gb < 5.0:
                    print("[ORCH] ⚠️  Low VRAM. Clearing cache...")
                    import gc
                    gc.collect()
                    torch.cuda.empty_cache()

            return self.generator.load()

        except Exception as e:
            print(f"[ORCH] Load error: {e}")
            return False

    def _get_global_count(self) -> int:
        """Get total samples in DB for ID generation."""
        from ..database.setup import get_db
        db = get_db()
        result = db.execute_query(
            "SELECT COUNT(*) FROM training_samples;",
            fetch=True
        )
        if result:
            return dict(result[0]).get("count", 0)
        return 0

    def _get_current_counts(self) -> Dict[str, int]:
        """Get current sample counts per subcategory."""
        from ..database.setup import get_db
        db = get_db()
        result = db.execute_query(
            """
            SELECT category, subcategory, total_generated
            FROM category_stats;
            """,
            fetch=True
        )
        if result:
            return {
                f"{r['category']}_{r['subcategory']}":
                r['total_generated']
                for r in result
            }
        return {}

    def _extract_instruction(self, prompt: str) -> str:
        """
        Extract clean instruction from full prompt.
        Removes system context, keeps the core question.
        """
        # Find the last Question: marker
        if "Question:" in prompt:
            idx = prompt.rfind("Question:")
            return prompt[idx:].strip()

        # Find the last ? in prompt
        lines = prompt.strip().split("\n")
        for line in reversed(lines):
            if "?" in line and len(line) > 20:
                return line.strip()

        # Fallback: last 200 chars
        return prompt[-200:].strip()

    def _shutdown(self):
        """Clean shutdown on session end."""
        print("\n[ORCH] Shutting down cleanly...")

        # Mark session as paused
        if self.checkpoint.current_batch_id:
            self.checkpoint.mark_session_paused()

        # Show final stats
        self.dashboard.show(
            self.checkpoint,
            self.writer,
            self._session_start
        )

        # Unload model
        self.generator.unload()

        print("[ORCH] ✅ Shutdown complete. Data safe in GCP PostgreSQL.")