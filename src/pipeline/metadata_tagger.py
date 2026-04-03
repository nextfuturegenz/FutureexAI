# ============================================================
# Metadata Tagger
# Assigns all metadata fields to each sample
# ============================================================

import re
from typing import Dict, Any


class MetadataTagger:
    """
    Assigns metadata to each generated sample.
    Called after generation and quality scoring.
    """

    def tag(
        self,
        raw_sample: Dict[str, Any],
        prompt_metadata: Dict[str, Any],
        quality_score: float,
        quality_flag: str,
        quality_breakdown: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Add all metadata to a sample.

        Args:
            raw_sample      : Dict with instruction + parsed sections
            prompt_metadata : Dict from PromptSelector
            quality_score   : Float 0-10
            quality_flag    : PASS / REVIEW / FAIL
            quality_breakdown: Per-dimension scores

        Returns:
            Complete sample dict ready for DB insert
        """

        full_output = self._build_full_output(raw_sample)
        word_count  = self._count_words(full_output)
        has_india   = self._detect_india_context(
            full_output,
            raw_sample.get("instruction", "")
        )

        return {
            # Identity
            "sample_id":    raw_sample.get("sample_id"),
            "batch_id":     raw_sample.get("batch_id"),
            "sprint":       "SPRINT-1",

            # Classification
            "source_model": raw_sample.get("source_model"),
            "category":     prompt_metadata.get("category"),
            "subcategory":  prompt_metadata.get("subcategory"),
            "industry":     prompt_metadata.get("industry"),
            "geography":    prompt_metadata.get("geography"),
            "business_stage": prompt_metadata.get("business_stage"),

            # Content
            "instruction":          raw_sample.get("instruction"),
            "problem_breakdown":    raw_sample.get("problem_breakdown"),
            "strategic_options":    raw_sample.get("strategic_options"),
            "recommended_decision": raw_sample.get("recommended_decision"),
            "execution_plan":       raw_sample.get("execution_plan"),
            "risks_and_mitigation": raw_sample.get("risks_and_mitigation"),
            "full_output":          full_output,
            "critique_output":      raw_sample.get("critique_output"),
            "improved_output":      raw_sample.get("improved_output"),

            # Metrics
            "word_count":        word_count,
            "has_india_context": has_india,
            "quality_score":     quality_score,
            "quality_flag":      quality_flag,
            "notes": (
                f"QBreakdown: structure={quality_breakdown.get('structure')} "
                f"length={quality_breakdown.get('length')} "
                f"specificity={quality_breakdown.get('specificity')} "
                f"india={quality_breakdown.get('india_context')} "
                f"generic={quality_breakdown.get('non_generic')}"
            )
        }

    def _build_full_output(self, sample: Dict) -> str:
        """Combine all 5 sections into full output string."""
        sections = [
            ("PROBLEM BREAKDOWN",    "problem_breakdown"),
            ("STRATEGIC OPTIONS",    "strategic_options"),
            ("RECOMMENDED DECISION", "recommended_decision"),
            ("EXECUTION PLAN",       "execution_plan"),
            ("RISKS AND MITIGATION", "risks_and_mitigation"),
        ]

        parts = []
        for header, key in sections:
            content = sample.get(key, "").strip()
            if content:
                parts.append(f"**{header}**\n{content}")

        return "\n\n".join(parts)

    def _count_words(self, text: str) -> int:
        """Count words in output."""
        if not text:
            return 0
        return len(text.split())

    def _detect_india_context(
        self,
        output: str,
        instruction: str
    ) -> bool:
        """Detect if sample has India-specific content."""
        india_signals = [
            "₹", "inr", "rupee", "lakh", "crore",
            "india", "indian", "tier 2", "tier 3",
            "whatsapp", "upi", "mumbai", "delhi",
            "bangalore", "jaipur", "surat", "nagpur",
        ]
        combined = (output + " " + instruction).lower()
        return any(s in combined for s in india_signals)