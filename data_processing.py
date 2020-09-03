import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sklearn.utils import shuffle


class prepped_data:

    def __init__(self, dataset_train, function_folder, possible_problems, feature_names, user_input, measures, *args):
        self.dataset_train = dataset_train
        self.function_folder = function_folder
        self.possible_problems = possible_problems
        self.feature_names = feature_names
        self.user_input = user_input
        self.measures = measures
        self.dropped = 0
        self.data_splitted = 0

    def drop_rows(self, chosen_problem):
        # removes the Datarows in which a specific problem is not present
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
        # for measure evaluation the user_input is a feature. This section adds it to the dataframe
        self.X_machine = np.hstack((self.X_machine, self.X_user))
        self.feature_names = np.hstack((self.feature_names, self.user_input))
        if self.data_splitted == 1:
            self.X_machine_split = np.hstack((self.X_machine_split, self.X_user_split))

    def get_data(self, *args):
        # create dataframe with train, val or test data
        if "train" in args:
            self.dataset_train = shuffle(self.dataset_train)
        if "test_known" in args or "train" in args:
            dataset_problems = self.dataset_train[self.possible_problems]
            self.dataset_measures = self.dataset_train[np.hstack(list(self.measures.values()))]
        dataset_machine = self.dataset_train[self.feature_names]
        dataset_user = self.dataset_train[self.user_input]

        scaler = MinMaxScaler(feature_range=(0, 1))
        if self.dropped == 0 and "train" in args:
            # scale train data and save the scaling function
            machine_scaled = scaler.fit_transform(dataset_machine)
            joblib.dump(scaler, str(self.function_folder) + '\\dataset_train_machine.gz')
            user_scaled = scaler.fit_transform(dataset_user)
            joblib.dump(scaler, str(self.function_folder) + '\\dataset_train_user.gz')
            measures_scaled = scaler.fit_transform(self.dataset_measures)
            joblib.dump(scaler, str(self.function_folder) + '\\dataset_train_measures.gz')
        else:
            # use scale of train data on test data
            scaler = joblib.load(str(self.function_folder) + '\\dataset_train_machine.gz')
            machine_scaled = scaler.transform(dataset_machine)
            scaler = joblib.load(str(self.function_folder) + '\\dataset_train_user.gz')
            user_scaled = scaler.transform(dataset_user)
            if "test_known" in args or "train" in args:
                scaler = joblib.load(str(self.function_folder) + '\\dataset_train_measures.gz')
                measures_scaled = scaler.transform(self.dataset_measures)
        if "train" in args:
            # split data into train and validation data
            self.X_machine, self.X_machine_split, self.X_user, self.X_user_split, y_problems, y_problems_split, self.Y_measures, self.Y_measures_split = train_test_split(
                machine_scaled, user_scaled, dataset_problems, measures_scaled, test_size=0.1)
            self.Y_problems, _ = self.hotencode(y_problems)
            self.Y_problems_split, self.n_classes_probs = self.hotencode(y_problems_split)
            self.n_classes_measures = 1
            self.data_splitted = 1

            # add collumn names back
            self.Y_measures_split = pd.DataFrame(data=self.Y_measures_split,
                                                 columns=list(self.dataset_measures.columns))
        else:
            self.X_machine = machine_scaled
            self.X_user = user_scaled
            if "test_known" in args:
                self.Y_problems = dataset_problems
                self.Y_measures = measures_scaled
                self.Y_measures = pd.DataFrame(data=self.Y_measures, columns=list(self.dataset_measures.columns))

        return

    def invers_scal(self, predictions):
        scaled_predictions = pd.DataFrame(columns=np.hstack(list(self.measures.values())))
        for measure in np.hstack(list(self.measures.values())):
            scaled_predictions[measure] = predictions[measure]
        scaler = joblib.load(str(self.function_folder) + '\\dataset_train_measures.gz')
        scaled_predictions = scaler.inverse_transform(scaled_predictions)
        scaled_predictions = pd.DataFrame(data=scaled_predictions, columns=np.hstack(list(self.measures.values())))
        for measure in np.hstack(list(self.measures.values())):
            predictions[measure] = np.array(scaled_predictions[measure])

        return predictions
