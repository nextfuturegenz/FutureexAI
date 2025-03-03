import os
import sys
import tensorflow as tf
import numpy as np

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.routing import RoutingModule

def create_dummy_fused_features(num_samples=100, input_dim=256):
    """
    Create dummy fused feature data.
    """
    X = np.random.rand(num_samples, input_dim).astype("float32")
    # Dummy targets (e.g., for regression or classification)
    y = np.random.rand(num_samples, 1).astype("float32")
    return X, y

def main():
    print("Starting training for Routing Module...")
    X, y = create_dummy_fused_features(num_samples=100, input_dim=256)
    
    # Let's say we want to project the fused features to 128 dimensions.
    model = RoutingModule(input_dim=256, output_dim=128)
    model.compile(optimizer="adam", loss="mse")
    model.summary(print_fn=lambda x: print(x))
    
    model.fit(X, y, epochs=5, batch_size=16)
    print("Routing module training complete.")

if __name__ == '__main__':
    main()
