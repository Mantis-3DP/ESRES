from pathlib import Path
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam, RMSprop
from tensorflow.keras.wrappers.scikit_learn import KerasClassifier, KerasRegressor
import shap


def create_custom_model(input_dim, output_dim, nodes, n, name, ):
    def create_model(conti):
        # Create model
        model = Sequential(name=name)
        model.add(Dense(nodes, input_dim=input_dim, activation='relu'))
        model.add(Dropout(0.25))
        model.add(Dense(nodes * 15 / 20, activation='relu'))
        #model.add(Dropout(0.25))
        model.add(Dense(nodes * 10 / 20, activation='relu'))
        if conti == 0:
            model.add(Dense(output_dim, activation='softmax'))
            model.compile(Adam(lr=0.001), loss='categorical_crossentropy',
                          metrics=['accuracy'])
        elif conti == 1:
            model.add(Dense(2, activation='relu'))
            model.compile(RMSprop(lr=0.1), loss='mse',
                          metrics=['mae', 'mse'])

        return model

    return create_model

def create_all_models(X_train, X_val, Y_train, Y_val, n_features, n_classes, model_number, conti):
    #n_classes = 1 #Zeile muss wieder weg
    models = [create_custom_model(n_features, n_classes, 64, n=4, name='model_{}'.format(model_number))]

    for create_model in models:
        create_model(conti).summary()

    for create_model in models:
        model = create_model(conti)
        print('Model name:', model.name)
        # history_callback =\

        model.fit(X_train, Y_train,
                  batch_size=10,
                  epochs=20,
                  # verbose=0,
                  validation_data=(X_val, Y_val)
                  )

        model.save(Path(__file__).parent / 'models/cold_system_{}.h5'.format(model.name))
        ### we need a wait and confirmation of a succsesful write
        print(Path(__file__).parent / 'models/cold_system_{}.h5 saved'.format(model.name))
    return





