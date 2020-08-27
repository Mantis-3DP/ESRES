from pathlib import Path

from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam, RMSprop


def create_custom_model(input_dim, output_dim, nodes, n, name, ):
    def create_model(conti):
        model = Sequential(name=name)
        model.add(Dense(nodes, input_dim=input_dim, activation='relu'))
        if conti == 0:
            # models for problem detection
            model.add(Dropout(0.25))
            model.add(Dense(nodes * 15 / 20, activation='relu'))
            model.add(Dropout(0.25))
            model.add(Dense(nodes * 10 / 20, activation='relu'))
            model.add(Dense(output_dim, activation='softmax'))
            model.compile(Adam(lr=0.001), loss='categorical_crossentropy',
                          metrics=['accuracy'])
        elif conti == 1:
            # models for measure evaluation
            model.add(Dense(nodes * 15 / 20, activation='relu'))
            model.add(Dense(nodes * 10 / 20, activation='relu'))
            model.add(Dense(1, activation='relu'))
            model.compile(RMSprop(lr=0.0001), loss='mse',
                          metrics=['mae', 'mse'])
        return model
    return create_model


def create_all_models(X_train, X_val, Y_train, Y_val, n_features, n_classes, model_number, folder, **kwargs):
    # to optimize the models this section could be looped with different model settings
    models = [create_custom_model(n_features, n_classes, 64, n=4, name='model_{}'.format(model_number))]
    if folder == "models_problem":
        measure = 0
    else:
        measure = 1
        measure_num = kwargs["measure_num"]

    for create_model in models:
        create_model(measure).summary()

    for create_model in models:
        model = create_model(measure)
        print('Model name:', model.name)

        model.fit(X_train, Y_train, batch_size=10, epochs=20, validation_data=(X_val, Y_val))
        if folder == "models_problem":
            model.save(Path(__file__).parent / 'models/{}/cold_system_{}.h5'.format(folder, model.name))
            print(Path(__file__).parent / 'models/{}/cold_system_{}.h5'.format(folder, model.name))
        else:
            model.save(Path(__file__).parent / 'models/{}/cold_system_{}_{}.h5'.format(folder, model.name, measure_num))
            print(Path(__file__).parent / 'models/{}/cold_system_{}_{}.h5'.format(folder, model.name, measure_num))
    return
