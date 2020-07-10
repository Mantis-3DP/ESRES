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
from ColdRoom import ColdRoom
from ColdRoom import generateRandomColdRooms
import joblib
import pandas as pd

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

    feature_names, measure_names, X_test, Y_test, n_features, n_classes = datapreprocess_test(fileloca_test, num_measures, function_folder)
    rel_feature_per_measure = []
    for i in range(0, len(feature_names)+1):
        shap.initjs()
        modelloca = Path(__file__).parent / "models/cold_system_model_{}.h5".format(i)
        model = keras.models.load_model(modelloca)
        # explain the model's predictions using SHAP
        # (same syntax works for LightGBM, CatBoost, scikit-learn and spark models)
        explainer = shap.DeepExplainer(model, X_test)
        shap_values = explainer.shap_values(X_test)

        shap.summary_plot(shap_values[1], X_test, plot_type="bar")
        importants_arr = np.mean(np.absolute(shap_values[1]), axis=0)
        top_value_positions = np.hstack(np.argwhere(importants_arr > 0.1))
        print(top_value_positions)
        rel_feature_per_measure.append(top_value_positions)
        #rel_feature_per_measure[i].append(top_value_positions)
    print(rel_feature_per_measure)
    if run_arg[1] == 'similar':
        feature_names, measure_names, X_train, X_val, Y_train, Y_val, n_features, n_classes = datapreprocess_train(
            fileloca_train,
            num_measures,
            function_folder
        )
        _, X_test, _ = datapreprocess_user(fileloca_user, num_measures, function_folder)
        X_test[0, i]
        X_train[:, i]


# faulty needs an update, doesnt do what i have hoped
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

elif run_arg[0] == 'crTest':
    cr = ColdRoom(mode="user", length=5, width=4, height=3, t_person=8, n_person=3, load_fan_electrical=200)
    # print(cr.volume)
    # print(cr.n_person)
    # print(cr.problems)
    # print(cr.createDataRow()) 
    df_temp = cr.createDataFrame()
    print(df_temp)

    num_measures = 8
    predictions: dict = dict()

    measure_names = ["Fan consumes too much energy", "Installed Load too high", "Insulation insufficient",
                     "Light consumes too much energy", "Light is on for too long", "People too long in the Room",
                     "To many people in the Room", "none"]

    for measure in measure_names:
        predictions[measure] = []

    for i in range(0, num_measures):
        modelloca = Path(__file__).parent / "models/cold_system_model_{}.h5".format(i)
        scaler = joblib.load(str(function_folder) + '\\scaler.gz')
        X = df_temp.iloc[[0]]
        X_test = scaler.transform(X)
        predictions[measure_names[i]] = predict_measure(modelloca, X_test)

    for measure in measure_names:
        print(measure)
        print(predictions[measure])
        

    # Add top 3 predictions to cr.problems
    topProblems = []
    for measure in measure_names:
        if predictions[measure] > 0.5 : 
            topProblems.append(measure)
    
    # TEMPORARILY SOLVING THE "none" PROBLEM:
    # del topProblems[(len(topProblems)-1)]

    # print(topProblems)
    print("######################### CALCULATE SAVING POTENTIALS #########################")
    cr.calculateDefaultValues() 
    cr.problems = topProblems # Bei Bedarf so anpassen, dass alle Probleme in Klasse gespeichert sind auch wenn die Prozentzahl niedrig ist, dann dort ausfiltern 
    # cr.calculatebestCaseLoads()

    cr.add_measure_columns()
    # Use function to calcuate diff
    # print out possible diff in Euros and BestCase


elif run_arg[0] == 'generateData':
    # Liste mit ColdRoom Instanzen -> amount bestimmt Anzahl der generierten Daten, "mode2 ="setup" sorgt dafür, dass nur fehlerhafte daten mit maßnahmen und ohne Probleme generiert werden!" 
    coldRooms = generateRandomColdRooms(amount=10, csv=False, filename="testNEW", fault_share=1, object=True, mode2="setup") 
    # Dateiname für generierte Daten
    filename = "Data/" + "MeasureTestData" + ".csv"
    # DataFrame für ColdRooms mit measure
    df_ColdRoomsInclMeasures = pd.DataFrame()
    # Schleife über alle ColdRooms in Coldroom
    for cr in coldRooms: 

        df_temp = cr.createDataFrame()
        # print(df_temp)
        num_measures = 8
        predictions: dict = dict()

        measure_names = ["Fan consumes too much energy", "Installed Load too high", "Insulation insufficient",
                     "Light consumes too much energy", "Light is on for too long", "People too long in the Room",
                     "To many people in the Room", "none"]

        for measure in measure_names:
            predictions[measure] = []

        for i in range(0, num_measures):
            modelloca = Path(__file__).parent / "models/cold_system_model_{}.h5".format(i)
            scaler = joblib.load(str(function_folder) + '\\scaler.gz')
            X = df_temp.iloc[[0]]
            X_test = scaler.transform(X)
            predictions[measure_names[i]] = predict_measure(modelloca, X_test)

        topProblems = []
        for measure in measure_names:
            if predictions[measure] > 0.5 : 
                topProblems.append(measure)
        print("################ Top Problems ################")
        print(topProblems)
        print("calculatingDefaultValues...")
        cr.calculateDefaultValues() 
        print("adding Top Problems to ColdRoom-Instance... ")
        cr.problems = topProblems
        print("adding measure columns...")
        #JoinDataFrames
        df_final = df_temp.join(cr.add_measure_columns()) 
        print(df_final)
        df_ColdRoomsInclMeasures = pd.concat([df_ColdRoomsInclMeasures, df_final], ignore_index=True)

    if run_arg[1] == 'csv':
        print(df_ColdRoomsInclMeasures)
        exportPath = Path(__file__).parent / filename
        df_ColdRoomsInclMeasures.to_csv(exportPath, index=False)
        temp = "Saved Data as csv at " + str(exportPath)
        pass
    else: 
        print(df_ColdRoomsInclMeasures)




    pass