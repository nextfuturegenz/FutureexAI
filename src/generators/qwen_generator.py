# ============================================================
# Qwen2.5-7B-Instruct Generator
# Primary teacher model
# Best for complex structured reasoning
# ============================================================

from .base_generator import BaseGenerator


class QwenGenerator(BaseGenerator):

    MODEL_ID   = "Qwen/Qwen2.5-7B-Instruct"
    MODEL_NAME = "Qwen2.5-7B-Instruct"

    # Qwen handles longer outputs well
    MAX_NEW_TOKENS    = 1200
    TEMPERATURE       = 0.7
    TOP_P             = 0.9
    REPETITION_PENALTY = 1.1

    def __init__(self):
        super().__init__()
        print(f"[INIT] Qwen generator ready")
        print(f"[INIT] Best for: Complex reasoning, structured outputs")
        print(f"[INIT] Target: startup_validation, gtm_strategy, pricing")