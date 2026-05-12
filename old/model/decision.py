# RL agent (Frontal Lobe) using TF-Agents or custom training loops

import tensorflow as tf

class DecisionModule(tf.keras.Model):
    def __init__(self, input_dim, num_actions):
        """
        A simple Q-network that outputs Q-values for each action.
        """
        super(DecisionModule, self).__init__()
        self.dense1 = tf.keras.layers.Dense(128, activation="relu")
        self.dense2 = tf.keras.layers.Dense(64, activation="relu")
        self.out_layer = tf.keras.layers.Dense(num_actions, activation="linear")
    
    def call(self, x, training=False):
        x = self.dense1(x)
        x = self.dense2(x)
        q_values = self.out_layer(x)
        return q_values
