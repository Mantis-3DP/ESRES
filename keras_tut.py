import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix
import itertools
import matplotlib.pyplot as plt
from pandas.plotting import scatter_matrix
from matplotlib import pyplot
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from keras.utils import np_utils
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, MinMaxScaler
from sklearn.pipeline import Pipeline
from pandas import read_csv
from pathlib import Path
from sklearn.utils import shuffle
from sklearn import preprocessing
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Activation, Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import categorical_crossentropy
from sklearn import svm, datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import plot_confusion_matrix
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt  # doctest: +SKIP
from sklearn.datasets import make_classification
from sklearn.metrics import plot_confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import scikitplot as skplt
from keras.callbacks import TensorBoard

def scatter_plot():
    # Visualize the data sets
    plt.figure(figsize=(16, 6))
    plt.subplot(1, 2, 1)
    for target, target_name in enumerate(names):
        X_plot = X[y == target]
        plt.plot(X_plot[:, 0], X_plot[:, 1], linestyle='none', marker='o', label=target_name)
    plt.xlabel(feature_names[0])
    plt.ylabel(feature_names[1])
    plt.axis('equal')
    plt.legend();

    plt.subplot(1, 2, 2)
    for target, target_name in enumerate(names):
        X_plot = X[y == target]
        plt.plot(X_plot[:, 2], X_plot[:, 3], linestyle='none', marker='o', label=target_name)
    plt.xlabel(feature_names[2])
    plt.ylabel(feature_names[3])
    plt.axis('equal')
    plt.legend()



def create_custom_model(input_dim, output_dim, nodes, n=2, name='model'):
    def create_model():
        # Create model
        model = Sequential(name=name)
        for i in range(n):
            model.add(Dense(nodes, input_dim=input_dim, activation='relu'))
        model.add(Dense(output_dim, activation='softmax'))

        # Compile model
        model.compile(loss='categorical_crossentropy',
                      optimizer='adam',
                      metrics=['accuracy'])
        return model
    return create_model


#muss ich noch scalen
fileloca_train = Path(__file__).parent / "data_sets/samleDataRefriRoom_transpose.csv"
fileloca_test = Path(__file__).parent / "data_sets/validate_transpose.csv"
dataset_train = pd.read_csv(fileloca_train)
dataset_vali = pd.read_csv(fileloca_test)

dataset_train_values = dataset_train.values
dataset_vali_values = dataset_vali.values

feature_names = list(dataset_train.columns[:-1])

X = dataset_train_values[:, :17]
y = dataset_train_values[:, 17]

names = pd.Categorical(y).categories

encoder = LabelEncoder()
encoder.fit(y)

encoded_Y = encoder.transform(y)
# One hot encoding
enc = OneHotEncoder()
Y = enc.fit_transform(y[:, np.newaxis]).toarray()

train_samples, train_labels = shuffle(X, Y)
scaler = MinMaxScaler(feature_range=(0, 1))
X_scaled= scaler.fit_transform(train_samples)

X_train, X_test, Y_train, Y_test = train_test_split(
    X_scaled, Y, test_size=0.5, random_state=2)

n_features = X.shape[1]
n_classes = Y.shape[1]





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
test_samples = dataset_vali[:, :17]
test_labels = dataset_vali[:, 17]
scaled_train_samples = scaler.fit_transform(test_samples)

predictions = model.predict(x=test_samples, batch_size=1)

print(predictions)

#mehr als zwei Maßnahmen als Lösung
#

models = [create_custom_model(n_features, n_classes, 20, i, 'model_{}'.format(i))
          for i in range(1, 4)]

for create_model in models:
    create_model().summary()

history_dict = {}

# TensorBoard Callback
cb = TensorBoard()

for create_model in models:
    model = create_model()
    print('Model name:', model.name)
    history_callback = model.fit(X_train, Y_train,
                                 batch_size=1,
                                 epochs=50,
                                 verbose=0,
                                 validation_data=(X_test, Y_test),
                                 callbacks=[cb])
    score = model.evaluate(X_test, Y_test, verbose=0)
    print('Test loss:', score[0])
    print('Test accuracy:', score[1])

    history_dict[model.name] = [history_callback, model]




'''