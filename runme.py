from create_model import create_all_models
from data_processing import datapreprocess_train, datapreprocess_test, datapreprocess_user, datapreprocess_calc
from format_strings import show_top_predictions, show_predictions, show_user_predictions
from predict_measures import predict_measure
from pathlib import Path
import sys
import shap
from tensorflow import keras
import tensorflow as tf
import numpy as np

physical_devices = tf.config.list_physical_devices('GPU')
try:
  tf.config.experimental.set_memory_growth(physical_devices[0], True)
except:
  # Invalid device or cannot modify virtual devices once initialized.
  pass


run_arg = []
run_arg.append(sys.argv[1])
run_arg.append(sys.argv[2])
num_measures = 8
function_folder = Path(__file__).parent / "saved_functions"
fileloca_train = Path(__file__).parent / "Data/TrainData.csv"
fileloca_test = Path(__file__).parent / "Data/TestData.csv"
fileloca_user = Path(__file__).parent / "Data/UserFaulty.csv"


if run_arg[0] == 'create_models':
    # create models
    feature_names, measure_names, X_train, X_val, Y_train, Y_val, n_features, n_classes = datapreprocess_train(
        fileloca_train,
        num_measures,
        function_folder
    )

    if run_arg[1] == 'all_models':
        for model_num, measure in enumerate(measure_names):
            create_all_models(X_train, X_val, Y_train[measure], Y_val[measure], n_features, n_classes[measure], model_num)

    else:
        measure = measure_names[int(run_arg[1])]
        model_num = int(run_arg[1])
        create_all_models(X_train, X_val, Y_train[measure], Y_val[measure], n_features, n_classes[measure], model_num)



elif run_arg[0] == 'test' or run_arg[0] == 'user_room':


    feature_names, measure_names, X_test, Y_test, n_features, n_classes = datapreprocess_test(fileloca_test, num_measures, function_folder)
    if run_arg[0] == 'user_room':
        feature_names, measure_names, _, _, n_features, _ = datapreprocess_test(fileloca_test, num_measures, function_folder)
        _, X_test, _ = datapreprocess_user(fileloca_user, num_measures, function_folder)
    # looks redundant, is there a simpler way?
    predictions: dict = dict()
    for measure in measure_names:  #wenn man user_params nutzt hat man die measures nicht
        predictions[measure] = []

    for i in range(0, num_measures):
        modelloca = Path(__file__).parent / "models/cold_system_model_{}.h5".format(i)
        predictions[measure_names[i]] = predict_measure(modelloca, X_test)

    if run_arg[0] == 'test':
        if run_arg[1] == 'top':
            show_top_predictions(predictions, measure_names, Y_test, len(X_test))
        else:
            show_predictions(predictions, measure_names, Y_test, len(X_test))
    if run_arg[0] == 'user_room':
        show_user_predictions(predictions, measure_names, len(X_test))



elif run_arg[0] == 'shap': # used to find importance of features
    shap.initjs()
    modelloca = Path(__file__).parent / "models/cold_system_model_{}.h5".format(1)
    feature_names, measure_names, X_test, Y_test, n_features, n_classes = datapreprocess_test(fileloca_test,
                                                                                              num_measures,
                                                                                              function_folder)
    model = keras.models.load_model(modelloca)
    # explain the model's predictions using SHAP
    # (same syntax works for LightGBM, CatBoost, scikit-learn and spark models)
    explainer = shap.DeepExplainer(model, X_test)
    shap_values = explainer.shap_values(X_test)

    shap.summary_plot(shap_values, X_test, plot_type="bar")

if run_arg[0] == 'user_room' and run_arg[1] == 'similar':
    k = []
    measure_values = []
    for measure in measure_names:
        measure_values.append(predictions[measure][0])
    measure_array = np.array(measure_values)
    for m in range(0, len(measure_array)):
        measure_name_at_m = measure_names[m] # name of measure
        value_at_m = int(100 * measure_values[m]) # Prozent bei der jeweiligen Maßnahme
        if value_at_m > 60:
            k.append(m)
    print(k)
    _, _, X_train, _, Y_train, _, _, _, X, y_values = datapreprocess_calc(fileloca_train, num_measures, function_folder)

    for i in k:
        print(i)
        positiov = np.where(y_values[:, 7] == 1)[0]
        midX = X[positiov, 6].sum()/len(positiov)
        print(midX)