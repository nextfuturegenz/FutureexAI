import tensorflow as tf
import numpy as np
from transformers import AutoTokenizer

def preprocess_image(image, target_size=(224, 224)):
    """
    Preprocess an image: convert to tensor, resize, and normalize.
    
    Args:
        image: A NumPy array representing an image.
        target_size: A tuple specifying the desired (height, width).
        
    Returns:
        A TensorFlow tensor of the processed image.
    """
    # Convert the numpy image to a tensor.
    image_tensor = tf.convert_to_tensor(image, dtype=tf.float32)
    # Resize the image.
    image_tensor = tf.image.resize(image_tensor, target_size)
    # Normalize pixel values to [0, 1] if they are not already.
    image_tensor = image_tensor / 255.0
    return image_tensor

def preprocess_text(text, tokenizer_name="bert-base-uncased", max_length=32):
    """
    Preprocess text using a Hugging Face tokenizer.
    
    Args:
        text: A string (or a list of strings) to be tokenized.
        tokenizer_name: Name of the pre-trained tokenizer.
        max_length: Maximum sequence length for tokenization.
        
    Returns:
        A dictionary with keys "input_ids" and "attention_mask" as TensorFlow tensors.
    """
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    encoding = tokenizer(
        text,
        padding="max_length",
        truncation=True,
        max_length=max_length,
        return_tensors="tf"
    )
    return encoding

def convert_to_tf_tensor(np_array):
    """
    Convert a NumPy array to a TensorFlow tensor.
    
    Args:
        np_array: A NumPy array.
        
    Returns:
        A TensorFlow tensor.
    """
    return tf.convert_to_tensor(np_array)
