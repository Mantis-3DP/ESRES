from tensorflow import keras
import numpy as np



def predict_problem(model_loca, X_test, conti):
    model = keras.models.load_model(model_loca)
    predictions = model.predict(x=X_test)
    if conti == 0:
        prediction_measure = np.round(predictions[:, 1], 2)
    else:
        prediction_measure = predictions[:, :2]
    return prediction_measure