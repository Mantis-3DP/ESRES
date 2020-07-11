from tensorflow import keras
import numpy as np



def predict_problem(modelloca, X_test):
    model = keras.models.load_model(modelloca)
    predictions = model.predict(x=X_test, batch_size=1)
    prediction_measure = np.round(predictions[:, 1], 2)
    return prediction_measure