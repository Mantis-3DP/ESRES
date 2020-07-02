from create_model import create_all_models
from data_processing import datapreprocess_train, datapreprocess_test, datapreprocess_user
from format_strings import show_top_predictions, show_predictions, show_user_predictions
from predict_measures import predict_measure
from pathlib import Path
import sys




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


    feature_names, measure_names, X_test, Y_test, n_features, n_classes = datapreprocess_test(fileloca_test, num_measures)
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
        show_user_predictions(predictions, measure_names)



