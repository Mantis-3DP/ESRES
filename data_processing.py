import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
import joblib


class prepped_data:

    def __init__(self, dataset_train, function_folder, possible_problems, feature_names, user_input, measures, *args):
        self.dataset_train = dataset_train
        self.function_folder = function_folder
        self.possible_problems = possible_problems
        self.feature_names = feature_names
        self.user_input = user_input
        self.measures = measures
        self.dropped = 0


    def drop_rows(self, chosen_problem):
        # removes the Datarows in which a problem is not present
        self.dataset_train = self.dataset_train[self.dataset_train[chosen_problem] == 1]
        self.dropped = 1


    def hotencode(self, y_split):
        y: dict = dict()
        Y: dict = dict()
        n_classes: dict = dict()
        enc = OneHotEncoder()
        for problem in self.possible_problems:
            y[problem] = []
            Y[problem] = []
            n_classes[problem] = 0
            y[problem] = y_split[problem]
            Y[problem] = enc.fit_transform(y[problem][:, np.newaxis]).toarray()
            n_classes[problem] = len(Y[problem][0])

        return Y, n_classes

    def append_user(self):
        self.X_machine = np.hstack((self.X_machine, self.X_user))
        self.X_machine_split = np.hstack((self.X_machine_split, self.X_user_split))
        self.feature_names = np.hstack((self.feature_names, self.user_input))



    def get_data(self, type):
        # type asks if data is used for training or testing w/ unknown Y or testing w/ known Y
        if type == "train":
            self.dataset_train = shuffle(self.dataset_train)
        if type == "test_known" or type == "train":
            dataset_problems = self.dataset_train[self.possible_problems]
            dataset_measures = self.dataset_train[np.hstack(list(self.measures.values()))]
        dataset_machine = self.dataset_train[self.feature_names]
        dataset_user = self.dataset_train[self.user_input]

        scaler = MinMaxScaler(feature_range=(0, 1))
        if self.dropped == 0 or type == "train":
            # could also be solved with a loop TODO
            train_machine_scaled = scaler.fit_transform(dataset_machine)
            joblib.dump(scaler, str(self.function_folder) + '\\dataset_train_machine.gz')
            train_user_scaled = scaler.fit_transform(dataset_user)
            joblib.dump(scaler, str(self.function_folder) + '\\dataset_train_user.gz')
            train_measures_scaled = scaler.fit_transform(dataset_measures)
            joblib.dump(scaler, str(self.function_folder) + '\\dataset_train_measures.gz')
        else:
            scaler = joblib.load(str(self.function_folder) + '\\dataset_train_machine.gz')
            train_machine_scaled = scaler.transform(dataset_machine)
            scaler = joblib.load(str(self.function_folder) + '\\dataset_train_user.gz')
            train_user_scaled = scaler.transform(dataset_user)
            if type == "test_known":
                scaler = joblib.load(str(self.function_folder) + '\\dataset_train_measures.gz')
                measures_scaled = scaler.transform(dataset_measures)
        if type == "train":
            self.X_machine, self.X_machine_split, self.X_user, self.X_user_split, y_problems, y_problems_split, self.Y_measures, self.Y_measures_split = train_test_split(
                train_machine_scaled, train_user_scaled, dataset_problems, train_measures_scaled, test_size=0.1)
            self.Y_problems, _ = self.hotencode(y_problems)
            self.Y_problems_split, self.n_classes = self.hotencode(y_problems_split)
        else:
            self.X_machine = train_machine_scaled
            self.X_user = train_user_scaled
            if type == "test_known":
                self.Y_problems = dataset_problems
                self.Y_measures = measures_scaled



        return



