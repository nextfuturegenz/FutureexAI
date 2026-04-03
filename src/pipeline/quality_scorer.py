# ============================================================
# Quality Scorer
# Rule-based scoring system
# No extra model needed
# Max score: 10 points
# ============================================================

import re
from typing import Dict, Tuple


# Phrases that indicate generic low-quality output
GENERIC_PHRASES = [
    "it depends",
    "there are many factors",
    "you should consider",
    "it is important to",
    "make sure to",
    "always remember",
    "in conclusion",
    "to summarize",
    "as mentioned above",
    "there is no one size fits all",
    "every business is different",
    "consult a professional",
    "do your research",
    "hope this helps",
]

# Phrases that indicate India-specific content
INDIA_SIGNALS = [
    "₹", "inr", "rupee", "lakh", "crore",
    "tier 2", "tier 3", "tier2", "tier3",
    "whatsapp", "upi", "razorpay", "paytm",
    "india", "indian", "mumbai", "delhi",
    "bangalore", "hyderabad", "chennai",
    "jaipur", "surat", "lucknow", "nagpur",
    "bootstrapped", "founder", "startup india",
    "smb", "msme",
]

# Phrases that indicate specific numbers/data
SPECIFICITY_SIGNALS = [
    r"₹[\d,]+",          # INR amounts
    r"\d+%",              # Percentages
    r"\d+ days?",         # Timeframes
    r"\d+ weeks?",
    r"\d+ months?",
    r"step \d",           # Numbered steps
    r"\d\.",              # Numbered lists
    r"day \d",
    r"week \d",
]


class QualityScorer:
    """
    Scores each generated sample on 5 dimensions.
    Total max score: 10 points.
    """

    # Thresholds
    PASS_THRESHOLD   = 7.0
    REVIEW_THRESHOLD = 4.0

    def score(
        self,
        sample: Dict
    ) -> Tuple[float, str, Dict]:
        """
        Score a sample and return result.

        Returns:
            score       : float 0-10
            flag        : 'PASS' | 'REVIEW' | 'FAIL'
            breakdown   : dict of individual scores
        """
        breakdown = {}
        total = 0.0

        # ── DIMENSION 1: Structure (0-2 points)
        # Are all 5 sections present?
        structure_score = self._score_structure(sample)
        breakdown["structure"] = structure_score
        total += structure_score

        # ── DIMENSION 2: Length (0-2 points)
        # Is the output long enough to be useful?
        length_score = self._score_length(sample)
        breakdown["length"] = length_score
        total += length_score

        # ── DIMENSION 3: Specificity (0-2 points)
        # Does it have real numbers and timeframes?
        specificity_score = self._score_specificity(sample)
        breakdown["specificity"] = specificity_score
        total += specificity_score

        # ── DIMENSION 4: India Context (0-2 points)
        # Does it reference Indian market realities?
        india_score = self._score_india_context(sample)
        breakdown["india_context"] = india_score
        total += india_score

        # ── DIMENSION 5: Non-Generic (0-2 points)
        # Does it avoid vague language?
        generic_score = self._score_non_generic(sample)
        breakdown["non_generic"] = generic_score
        total += generic_score

        # Round to 1 decimal
        total = round(total, 1)

        # Assign flag
        if total >= self.PASS_THRESHOLD:
            flag = "PASS"
        elif total >= self.REVIEW_THRESHOLD:
            flag = "REVIEW"
        else:
            flag = "FAIL"

        return total, flag, breakdown

    def _score_structure(self, sample: Dict) -> float:
        """Score based on presence of all 5 sections."""
        required_sections = [
            "problem_breakdown",
            "strategic_options",
            "recommended_decision",
            "execution_plan",
            "risks_and_mitigation",
        ]

        present = sum(
            1 for s in required_sections
            if sample.get(s) and len(sample.get(s, "").strip()) > 20
        )

        # 5/5 = 2.0 | 4/5 = 1.5 | 3/5 = 1.0 | 2/5 = 0.5 | <2 = 0
        if present == 5:
            return 2.0
        elif present == 4:
            return 1.5
        elif present == 3:
            return 1.0
        elif present == 2:
            return 0.5
        else:
            return 0.0

    def _score_length(self, sample: Dict) -> float:
        """Score based on total word count."""
        word_count = sample.get("word_count", 0)

        if word_count >= 400:
            return 2.0
        elif word_count >= 250:
            return 1.5
        elif word_count >= 150:
            return 1.0
        elif word_count >= 80:
            return 0.5
        else:
            return 0.0

    def _score_specificity(self, sample: Dict) -> float:
        """Score based on presence of specific numbers/data."""
        full_output = sample.get("full_output", "").lower()

        if not full_output:
            return 0.0

        matches = 0
        for pattern in SPECIFICITY_SIGNALS:
            if re.search(pattern, full_output, re.IGNORECASE):
                matches += 1

        if matches >= 5:
            return 2.0
        elif matches >= 3:
            return 1.5
        elif matches >= 2:
            return 1.0
        elif matches >= 1:
            return 0.5
        else:
            return 0.0

    def _score_india_context(self, sample: Dict) -> float:
        """Score based on India-specific content."""
        full_output = sample.get("full_output", "").lower()
        instruction = sample.get("instruction", "").lower()
        combined    = full_output + " " + instruction

        if not combined.strip():
            return 0.0

        matches = sum(
            1 for signal in INDIA_SIGNALS
            if signal.lower() in combined
        )

        if matches >= 5:
            return 2.0
        elif matches >= 3:
            return 1.5
        elif matches >= 2:
            return 1.0
        elif matches >= 1:
            return 0.5
        else:
            return 0.0

    def _score_non_generic(self, sample: Dict) -> float:
        """Score based on absence of generic phrases."""
        full_output = sample.get("full_output", "").lower()

        if not full_output:
            return 0.0

        generic_count = sum(
            1 for phrase in GENERIC_PHRASES
            if phrase.lower() in full_output
        )

        # Fewer generic phrases = better score
        if generic_count == 0:
            return 2.0
        elif generic_count == 1:
            return 1.5
        elif generic_count == 2:
            return 1.0
        elif generic_count == 3:
            return 0.5
        else:
            return 0.0