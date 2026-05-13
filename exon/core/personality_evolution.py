"""
File: /opt/futureex/exon/core/personality_evolution.py
Author: Ashish Pal
Purpose: Shift personality traits based on user feedback and successful interactions.
"""

import json
import logging
from typing import Dict, List
import redis.asyncio as redis

logger = logging.getLogger(__name__)

# Default initial traits
DEFAULT_TRAITS = {
    "curiosity": 0.7,
    "formality": 0.5,
    "optimism": 0.6,
    "verbosity": 0.5
}

class PersonalityEvolution:
    def __init__(self, exon_id: str, redis_client: redis.Redis):
        self.exon_id = exon_id
        self.redis = redis_client
        self.traits_key = f"{exon_id}:personality_traits"
        self.feedback_key = f"{exon_id}:feedback_count"

    async def get_traits(self) -> Dict[str, float]:
        """Get current personality traits."""
        traits = await self.redis.hgetall(self.traits_key)
        if not traits:
            # Initialize default
            await self.redis.hset(self.traits_key, mapping=DEFAULT_TRAITS)
            return DEFAULT_TRAITS.copy()
        return {k: float(v) for k, v in traits.items()}

    async def update_from_feedback(self, user_message: str, response: str, was_successful: bool):
        """Adjust traits based on implicit/explicit feedback."""
        traits = await self.get_traits()
        delta = 0.02 if was_successful else -0.02

        # Detect explicit feedback keywords
        msg_lower = user_message.lower()
        if "too formal" in msg_lower:
            traits["formality"] -= 0.05
        elif "too casual" in msg_lower:
            traits["formality"] += 0.05
        if "be more curious" in msg_lower:
            traits["curiosity"] += 0.05
        if "be more optimistic" in msg_lower:
            traits["optimism"] += 0.05
        if "be more concise" in msg_lower:
            traits["verbosity"] -= 0.05
        elif "be more detailed" in msg_lower:
            traits["verbosity"] += 0.05

        # Also adjust based on success (positive reinforcement)
        if was_successful:
            traits["curiosity"] += delta
            traits["optimism"] += delta
        else:
            traits["curiosity"] -= delta*0.5

        # Clamp values
        for k in traits:
            traits[k] = max(0.1, min(1.0, traits[k]))

        await self.redis.hset(self.traits_key, mapping=traits)
        await self.redis.incr(self.feedback_key)
        logger.debug(f"Personality updated: {traits}")

    async def get_temperature_modifier(self) -> float:
        """Return temperature adjustment based on traits."""
        traits = await self.get_traits()
        # More curiosity -> higher temp; more formality -> lower
        modifier = (traits["curiosity"] * 0.3) - (traits["formality"] * 0.2)
        return max(-0.3, min(0.3, modifier))