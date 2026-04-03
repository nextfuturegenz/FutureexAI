# ============================================================
# Self Critique Loop
# Generate → Critique → Improve
# Runs on same model that generated original
# ============================================================

from typing import Optional, Dict, Any
from ..generators.base_generator import BaseGenerator
from ..prompts.templates import PromptSelector


class SelfCritiqueLoop:
    """
    Runs self-critique improvement cycle.

    For every generated sample:
    Step 1 → Generate initial answer
    Step 2 → Ask model to critique it
    Step 3 → Ask model to produce improved version
    Step 4 → Return improved version as final output
    """

    def __init__(self, generator: BaseGenerator):
        self.generator = generator
        self.selector  = PromptSelector()

    def run(
        self,
        instruction: str,
        initial_output: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run full critique + improvement cycle.

        Returns:
            Dict with critique_output and improved_output
        """
        result = {
            "critique_output":  None,
            "improved_output":  None,
            "used_improvement": False
        }

        # Step 1: Generate critique
        critique_prompt = self.selector.get_critique_prompt(
            instruction=instruction,
            original_response=initial_output
        )

        critique = self.generator.generate(
            prompt=critique_prompt,
            max_new_tokens=1500,
            temperature=0.6,   # Lower temp for critique
        )

        if not critique:
            return result

        result["critique_output"] = critique

        # Extract improved response from critique output
        improved = self._extract_improved_section(critique)

        if improved and len(improved) > len(initial_output) * 0.7:
            result["improved_output"]  = improved
            result["used_improvement"] = True
        else:
            # Critique did not produce better output
            # Keep original
            result["improved_output"]  = initial_output
            result["used_improvement"] = False

        return result

    def _extract_improved_section(
        self,
        critique_output: str
    ) -> Optional[str]:
        """
        Extract the improved response section
        from critique output.
        """
        if not critique_output:
            return None

        # Look for IMPROVED RESPONSE marker
        markers = [
            "**IMPROVED RESPONSE**",
            "IMPROVED RESPONSE",
            "**Improved Response**",
            "## Improved Response",
            "**IMPROVED ANSWER**",
        ]

        for marker in markers:
            if marker in critique_output:
                idx = critique_output.find(marker)
                # Get everything after the marker
                improved = critique_output[
                    idx + len(marker):
                ].strip()

                if improved and len(improved) > 100:
                    return improved

        return None