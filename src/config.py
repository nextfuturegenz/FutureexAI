# ============================================================
# Central Configuration
# All settings in one place
# Never put credentials here
# ============================================================

import os


class Config:
    """
    Central config for entire pipeline.
    All values can be overridden via environment variables.
    """

    # ── Database
    DB_HOST     = os.environ.get("DB_HOST", "34.131.80.243")
    DB_PORT     = int(os.environ.get("DB_PORT", "5432"))
    DB_NAME     = os.environ.get("DB_NAME", "gotrackpro")
    DB_USER     = os.environ.get("DB_USER", "")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_SSLMODE  = os.environ.get("DB_SSLMODE", "require")

    # ── Models
    MODELS = {
        "qwen": {
            "model_id":   "Qwen/Qwen2.5-7B-Instruct",
            "max_tokens": 1200,
            "temperature": 0.7,
        },
        "deepseek": {
            "model_id":   "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
            "max_tokens": 1500,
            "temperature": 0.6,
        },
        "phi": {
            "model_id":   "microsoft/Phi-3.5-mini-instruct",
            "max_tokens": 900,
            "temperature": 0.75,
        },
    }

    # ── Generation
    CHECKPOINT_EVERY    = 10     # Save checkpoint every N samples
    CRITIQUE_RATE       = 50     # Run critique on 50% of samples
    MAX_SESSION_SAMPLES = 200    # Safe limit per 4hr Colab session
    CATEGORY_BATCH_SIZE = 50     # Max per category before rotating

    # ── Quality Thresholds
    PASS_THRESHOLD   = 7.0
    REVIEW_THRESHOLD = 4.0

    # ── Dataset Targets
    TOTAL_TARGET = 50000

    # ── Account IDs
    # Change this per Colab account for parallel generation
    ACCOUNT_ID = os.environ.get("ACCOUNT_ID", "ACCOUNT-1")

    @classmethod
    def validate(cls) -> bool:
        """Check all required config is set."""
        missing = []
        if not cls.DB_USER:
            missing.append("DB_USER")
        if not cls.DB_PASSWORD:
            missing.append("DB_PASSWORD")

        if missing:
            print(f"[CONFIG] ❌ Missing: {missing}")
            print("[CONFIG] Set these in Colab Secrets")
            return False

        print("[CONFIG] ✅ All configuration valid")
        return True

    @classmethod
    def print_summary(cls):
        """Print config summary without exposing credentials."""
        print("\n  CONFIG SUMMARY:")
        print(f"  DB Host      : {cls.DB_HOST}")
        print(f"  DB Name      : {cls.DB_NAME}")
        print(f"  DB User      : {cls.DB_USER[:3]}***")
        print(f"  SSL Mode     : {cls.DB_SSLMODE}")
        print(f"  Account ID   : {cls.ACCOUNT_ID}")
        print(
            f"  Checkpoint   : Every {cls.CHECKPOINT_EVERY} samples"
        )
        print(
            f"  Critique Rate: {cls.CRITIQUE_RATE}% of samples"
        )
        print(
            f"  Session Max  : {cls.MAX_SESSION_SAMPLES} samples"
        )