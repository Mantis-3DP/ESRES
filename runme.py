from create_model import create_all_models
from data_processing import datapreprocess_train, datapreprocess_test
from format_strings import show_predictions
from predict_measures import predict_measure
from pathlib import Path
import sys
# import seaborn as sb
# import matplotlib.pyplot as plt
# import numpy as np
# from ColdRoom import ColdRoom

run_arg = []
run_arg.append(sys.argv[1])
run_arg.append(sys.argv[2])

if run_arg[0] == 'create_models':
    # create models
    # link to data
    fileloca_train = Path(__file__).parent / "data/TrainData.csv"

    #das muss auch anders gelöst werden unten ist nochmal der gleiche Parameter
    num_measures = 8



    # create_model.py needs a class with an __init__ instead of following

    feature_names, measure_names, X_train, X_val, Y_train, Y_val, n_features, n_classes = datapreprocess_train(
        fileloca_train,
        num_measures)

    if run_arg[1] == 'all_models':
        for model_num, measure in enumerate(measure_names):
            create_all_models(X_train, X_val, Y_train[measure], Y_val[measure], n_features, n_classes[measure],
                              model_num)

    else:
        measure = measure_names[int(run_arg[1])]
        model_num = int(run_arg[1])
        create_all_models(X_train, X_val, Y_train[measure], Y_val[measure], n_features, n_classes[measure],
                          model_num)


elif run_arg[0] == 'test':
    fileloca_test = Path(__file__).parent / "data/TestData.csv"

    # das muss auch anders gelöst werden unten ist nochmal der gleiche Parameter
    num_measures = 8
    feature_names, measure_names, X_test, Y_test, n_features, n_classes = datapreprocess_test(fileloca_test,
                                                                                              num_measures)

    # looks redundant, is there a simpler way?
    predictions: dict = dict()
    for measure in measure_names:
        predictions[measure] = []

    for i in range(0, num_measures):
        modelloca = Path(__file__).parent / "models/cold_system_model_{}.h5".format(i)
        predictions[measure_names[i]] = predict_measure(modelloca, X_test)

    show_predictions(predictions, measure_names, Y_test, len(X_test))

elif run_arg[0] == 'corr':
    fileloca_test = Path(__file__).parent / "data/TestData.csv"

    # das muss auch anders gelöst werden unten ist nochmal der gleiche Parameter
    num_measures = 7
    feature_names, measure_names, X_test, Y_test, n_features, n_classes = datapreprocess_test(fileloca_test,
                                                                                              num_measures)
