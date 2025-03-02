# CNN for vision (Occipital Lobe)
import os
import tensorflow as tf
from models.vision import VisionModule

# Optional: Mount Google Drive if running in Google Colab.
# Uncomment these lines when using Colab.
# from google.colab import drive
# drive.mount('/content/drive')

def load_data():
    """
    Loads CIFAR-10 data, normalizes pixel values,
    and resizes images from (32,32,3) to (224,224,3).
    """
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
    
    # Normalize the pixel values to [0,1]
    x_train = x_train.astype("float32") / 255.0
    x_test = x_test.astype("float32") / 255.0

    # Resize images to 224x224 (required by our VisionModule)
    x_train = tf.image.resize(x_train, (224, 224))
    x_test = tf.image.resize(x_test, (224, 224))
    
    return (x_train, y_train), (x_test, y_test)

def build_model(feature_dim=128, num_classes=10):
    """
    Constructs a model by stacking the VisionModule with
    a classifier head for demonstration.
    """
    inputs = tf.keras.Input(shape=(224, 224, 3))
    vision_module = VisionModule(feature_dim=feature_dim)
    features = vision_module(inputs)
    
    # Add a classification head on top of the features
    outputs = tf.keras.layers.Dense(num_classes, activation='softmax')(features)
    
    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    return model

def save_model(model, model_dir):
    """
    Saves the entire model to the specified directory.
    """
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    model.save(model_dir)
    print(f"Model saved to: {model_dir}")

def load_model(model_dir):
    """
    Loads a saved model from the specified directory.
    """
    if os.path.exists(model_dir):
        model = tf.keras.models.load_model(model_dir)
        print(f"Model loaded from: {model_dir}")
        return model
    else:
        print("No saved model found at the specified path.")
        return None

def main():
    # Define the directory where the model will be saved.
    # Adjust the path to your Google Drive location if running on Colab.
    model_dir = './saved_models/vision_model'
    # For Google Colab, it might look like:
    # model_dir = '/content/drive/MyDrive/brain_ai_tf/saved_models/vision_model'
    
    # Try loading an existing model
    model = load_model(model_dir)
    
    if model is None:
        # Load data
        (x_train, y_train), (x_test, y_test) = load_data()
    
        # Build the model
        model = build_model()
    
        # Compile the model with optimizer, loss, and evaluation metrics
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
    
        # Display the model's architecture
        model.summary()
    
        # Train the model for 10 epochs
        model.fit(x_train, y_train, epochs=10, validation_data=(x_test, y_test))
    
        # Save the model after training
        save_model(model, model_dir)
    else:
        # If the model was loaded successfully, you can evaluate or further train it.
        (x_train, y_train), (x_test, y_test) = load_data()
        loss, acc = model.evaluate(x_test, y_test)
        print(f"Loaded model test accuracy: {acc:.4f}")

if __name__ == '__main__':
    main()
