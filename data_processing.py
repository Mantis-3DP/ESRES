import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
import joblib

def datapreprocess_train(fileloca_train, num_problems, function_folder):
    dataset_train = pd.read_csv(fileloca_train)
    dataset_train_values = dataset_train.values
    feature_names = list(dataset_train.columns[:-1])
    problem_names = list(dataset_train.columns[-num_problems:])
    X = dataset_train_values[:, :-num_problems]
    y_values = dataset_train_values[:, -num_problems:]

    X, y_values = shuffle(X, y_values)

    scaler = MinMaxScaler(feature_range=(0, 1))
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, str(function_folder)+'\\scaler.gz')
    X_train, X_val, y_train_split, y_val_split = train_test_split(X_scaled, y_values, test_size=0.1, random_state=2)

    # looks redundant, is there a simpler way?
    y_train: dict = dict()
    Y_train: dict = dict()
    y_val: dict = dict()
    Y_val: dict = dict()
    n_classes: dict = dict()
    for problem in problem_names:
        y_train[problem] = []
        Y_train[problem] = []
        y_val[problem] = []
        Y_val[problem] = []
        n_classes[problem] = 0

    for t in range(0, num_problems):
        y_train[problem_names[t]] = np.array(y_train_split[:, t])
        y_val[problem_names[t]] = np.array(y_val_split[:, t])

        # One hot encoding
        enc = OneHotEncoder()
        Y_train[problem_names[t]] = enc.fit_transform(y_train[problem_names[t]][:, np.newaxis]).toarray()
        Y_val[problem_names[t]] = enc.fit_transform(y_val[problem_names[t]][:, np.newaxis]).toarray()
        n_classes[problem_names[t]] = len(Y_train[problem_names[0]][0])

    n_features = X.shape[1]

    return feature_names, problem_names, X_train, X_val, Y_train, Y_val, n_features, n_classes


def datapreprocess_test(fileloca_train, num_problems, function_folder):
    dataset_train = pd.read_csv(fileloca_train)
    dataset_train_values = dataset_train.values
    feature_names = list(dataset_train.columns[:-num_problems])
    problem_names = list(dataset_train.columns[-num_problems:])
    X = dataset_train_values[:, :-num_problems]
    y_values = dataset_train_values[:, -num_problems:]

    X, y_values = shuffle(X, y_values)

    scaler = joblib.load(str(function_folder)+'\\scaler.gz')
    X_test = scaler.transform(X)

    # looks redundant, is there a simpler way?
    y_test: dict = dict()
    Y_test: dict = dict()
    n_classes: dict = dict()
    for problem in problem_names:
        y_test[problem] = []
        Y_test[problem] = []
        n_classes[problem] = 0

    for t in range(0, num_problems):
        y_test[problem_names[t]] = np.array(y_values[:, t])
        # One hot encoding
        enc = OneHotEncoder()
        Y_test[problem_names[t]] = enc.fit_transform(y_test[problem_names[t]][:, np.newaxis]).toarray()
        #Labels per problem
        n_classes[problem_names[t]] = len(Y_test[problem_names[0]][0])

    n_features = X.shape[1]

    return feature_names, problem_names, X_test, Y_test, n_features, n_classes

def datapreprocess_user(fileloca_user, num_problems, function_folder):
    num_problems = 8  # this method has do change, it must be calculated automatically
    dataset_train = pd.read_csv(fileloca_user)
    dataset_train_values = dataset_train.values
    feature_names = list(dataset_train.columns[:-num_problems])

    ############################ die 7 muss weg
    X = dataset_train_values[:, :7]   ## das muss verändert werden

    # X, y_values = shuffle(X, y_values)

    scaler = joblib.load(str(function_folder) + '\\scaler.gz')
    X_user = scaler.transform(X)


    n_features = X.shape[1]

    return feature_names, X_user, n_features


def datapreprocess_calc(fileloca_train, num_problems, function_folder):
    dataset_train = pd.read_csv(fileloca_train)
    dataset_train_values = dataset_train.values
    feature_names = list(dataset_train.columns[:-1])
    problem_names = list(dataset_train.columns[-num_problems:])
    X = dataset_train_values[:, :-num_problems]
    y_values = dataset_train_values[:, -num_problems:]

    X_s, y_values = shuffle(X, y_values)

    scaler = MinMaxScaler(feature_range=(0, 1))
    X_scaled = scaler.fit_transform(X_s)
    joblib.dump(scaler, str(function_folder)+'\\scaler.gz')
    X_train, X_val, y_train_split, y_val_split = train_test_split(X_scaled, y_values, test_size=0.1, random_state=2)

    # looks redundant, is there a simpler way?
    y_train: dict = dict()
    Y_train: dict = dict()
    y_val: dict = dict()
    Y_val: dict = dict()
    n_classes: dict = dict()
    for problem in problem_names:
        y_train[problem] = []
        Y_train[problem] = []
        y_val[problem] = []
        Y_val[problem] = []
        n_classes[problem] = 0

    for t in range(0, num_problems):
        y_train[problem_names[t]] = np.array(y_train_split[:, t])
        y_val[problem_names[t]] = np.array(y_val_split[:, t])

        # One hot encoding
        enc = OneHotEncoder()
        Y_train[problem_names[t]] = enc.fit_transform(y_train[problem_names[t]][:, np.newaxis]).toarray()
        Y_val[problem_names[t]] = enc.fit_transform(y_val[problem_names[t]][:, np.newaxis]).toarray()
        n_classes[problem_names[t]] = len(Y_train[problem_names[0]][0])

    n_features = X.shape[1]

    return feature_names, problem_names, X_train, X_val, Y_train, Y_val, n_features, n_classes, X, y_train_split