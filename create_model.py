import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, MinMaxScaler
from pathlib import Path
from sklearn.utils import shuffle
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Activation, Dense
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from keras.callbacks import TensorBoard
import seaborn as sns



def create_custom_model(input_dim, output_dim, nodes, n=2, name='model'):
    def create_model():
        # Create model
        model = Sequential(name=name)
        for i in range(n):
            model.add(Dense(nodes, input_dim=input_dim, activation='relu'))
        model.add(Dense(output_dim, activation='softmax'))

        # Compile model
        model.compile(Adam(lr=0.001), loss='categorical_crossentropy',
                      metrics=['accuracy'])
        return model
    return create_model


if __name__=="__main__":
    #change to import from .json
    fileloca_train = Path(__file__).parent / "data_sets/samleDataRefriRoom_transpose_new.csv"
    fileloca_test = Path(__file__).parent / "data_sets/test_transpose.csv"
    dataset_train = pd.read_csv(fileloca_train)
    dataset_test = pd.read_csv(fileloca_test)

    dataset_train_values = dataset_train.values
    dataset_test_values = dataset_test.values

    feature_names = list(dataset_train.columns[:-1])

    X = dataset_train_values[:, :-1]
    y = dataset_train_values[:, -1]
    X_test = dataset_test_values[:, :-1]
    y_test = dataset_test_values[:, -1]

    names = pd.Categorical(y).categories

    encoder = LabelEncoder()
    encoder_test = LabelEncoder()
    encoder.fit(y)
    encoder_test.fit(y_test)

    encoded_Y = encoder.transform(y)
    encoded_Y_test = encoder_test.transform(y_test)

    ######correlations

    corr_data = dataset_train
    corr_data['Measure'] = encoded_Y
    corr = corr_data.corr()
    heatmap = sns.heatmap(corr, xticklabels=list(dataset_train.columns[:]), yticklabels=list(dataset_train.columns[:]))
    plt.show()


    # One hot encoding
    enc = OneHotEncoder()
    enc_test = OneHotEncoder()
    Y = enc.fit_transform(y[:, np.newaxis]).toarray()
    Y_test = enc_test.fit_transform(y_test[:, np.newaxis]).toarray()

    train_samples, train_labels = shuffle(X, Y)
    scaler = MinMaxScaler(feature_range=(0, 1))

    X_scaled= scaler.fit_transform(train_samples)
    X_scaled_test = scaler.fit_transform(X_test)

    X_train, X_val, Y_train, Y_val = train_test_split(
        X_scaled, train_labels, test_size=0.1, random_state=2)

    n_features = X.shape[1]
    n_classes = Y.shape[1]


    models = [create_custom_model(n_features, n_classes, 10, n=i, name='model_{}'.format(i))
              for i in range(2, 3)]

    for create_model in models:
        create_model().summary()

    history_dict = {}

    # TensorBoard Callback
    cb = TensorBoard()

    for create_model in models:
        model = create_model()
        print('Model name:', model.name)
        #history_callback =\
        model.fit(X_train, Y_train,
                                     batch_size=1,
                                     epochs=100,
                                     #verbose=0,
                                     validation_data=(X_val, Y_val)
                  )
        '''
        score = model.evaluate(
            X_scaled_test,
            Y_test,
            verbose=0
        )
        print('Test loss:', score[0])
        print('Test accuracy:', score[1])
        predictions = model.predict(x=X_scaled_test, batch_size=1, verbose=0)
        print(predictions)
        rounded_predictions = np.argmax(predictions, axis=-1)
        print('measures for test scenarios are:')
        for i in rounded_predictions:
            print(names[i])
        '''


    #history_dict[model.name] = [history_callback, model]

    ###### Save Keras Model

    model.save(Path(__file__).parent / 'models/cold_system_model.h5')
    print('model saved')



    #confusion matrix


    corr_data = dataset_train
    corr_data['Measure'] = encoded_Y
    corr = corr_data.corr()
    heatmap = sns.heatmap(corr, xticklabels=list(dataset_train.columns[:]), yticklabels=list(dataset_train.columns[:]))
    plt.show()



'''
model = Sequential()
model.add(Dense(20, input_dim=(17), activation='relu')) #hidden layer hat 12 Möglichkeiten, input sind 8 Datasets
model.add(Dense(15, activation='relu')) #das ist das zweite hidden layer mit 8 Knoten
model.add(Dense(3, activation='softmax')) #output ist dann ein Knoten
model.summary()
model.compile(Adam(lr=0.0001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(x=X_train, y=Y_train, validation_data=(X_test, Y_test), batch_size=1, epochs=100, shuffle=True)

score = model.evaluate(X_test, Y_test, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])
'''
'''
test_samples = dataset_vali[:, :17]
test_labels = dataset_vali[:, 17]
scaled_train_samples = scaler.fit_transform(test_samples)

predictions = model.predict(x=test_samples, batch_size=1)

print(predictions)
'''