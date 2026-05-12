"""
Connects Exon to your old/model modules (Decision, Language, Memory, etc.)
"""

import sys
import os
import numpy as np
import tensorflow as tf

FUTUREEX_PATH = os.environ.get("FUTUREEX_PATH", "/home/nfg/FutureexAI")
sys.path.insert(0, FUTUREEX_PATH)

from old.model.decision import DecisionModule
from old.model.language import LanguageModule
from old.model.memory import MemoryModule
from old.model.routing import RoutingModule


class BrainBridge:
    """Wrapper around your existing brain modules."""

    def __init__(self):
        self.language = LanguageModule(model_name="bert-base-uncased")
        self.memory = MemoryModule(input_size=128, memory_size=100)
        self.decision = DecisionModule(input_dim=128, num_actions=10)
        self.routing = RoutingModule(input_dim=384, output_dim=256)

        # Note: we don't load actual BERT weights here to save memory;
        # the LanguageModule will lazy-load. If you want to preload, call
        # self.language.transformer etc.

    def get_embedding(self, text: str) -> np.ndarray:
        """Get semantic embedding using your LanguageModule."""
        tokenized = self.language.tokenize([text])
        features = self.language(
            tokenized["input_ids"],
            tokenized["attention_mask"],
            training=False
        )
        return features.numpy()[0]

    def augment_with_memory(self, embedding: np.ndarray) -> np.ndarray:
        """Apply your MemoryModule to embedding."""
        emb_tensor = tf.convert_to_tensor(embedding.reshape(1, -1), dtype=tf.float32)
        memory_output = self.memory(emb_tensor, training=False)
        return memory_output.numpy().flatten()