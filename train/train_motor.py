# LSTM for motor control (Cerebellum)

import os
import sys
import tensorflow as tf
import numpy as np

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.motor import MotorControl

def create_dummy_sequence_data(num_samples=100, timesteps=10, input_size=10, output_size=2):
    """
    Create dummy sequential data for motor control.
    """
    X = np.random.rand(num_samples, timesteps, input_size).astype("float32")
    y = np.random.rand(num_samples, output_size).astype("float32")
    return X, y

def main():
    print("Starting training for Motor Control Module...")
    X, y = create_dummy_sequence_data(num_samples=100, timesteps=10, input_size=10, output_size=2)
    
    model = MotorControl(input_size=10, hidden_size=50, output_size=2)
    model.compile(optimizer="adam", loss="mse")
    model.summary(print_fn=lambda x: print(x))
    
    model.fit(X, y, epochs=5, batch_size=16)
    print("Motor control module training complete.")

if __name__ == '__main__':
    main()
