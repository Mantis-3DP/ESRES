import pandas as pd
import numpy as np
from pathlib import Path
from tensorflow import keras
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, MinMaxScaler


def preprocess_cold_data():
    fileloca_test = Path(__file__).parent / "data_sets/test_transpose.csv"
    dataset_test = pd.read_csv(fileloca_test)
    dataset_test_values = dataset_test.values
    X_test = dataset_test_values[:, :-1]
    y_test = dataset_test_values[:, -1]
    encoder_test = LabelEncoder()
    encoder_test.fit(y_test)
    encoded_Y_test = encoder_test.transform(y_test)
    enc_test = OneHotEncoder()
    Y_test = enc_test.fit_transform(y_test[:, np.newaxis]).toarray()
    scaler = MinMaxScaler(feature_range=(0, 1))
    X_scaled_test = scaler.fit_transform(X_test)
    return X_scaled_test, Y_test

def measure_names():
    fileloca_train = Path(__file__).parent / "data_sets/samleDataRefriRoom_transpose_new.csv"
    last_col = len(pd.read_csv(fileloca_train, nrows=1).columns)
    dataset_train = pd.read_csv(fileloca_train, usecols=[last_col-1]).values
    names = pd.Categorical(np.hstack(dataset_train)).categories
    return names









X_scaled_test, _ = preprocess_cold_data()

model = keras.models.load_model(Path(__file__).parent / 'models/cold_system_model.h5')

predictions = model.predict(x=X_scaled_test, batch_size=1, verbose=0)
names = measure_names()

stringold = ''
for t in range(0, len(predictions)):
    stringold = 'Test Nr. ' + str(t)
    for n in range(0, len(predictions)):
        stringold = stringold + ' ' + names[n] + ' ' + '(' '%s%%' % str(round(predictions[t, n]*100, 0)) + ')'
    print(stringold)
rounded_predictions = np.argmax(predictions, axis=-1)










'''

print('highest rated measures for test scenarios are:')
for i in rounded_predictions:
    print(names[i])
'''