# ============================================================
# DeepSeek-R1-Distill-Qwen-7B Generator
# Reasoning specialist
# Best for chain-of-thought heavy samples
# ============================================================

import re
from .base_generator import BaseGenerator


class DeepSeekGenerator(BaseGenerator):

    MODEL_ID   = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
    MODEL_NAME = "DeepSeek-R1-Distill-7B"

    # DeepSeek thinks longer before answering
    MAX_NEW_TOKENS    = 1500
    TEMPERATURE       = 0.6
    TOP_P             = 0.95
    REPETITION_PENALTY = 1.05

    def __init__(self):
        super().__init__()
        print(f"[INIT] DeepSeek generator ready")
        print(f"[INIT] Best for: Chain-of-thought, strategy analysis")
        print(f"[INIT] Target: pmf_analysis, pivot_analysis, pricing")

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = None,
        temperature: float = None,
    ):
        """
        Override generate to strip DeepSeek thinking tags.
        DeepSeek-R1 wraps reasoning in <think>...</think>
        We extract only the final answer.
        """
        raw = super().generate(prompt, max_new_tokens, temperature)

        if raw is None:
            return None

        # Remove <think>...</think> blocks
        # Keep only the final structured answer
        cleaned = re.sub(
            r"<think>.*?</think>",
            "",
            raw,
            flags=re.DOTALL
        ).strip()

        # If nothing left after removing think blocks
        # return the full output
        if not cleaned:
            return raw

        return cleaned