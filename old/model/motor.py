# LSTM for motor control (Cerebellum)

import tensorflow as tf

class MotorControl(tf.keras.Model):
    def __init__(self, input_size=10, hidden_size=50, output_size=2):
        """
        An LSTM-based module for motor control.
        """
        super(MotorControl, self).__init__()
        self.lstm = tf.keras.layers.LSTM(hidden_size, return_sequences=False)
        self.dense = tf.keras.layers.Dense(output_size, activation="linear")
    
    def call(self, x, training=False):
        # x shape: (batch, timesteps, input_size)
        x = self.lstm(x)
        output = self.dense(x)
        return output
