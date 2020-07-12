import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
import joblib


class prepped_data:

    def __init__(self, dataset_train, function_folder, possible_problems, feature_names, user_input, measures, num_problems, num_features, num_measure, num_user_input):
        self.dataset_train = dataset_train


        self.dataset_train_machine = self.dataset_train[feature_names]
        self.dataset_train_user = self.dataset_train[user_input]
        self.dataset_train_problems = self.dataset_train[possible_problems]
        self.dataset_train_measures = self.dataset_train[np.hstack(measures.values())]

        scaler = MinMaxScaler(feature_range=(0, 1))
        self.train_machine_scaled = scaler.fit_transform(self.dataset_train_machine)
        joblib.dump(scaler, str(function_folder) + '\\dataset_train_machine.gz')
        self.train_user_scaled = scaler.fit_transform(self.dataset_train_user)
        joblib.dump(scaler, str(function_folder) + '\\dataset_train_user.gz')
        self.train_measures_scaled = scaler.fit_transform(self.dataset_train_measures)
        joblib.dump(scaler, str(function_folder) + '\\dataset_train_measures.gz')


    def drop_rows(self):
        self.dataset_train = self.dataset_train[]
        indexNames = self.dataset_train[self.dataset_train['Fan consumes too much energy'] == '0'].index
        # Delete these row indexes from dataFrame
        self.dataset_train.drop(indexNames, inplace=True)
        print('ausgeführt')







"""


        # dataframe als dic zusammensetzen

        X_train_dataset = pd.DataFrame()
        X_train_dataset.join(train_machine_scaled)
        X_train_dataset.join(train_user_scaled)
        Y_train_dataset = pd.DataFrame()
        Y_train_dataset.join()
        Y_train_dataset.join(train_machine_scaled)
        Y_train_dataset.join(train_measures_scaled)



        dataset_train_values = dataset_train.values
        X = dataset_train_values[:, :num_features]
        y_values = dataset_train_values[:, num_features:num_features+num_problems]

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

        return  X_machine_train, X_machine_val, Y_machine_train, Y_machine_val
"""