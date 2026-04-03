# ============================================================
# Phi-3.5-Mini-Instruct Generator
# High-volume bulk generator
# Best for simpler scenarios at speed
# ============================================================

from .base_generator import BaseGenerator


class PhiGenerator(BaseGenerator):

    MODEL_ID   = "microsoft/Phi-3.5-mini-instruct"
    MODEL_NAME = "Phi-3.5-Mini-Instruct"

    # Phi is faster with shorter outputs
    MAX_NEW_TOKENS    = 900
    TEMPERATURE       = 0.75
    TOP_P             = 0.9
    REPETITION_PENALTY = 1.15

    def __init__(self):
        super().__init__()
        print(f"[INIT] Phi generator ready")
        print(f"[INIT] Best for: High volume, simpler scenarios")
        print(f"[INIT] Target: customer_support, social_media, content")