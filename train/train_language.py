# Transformer for language (Temporal Lobe)
import os
import sys
import tensorflow as tf
import numpy as np

# Force CPU mode for local testing (remove for GPU production)
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# Add project root to sys.path so that models can be found.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.language import LanguageModule

def create_dummy_dataset(num_samples=100):
    """
    Create a dummy dataset of texts and labels.
    For demonstration, we simply use a list of example sentences.
    """
    texts = ["This is a test sentence." for _ in range(num_samples)]
    # Dummy binary labels (0 or 1)
    labels = np.random.randint(0, 2, size=(num_samples, 1))
    return texts, labels

def build_classifier(output_dim=128, num_classes=2):
    """
    Builds a simple classifier by stacking the language module
    with a classification head.
    """
    # Define inputs for tokenized text
    input_ids = tf.keras.Input(shape=(32,), dtype=tf.int32, name="input_ids")
    attention_mask = tf.keras.Input(shape=(32,), dtype=tf.int32, name="attention_mask")
    
    language_module = LanguageModule(output_dim=output_dim)
    features = language_module(input_ids, attention_mask)
    
    # Add a classifier head.
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(features)
    model = tf.keras.Model(inputs=[input_ids, attention_mask], outputs=outputs)
    return model

def main():
    print("Starting training for Language Module...")
    texts, labels = create_dummy_dataset(num_samples=100)
    
    # Instantiate the language module for tokenization.
    language_module = LanguageModule()
    encoded = language_module.tokenize(texts, max_length=32)
    
    # Build classifier model.
    model = build_classifier(output_dim=128, num_classes=2)
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    model.summary(print_fn=lambda x: print(x))
    
    # Create a tf.data.Dataset from the encoded tensors.
    dataset = tf.data.Dataset.from_tensor_slices((encoded, labels))
    dataset = dataset.batch(16).prefetch(tf.data.AUTOTUNE)
    
    model.fit(dataset, epochs=3)
    print("Language module training complete.")

if __name__ == '__main__':
    main()
