# Transformer for language (Temporal Lobe)
import tensorflow as tf
from transformers import TFAutoModel, AutoTokenizer

class LanguageModule(tf.keras.Model):
    def __init__(self, model_name="bert-base-uncased", output_dim=128):
        """
        A language processing module using a pre-trained transformer.
        It extracts semantic features and projects them into a fixed dimension.
        """
        super(LanguageModule, self).__init__()
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.transformer = TFAutoModel.from_pretrained(model_name)
        self.pooling = tf.keras.layers.GlobalAveragePooling1D()
        self.dense = tf.keras.layers.Dense(output_dim, activation="relu")
    
    def call(self, input_ids, attention_mask, training=False):
        # Pass inputs through the transformer.
        transformer_outputs = self.transformer(input_ids, attention_mask=attention_mask)
        # transformer_outputs.last_hidden_state shape: (batch, sequence_length, hidden_dim)
        pooled_output = self.pooling(transformer_outputs.last_hidden_state)
        features = self.dense(pooled_output)
        return features

    def tokenize(self, texts, max_length=32):
        """
        Utility method to tokenize raw text.
        Returns a dictionary with 'input_ids' and 'attention_mask' as TensorFlow tensors.
        """
        return self.tokenizer(
            texts, padding="max_length", truncation=True, max_length=max_length, return_tensors="tf"
        )
