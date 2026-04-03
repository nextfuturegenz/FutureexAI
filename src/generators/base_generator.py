# ============================================================
# Base Generator
# Shared logic for all 3 models
# Handles 4-bit loading, memory cleanup, generation
# ============================================================

import gc
import re
import torch
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    GenerationConfig
)


class BaseGenerator:
    """
    Base class for all model generators.
    Handles loading, generation, and cleanup
    for Google Colab T4 (16GB VRAM).
    """

    # Override in subclass
    MODEL_ID   = ""
    MODEL_NAME = ""

    # Generation defaults
    MAX_NEW_TOKENS   = 1024
    TEMPERATURE      = 0.7
    TOP_P            = 0.9
    REPETITION_PENALTY = 1.1

    def __init__(self):
        self.model     = None
        self.tokenizer = None
        self.is_loaded = False
        self.device    = (
            "cuda" if torch.cuda.is_available() else "cpu"
        )

    # ─────────────────────────────────────────────
    # LOADING
    # ─────────────────────────────────────────────

    def load(self) -> bool:
        """
        Load model in 4-bit quantization.
        Optimized for T4 16GB VRAM.
        """
        print(f"\n[LOADER] Loading {self.MODEL_NAME}...")
        print(f"[LOADER] Device: {self.device}")

        if self.device == "cpu":
            print("[LOADER] ⚠️  No GPU detected. Generation will be slow.")

        try:
            # 4-bit quantization config
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )

            print(f"[LOADER] Downloading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.MODEL_ID,
                trust_remote_code=True,
                padding_side="left"
            )

            # Ensure pad token exists
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = (
                    self.tokenizer.eos_token
                )

            print(f"[LOADER] Downloading model weights (4-bit)...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.MODEL_ID,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True,
                torch_dtype=torch.float16,
            )

            self.model.eval()
            self.is_loaded = True

            # Report memory usage
            if torch.cuda.is_available():
                used_gb = (
                    torch.cuda.memory_allocated() / 1024**3
                )
                total_gb = (
                    torch.cuda.get_device_properties(0).total_memory
                    / 1024**3
                )
                print(
                    f"[LOADER] ✅ {self.MODEL_NAME} loaded"
                    f" | VRAM: {used_gb:.1f}GB / {total_gb:.1f}GB"
                )
            else:
                print(f"[LOADER] ✅ {self.MODEL_NAME} loaded on CPU")

            return True

        except Exception as e:
            print(f"[LOADER] ❌ Failed to load {self.MODEL_NAME}: {e}")
            self.is_loaded = False
            return False

    def unload(self):
        """
        Completely unload model from VRAM.
        Call before loading a different model.
        """
        if self.model:
            del self.model
            self.model = None

        if self.tokenizer:
            del self.tokenizer
            self.tokenizer = None

        self.is_loaded = False

        # Force garbage collection
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()

        print(f"[LOADER] 🧹 {self.MODEL_NAME} unloaded. VRAM cleared.")

    # ─────────────────────────────────────────────
    # GENERATION
    # ─────────────────────────────────────────────

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = None,
        temperature: float = None,
    ) -> Optional[str]:
        """
        Generate response for a single prompt.

        Returns:
            Generated text string or None on failure
        """
        if not self.is_loaded:
            print(f"[GEN] ❌ Model not loaded. Call load() first.")
            return None

        max_tokens = max_new_tokens or self.MAX_NEW_TOKENS
        temp       = temperature or self.TEMPERATURE

        try:
            # Format prompt using chat template
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a senior business strategist "
                        "specializing in Indian startups and markets. "
                        "Always respond with structured frameworks "
                        "and actionable advice."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            # Apply chat template
            formatted = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )

            # Tokenize
            inputs = self.tokenizer(
                formatted,
                return_tensors="pt",
                truncation=True,
                max_length=2048,
            ).to(self.device)

            input_length = inputs["input_ids"].shape[1]

            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temp,
                    top_p=self.TOP_P,
                    repetition_penalty=self.REPETITION_PENALTY,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )

            # Decode only the new tokens
            new_tokens = outputs[0][input_length:]
            response = self.tokenizer.decode(
                new_tokens,
                skip_special_tokens=True
            ).strip()

            return response if response else None

        except torch.cuda.OutOfMemoryError:
            print("[GEN] ❌ CUDA Out of Memory")
            print("[GEN] Clearing cache and skipping sample...")
            torch.cuda.empty_cache()
            gc.collect()
            return None

        except Exception as e:
            print(f"[GEN] ❌ Generation error: {e}")
            return None

    # ─────────────────────────────────────────────
    # OUTPUT PARSING
    # ─────────────────────────────────────────────

    def parse_sections(
        self,
        raw_output: str
    ) -> Dict[str, str]:
        """
        Parse 5-section structured output into dict.
        Handles slight variations in section headers.

        Returns dict with all 5 sections.
        """
        sections = {
            "problem_breakdown":    "",
            "strategic_options":    "",
            "recommended_decision": "",
            "execution_plan":       "",
            "risks_and_mitigation": ""
        }

        if not raw_output:
            return sections

        # Section header patterns
        # Handles bold markdown and variations
        patterns = {
            "problem_breakdown": [
                r"\*\*PROBLEM BREAKDOWN\*\*",
                r"PROBLEM BREAKDOWN",
                r"\*\*Problem Breakdown\*\*",
                r"## Problem Breakdown",
            ],
            "strategic_options": [
                r"\*\*STRATEGIC OPTIONS\*\*",
                r"STRATEGIC OPTIONS",
                r"\*\*Strategic Options\*\*",
                r"## Strategic Options",
            ],
            "recommended_decision": [
                r"\*\*RECOMMENDED DECISION\*\*",
                r"RECOMMENDED DECISION",
                r"\*\*Recommended Decision\*\*",
                r"## Recommended Decision",
            ],
            "execution_plan": [
                r"\*\*EXECUTION PLAN\*\*",
                r"EXECUTION PLAN",
                r"\*\*Execution Plan\*\*",
                r"## Execution Plan",
            ],
            "risks_and_mitigation": [
                r"\*\*RISKS AND MITIGATION\*\*",
                r"RISKS AND MITIGATION",
                r"\*\*Risks and Mitigation\*\*",
                r"\*\*RISKS & MITIGATION\*\*",
                r"## Risks",
            ],
        }

        # Find positions of each section
        section_positions = {}

        for section_key, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, raw_output, re.IGNORECASE)
                if match:
                    section_positions[section_key] = match.start()
                    break

        if not section_positions:
            # No sections found at all
            # Store entire output as problem_breakdown
            sections["problem_breakdown"] = raw_output.strip()
            return sections

        # Sort by position in text
        ordered = sorted(
            section_positions.items(),
            key=lambda x: x[1]
        )

        # Extract text between consecutive section headers
        for i, (section_key, start_pos) in enumerate(ordered):

            # Find where content starts (after the header line)
            header_end = raw_output.find("\n", start_pos)
            if header_end == -1:
                content_start = start_pos
            else:
                content_start = header_end + 1

            # Find where content ends (start of next section)
            if i + 1 < len(ordered):
                content_end = ordered[i + 1][1]
            else:
                content_end = len(raw_output)

            content = raw_output[content_start:content_end].strip()
            sections[section_key] = content

        return sections

    # ─────────────────────────────────────────────
    # SAMPLE ID GENERATION
    # ─────────────────────────────────────────────

    def generate_sample_id(self, counter: int) -> str:
        """Generate unique sample ID."""
        return f"BIZ-{str(counter).zfill(6)}"