import tensorflow as tf
import models.utils as utils

class Model(tf.keras.Model):
  def __init__(self):
    super(Model, self).__init__()

    num_labels=1918
    conv_type='1d' #sequential data: [batch, seq, vec]

    #CNN
    self.conv_layers=[
        utils.ResidualLayer(conv_type=conv_type, num_filters=64 ,filter_size=9, pooling=True),
        utils.ResidualLayer(conv_type=conv_type, num_filters=128 ,filter_size=9, pooling=True),
        utils.ConvLayer(conv_type=conv_type, num_filters=256 ,filter_size=9),
        utils.ResidualLayer(conv_type=conv_type, num_filters=256 ,filter_size=9, pooling=True),
        utils.ConvLayer(conv_type=conv_type, num_filters=512 ,filter_size=9),
        utils.ResidualLayer(conv_type=conv_type, num_filters=512 ,filter_size=9, pooling=True),
        utils.ConvLayer(conv_type=conv_type, num_filters=512 ,filter_size=9),
        utils.ResidualLayer(conv_type=conv_type, num_filters=512 ,filter_size=9, pooling=True)
    ]

    #FLAT
    self.flat=tf.keras.layers.Flatten()

    #FC
    self.fc_layers=[
      tf.keras.layers.Dense(4096, activation='relu'),
      tf.keras.layers.Dense(1024, activation='relu'),
      tf.keras.layers.Dense(num_labels, activation='sigmoid')
    ]
    

  def call(self, x):
    print('Input shape:', x.shape)
    for i, layer in enumerate(self.conv_layers):
        x=layer(x)
        print('conv_{}: {}'.format(i, x.shape))

    x=self.flat(x)
    print('flatten', x.shape)
    for i,layer in enumerate(self.fc_layers):
      x=layer(x)
      print('fc_{}: {}'.format(i, x.shape))
    return x