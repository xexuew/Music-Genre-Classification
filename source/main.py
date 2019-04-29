import configparser
import argparse
import matplotlib.pyplot as plt
import os
import sys
import json

parser = argparse.ArgumentParser()
parser.add_argument("--preprocess", "-p", help = "Preparar los datos de las canciones", action = "store_true")
parser.add_argument("--dataset", "-d", help = "Preparar los datos para el entrenamiento", action = "store_true")
parser.add_argument("--trainmodel", "-t", help = "Entrenar el modelo", action = "store_true")
parser.add_argument("--model", "-m ", help = "Archivo con los parámetros del modelo")
parser.add_argument("--config", "-c", help = "Archivo de Configuracion")
parser.add_argument("--device", "-v", type = int, default = 0, help = "Cuda Visible Device")
args = parser.parse_args()

# Seleccionamos la gpu disponible. Por defecto la 0.
os.environ["CUDA_VISIBLE_DEVICES"] = str(args.device);

from keras import optimizers
from keras import losses
from keras.utils import np_utils
from keras.callbacks import TensorBoard, EarlyStopping, ModelCheckpoint
from os.path import isfile
from pathlib import Path
from tensorflow.python.keras import backend as K
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Activation
from keras.layers import Flatten
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import MaxPooling2D

from Extract_Audio_Features import ExtractAudioFeatures
from Get_Train_Test_Data import GetTrainTestData
from Create_Model import CNNModel

config_path = Path(args.config)
if not config_path.exists():
    print("No se ha encontrado el fichero config")
    sys.exit(0)
config = configparser.ConfigParser()
config.read(config_path)

if args.preprocess:
    ExtractAudioFeatures(config).prepossessingAudio()
elif args.dataset:
    GetTrainTestData(config).splitDataset()
elif args.trainmodel:
    # Leemos los datos
    X_train, X_test, X_val, y_train, y_test, y_val = GetTrainTestData(config).read_dataset()
 
    X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], X_train.shape[2], 1).astype('float32')
    X_test = X_test.reshape(X_test.shape[0], X_train.shape[1], X_train.shape[2], 1).astype('float32')
    X_val = X_val.reshape(X_val.shape[0], X_val.shape[1], X_val.shape[2], 1).astype('float32')
    
    y_train = np_utils.to_categorical(y_train)
    y_test = np_utils.to_categorical(y_test)
    y_val = np_utils.to_categorical(y_val)

    model_path = Path(args.model)
    if not model_path.exists():
        print("No se ha encontrado el fichero model")
        sys.exit(0)
    with open(model_path) as json_data:
        modelo = json.load(json_data)

    try:
        os.mkdir(config['CALLBACKS']['TENSORBOARD_LOGDIR'] + str(modelo['id']))
    except:
        print("No se ha podido crear la carpeta")
        pass

    # Creamos el modelo
    model = CNNModel(config, modelo, X_train).build_model(nb_classes = y_test.shape[1])
    model.compile(loss = losses.categorical_crossentropy,
                #optimizer = optimizers.Adam(lr = 0.001),
                optimizer = optimizers.SGD(lr = 0.001, momentum = 0, decay = 1e-5, nesterov = True),
                metrics = ['accuracy'])
    model.summary()
            
    # Guardamos el Modelo
    model_json = model.to_json()
    model_json_path = Path(config['CALLBACKS']['TENSORBOARD_LOGDIR'] + str(modelo['id']) + "/model.json")
    with open(model_json_path, "w") as json_file:
        json_file.write(model_json)

    # Comprobamos si hay un fichero checkpoint
    if int(config['CALLBACKS']['LOAD_CHECKPOINT']):
        print("Buscando fichero Checkpoint...")
        if isfile(config['CALLBACKS']['CHECKPOINT_FILE']):
            print('Fichero Checkpoint detectando. Cargando weights.')
            model.load_weights(config['CALLBACKS']['CHECKPOINT_FILE'])
        else:
            print('No se ha detectado el fichero Checkpoint.  Empezando de cero')
    else:
        print('No Checkpoint')
            
    # Creamos los Callbacks
    """
    ModelCheckpoint(filepath = config['CALLBACKS']['CHECKPOINT_FILE'],
        verbose = 1,
        save_best_only = True,
    ),
    """
    callbacks = [
                TensorBoard(log_dir = config['CALLBACKS']['TENSORBOARD_LOGDIR'] + str(modelo['id']),
                            write_images = config['CALLBACKS']['TENSORBOARD_WRITEIMAGES'],
                            write_graph = config['CALLBACKS']['TENSORBOARD_WRITEGRAPH'],
                            update_freq = config['CALLBACKS']['TENSORBOARD_UPDATEFREQ']
                            ),
                EarlyStopping(monitor = config['CALLBACKS']['EARLYSTOPPING_MONITOR'],
                            mode = config['CALLBACKS']['EARLYSTOPPING_MODE'], 
                            patience = int(config['CALLBACKS']['EARLYSTOPPING_PATIENCE']),
                            verbose = 1)
    ]

    # Entrenamos el modelo
    history = model.fit(
                        X_train,
                        y_train,
                        batch_size = int(config['CNN_CONFIGURATION']['BATCH_SIZE']),
                        epochs = int(config['CNN_CONFIGURATION']['NUMBERS_EPOCH']),
                        verbose = 1,
                        validation_data = (X_val, y_val),
                        callbacks = callbacks)

    score = model.evaluate(X_test, y_test, verbose=0)
    print('Test score:', score[0])
    print('Test accuracy:', score[1])

    print(history.history.keys())

    # Grafica Accuracy
    plt.plot(history.history['acc'])
    plt.plot(history.history['val_acc'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.savefig(config['CALLBACKS']['TENSORBOARD_LOGDIR'] + str(modelo['id']) +  '/acc.png')
    plt.close()

    # Grafica Loss 
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.savefig(config['CALLBACKS']['TENSORBOARD_LOGDIR'] + str(modelo['id']) + '/loss.png')

    model.save_weights(config['PATH_CONFIGURATION']['OUTPUT'] + config['OUTPUT']['WEIGHTS_FILE'])