# RL agent (Frontal Lobe) using TF-Agents or custom training loops
import os
import sys
import tensorflow as tf
import numpy as np

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.decision import DecisionModule

def create_dummy_experience(num_samples=200, input_dim=20, num_actions=4):
    """
    Create dummy experience tuples.
    For demonstration, we generate random state features.
    """
    states = np.random.rand(num_samples, input_dim).astype("float32")
    # Dummy Q-targets (for a regression loss)
    targets = np.random.rand(num_samples, num_actions).astype("float32")
    return states, targets

def main():
    print("Starting training for Decision Module...")
    input_dim = 20
    num_actions = 4
    states, targets = create_dummy_experience(num_samples=200, input_dim=input_dim, num_actions=num_actions)
    
    model = DecisionModule(input_dim=input_dim, num_actions=num_actions)
    model.compile(optimizer="adam", loss="mse")
    model.summary(print_fn=lambda x: print(x))
    
    model.fit(states, targets, epochs=5, batch_size=16)
    print("Decision module training complete.")

if __name__ == '__main__':
    main()
