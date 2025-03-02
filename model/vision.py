# CNN for vision (Occipital Lobe)
import tensorflow as tf

class VisionModule(tf.keras.Model):
    def __init__(self, feature_dim=128):
        """
        A simple CNN-based feature extractor.
        Args:
            feature_dim: The dimension of the output feature vector.
        """
        super(VisionModule, self).__init__()
        # Convolutional layers
        self.conv1 = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')
        self.pool1 = tf.keras.layers.MaxPooling2D((2, 2))
        self.conv2 = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')
        self.pool2 = tf.keras.layers.MaxPooling2D((2, 2))
        self.conv3 = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same')
        self.pool3 = tf.keras.layers.MaxPooling2D((2, 2))
        
        # Flatten and Dense layers to produce the feature vector
        self.flatten = tf.keras.layers.Flatten()
        self.fc = tf.keras.layers.Dense(feature_dim, activation='relu')
        
    def call(self, x, training=False):
        x = self.conv1(x)
        x = self.pool1(x)
        x = self.conv2(x)
        x = self.pool2(x)
        x = self.conv3(x)
        x = self.pool3(x)
        x = self.flatten(x)
        x = self.fc(x)
        return x
