# Memory-Augmented Network (Limbic System)
import tensorflow as tf

class MemoryModule(tf.keras.Model):
    def __init__(self, input_size=128, memory_size=100):
        """
        A memory-augmented network that adds a trainable memory vector to input features.
        """
        super(MemoryModule, self).__init__()
        # Initialize a trainable memory matrix (or vector mean)
        self.memory = self.add_weight(
            shape=(memory_size, input_size), initializer="random_normal", trainable=True, name="memory"
        )
        self.dense = tf.keras.layers.Dense(1, activation="sigmoid")
    
    def call(self, x, training=False):
        # Compute the mean memory vector.
        memory_mean = tf.reduce_mean(self.memory, axis=0)
        x_augmented = x + memory_mean
        output = self.dense(x_augmented)
        return output
