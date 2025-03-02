import numpy as np
from pipeline.integrate import BrainAI

def main():
    # Initialize the hybrid brain-inspired AI model
    brain = BrainAI()
    print("Brain AI model initialized successfully!")
    
    # Create dummy inputs for testing each module
    # Dummy image: Assuming shape (batch, height, width, channels)
    dummy_image = np.random.rand(1, 224, 224, 3).astype('float32')
    
    # Dummy text input: Using a dictionary that mimics Hugging Face tokenized output
    # (For example, using input_ids and attention_mask)
    dummy_text = {
        "input_ids": np.array([[101, 2054, 2003, 1996, 2561, 102]]),  # Example token IDs
        "attention_mask": np.array([[1, 1, 1, 1, 1, 1]])
    }
    
    # Dummy environment state for the Decision Module (e.g., a feature vector)
    dummy_env_state = np.random.rand(1, 10).astype('float32')
    
    # Dummy motor control input for the LSTM (shape: batch, time steps, features)
    dummy_motor_input = np.random.rand(1, 10, 10).astype('float32')

    # Perform a forward pass through the integrated model
    outputs = brain.forward(dummy_image, dummy_text, dummy_env_state, dummy_motor_input)
    
    # Display the outputs from each module
    print("Model outputs:")
    for key, value in outputs.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
