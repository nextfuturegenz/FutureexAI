"""
Brain Bridge - Connects Exon to your existing old/model modules
"""

import sys
import os

# Add parent directory to path
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PARENT_DIR)


class BrainBridge:
    """Wrapper around your existing brain modules"""
    
    def __init__(self):
        self.modules_available = False
        self.language = None
        self.memory = None
        self.decision = None
        
        try:
            # Try to import your existing modules
            from old.model.language import LanguageModule
            from old.model.memory import MemoryModule
            from old.model.decision import DecisionModule
            
            # Initialize with dummy values to test
            self.language = LanguageModule(model_name="bert-base-uncased")
            self.memory = MemoryModule(input_size=128, memory_size=100)
            self.decision = DecisionModule(input_dim=128, num_actions=10)
            
            self.modules_available = True
            print("[BRAIN] Successfully loaded your existing brain modules")
        except Exception as e:
            print(f"[BRAIN] Could not load existing modules: {e}")
            print("[BRAIN] Using mock implementations")
            self.modules_available = False
    
    def get_embedding(self, text: str):
        """Get semantic embedding of text"""
        if self.modules_available and self.language:
            try:
                tokenized = self.language.tokenize([text])
                features = self.language(
                    tokenized["input_ids"],
                    tokenized["attention_mask"],
                    training=False
                )
                return features.numpy()
            except Exception as e:
                print(f"[BRAIN] Embedding error: {e}")
        
        # Mock embedding
        import numpy as np
        return np.random.rand(1, 128)
    
    def augment_with_memory(self, embedding):
        """Augment embedding with memory"""
        if self.modules_available and self.memory:
            try:
                import tensorflow as tf
                emb_tensor = tf.convert_to_tensor(embedding, dtype=tf.float32)
                result = self.memory(emb_tensor, training=False)
                return result.numpy()
            except Exception as e:
                print(f"[BRAIN] Memory augmentation error: {e}")
        
        return embedding
    
    def decide_action(self, state_vector):
        """Make decision based on state"""
        if self.modules_available and self.decision:
            try:
                import tensorflow as tf
                state_tensor = tf.convert_to_tensor(state_vector, dtype=tf.float32)
                q_values = self.decision(state_tensor, training=False)
                return q_values.numpy()
            except Exception as e:
                print(f"[BRAIN] Decision error: {e}")
        
        # Mock decision
        return [0.5] * 10