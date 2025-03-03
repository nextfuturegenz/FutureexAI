# Memory-Augmented Network (Limbic System)
import os
import sys
import tensorflow as tf
import numpy as np

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.memory import MemoryModule

def create_dummy_feature_data(num_samples=100, feature_size=128):
    """
    Create dummy feature data and binary labels.
    """
    X = np.random.rand(num_samples, feature_size).astype("float32")
    y = np.random.randint(0, 2, size=(num_samples, 1)).astype("float32")
    return X, y

def main():
    print("Starting training for Memory & Emotion Module...")
    X, y = create_dummy_feature_data(num_samples=100, feature_size=128)
    
    model = MemoryModule(input_size=128, memory_size=100)
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    model.summary(print_fn=lambda x: print(x))
    
    model.fit(X, y, epochs=5, batch_size=16)
    print("Memory module training complete.")

if __name__ == '__main__':
    main()
