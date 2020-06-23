import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split


def datapreprocess_train(fileloca_train, num_measures):
    dataset_train = pd.read_csv(fileloca_train)
    dataset_train_values = dataset_train.values
    feature_names = list(dataset_train.columns[:-1])
    measure_names = list(dataset_train.columns[-num_measures:])
    X = dataset_train_values[:, :-num_measures]
    y_values = dataset_train_values[:, -num_measures:]

    X, y_values = shuffle(X, y_values)

    scaler = MinMaxScaler(feature_range=(0, 1))
    X_scaled = scaler.fit_transform(X)
    X_train, X_val, y_train_split, y_val_split = train_test_split(X_scaled, y_values, test_size=0.1, random_state=2)

    # looks redundant, is there a simpler way?
    y_train: dict = dict()
    Y_train: dict = dict()
    y_val: dict = dict()
    Y_val: dict = dict()
    n_classes: dict = dict()
    for measure in measure_names:
        y_train[measure] = []
        Y_train[measure] = []
        y_val[measure] = []
        Y_val[measure] = []
        n_classes[measure] = 0

    for t in range(0, num_measures):
        y_train[measure_names[t]] = np.array(y_train_split[:, t])
        y_val[measure_names[t]] = np.array(y_val_split[:, t])

        # One hot encoding
        enc = OneHotEncoder()
        Y_train[measure_names[t]] = enc.fit_transform(y_train[measure_names[t]][:, np.newaxis]).toarray()
        Y_val[measure_names[t]] = enc.fit_transform(y_val[measure_names[t]][:, np.newaxis]).toarray()
        n_classes[measure_names[t]] = len(Y_train[measure_names[0]][0])

    n_features = X.shape[1]

    return feature_names, measure_names, X_train, X_val, Y_train, Y_val, n_features, n_classes


def datapreprocess_test(fileloca_train, num_measures):
    dataset_train = pd.read_csv(fileloca_train)
    dataset_train_values = dataset_train.values
    feature_names = list(dataset_train.columns[:-1])
    measure_names = list(dataset_train.columns[-num_measures:])
    X = dataset_train_values[:, :-num_measures]
    y_values = dataset_train_values[:, -num_measures:]

    # X, y_values = shuffle(X, y_values)

    scaler = MinMaxScaler(feature_range=(0, 1))
    X_test = scaler.fit_transform(X)

    # looks redundant, is there a simpler way?
    y_test: dict = dict()
    Y_test: dict = dict()
    n_classes: dict = dict()
    for measure in measure_names:
        y_test[measure] = []
        Y_test[measure] = []
        n_classes[measure] = 0

    for t in range(0, num_measures):
        y_test[measure_names[t]] = np.array(y_values[:, t])
        # One hot encoding
        enc = OneHotEncoder()
        Y_test[measure_names[t]] = enc.fit_transform(y_test[measure_names[t]][:, np.newaxis]).toarray()
        #Labels per measure
        n_classes[measure_names[t]] = len(Y_test[measure_names[0]][0])

    n_features = X.shape[1]

    return feature_names, measure_names, X_test, Y_test, n_features, n_classes
