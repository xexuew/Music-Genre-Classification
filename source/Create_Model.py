from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Activation
from keras.layers import Flatten
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import MaxPooling2D


class CNNModel(object):
    """
        Creacción del modelo CNN
        # Arguments:
            object: configparser
                Archivo con las distintas configuraciones.
    """


    def __init__(self, config, model, X):

        # Filtros a usar
        self.filters1 = int(model['layer1']['filters'])
        # Tamaños para el area del Max Pooling
        self.pool_size1 = tuple(model['layer1']['pool_size'])
        # Tamaño Kernel para la Convolución
        self.kernel_size1 = tuple(model['layer1']['kernel_size'])
        self.padding1 = model['layer1']['padding']

        self.filters2 = int(model['layer2']['filters'])
        self.pool_size2 = tuple(model['layer2']['pool_size'])
        self.kernel_size2 = tuple(model['layer2']['kernel_size'])
        self.padding2 = model['layer2']['padding']
        self.dropout2 = float(model['layer2']['dropout'])

        self.filters3 = int(model['layer3']['filters'])
        self.pool_size3 = tuple(model['layer3']['pool_size'])
        self.kernel_size3 = tuple(model['layer3']['kernel_size'])
        self.padding3 = model['layer3']['padding']
        self.dropout3 = float(model['layer3']['dropout'])
        
        self.filters4 = int(model['layer4']['filters'])
        self.pool_size4 = tuple(model['layer4']['pool_size'])
        self.kernel_size4 = tuple(model['layer4']['kernel_size'])
        self.padding4 = model['layer4']['padding']
        self.dropout4 = float(model['layer4']['dropout'])

        self.input_shape = (X.shape[1], X.shape[2], X.shape[3])
        
        
    def build_model(self, nb_classes):
        """
            Crea el modelo en función de los parámetros establecidos.
            # Return:
                model: keras.model
        """
        model = Sequential()
        model.add(
                Conv2D(
                    self.filters1,
                    self.kernel_size1,
                    padding = self.padding1,
                    input_shape = self.input_shape))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size = self.pool_size1))
        
        model.add(
                Conv2D(
                    self.filters2,
                    self.kernel_size2,
                    padding = self.padding2))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size = self.pool_size2))
        model.add(Dropout(self.dropout2))

        model.add(
                Conv2D(
                    self.filters3,
                    self.kernel_size3,
                    padding = self.padding3))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size = self.pool_size3))
        model.add(Dropout(self.dropout3))
        
        model.add(
                Conv2D(
                    self.filters4,
                    self.kernel_size4,
                    padding = self.padding4))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size = self.pool_size4))
        model.add(Dropout(self.dropout4))
             
        model.add(Flatten())

        model.add(Dense(512))
        model.add(Activation('relu'))
        model.add(Dropout(0.5))

        model.add(Dense(nb_classes))
        model.add(Activation("softmax"))
        
        return model