import tensorflow as tf

class RoutingModule(tf.keras.Model):
    def __init__(self, input_dim, output_dim):
        """
        A simple dense layer to fuse features from multiple modules.
        """
        super(RoutingModule, self).__init__()
        self.dense = tf.keras.layers.Dense(output_dim, activation="relu")
    
    def call(self, x, training=False):
        return self.dense(x)
