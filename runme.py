from create_model import create_all_models
from data_processing import datapreprocess_train, datapreprocess_test, datapreprocess_user, datapreprocess_calc
from format_strings import show_top_predictions, show_predictions, show_user_predictions
from predict_problems import predict_problem
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
for element in sys.argv:
    run_arg.append(element)


function_folder = Path(__file__).parent / "saved_functions"
fileloca_train = Path(__file__).parent / "Data/TrainData.csv"
fileloca_test = Path(__file__).parent / "Data/TestData.csv"
fileloca_user = Path(__file__).parent / "Data/UserFaulty.csv"
fileloca_problem = Path(__file__).parent / "Data/ProblemTestData.csv"
possible_problems = [
    "Fan consumes too much energy",
    "Insulation insufficient",
    "Light consumes too much energy",
    "Light is on for too long",
    "People too long in the Room",
    "To many people in the Room",
    "Installed Load too high",
    "none"
]
print(possible_problems)
num_problems = len(possible_problems)


if 'create_models' in run_arg:
    # create models
    feature_names, problem_names, X_train, X_val, Y_train, Y_val, n_features, n_classes = datapreprocess_train(
        fileloca_train,
        num_problems,
        function_folder
    )

    if 'all_models' in run_arg:
        for model_num, problem in enumerate(problem_names):
            create_all_models(X_train, X_val, Y_train[problem], Y_val[problem], n_features, n_classes[problem], model_num)
    else:
        new_list = []
        for value in run_arg:
            try:
                new_list.append(int(value))
            except ValueError:
                continue
        for i in new_list:
            problem = problem_names[i]
            model_num = i
            create_all_models(X_train, X_val, Y_train[problem], Y_val[problem], n_features, n_classes[problem], model_num)


elif 'test' in run_arg or 'user_room'in run_arg:


    feature_names, problem_names, X_test, Y_test, n_features, n_classes = datapreprocess_test(fileloca_test, num_problems, function_folder)
    if 'user_room' in run_arg:
        feature_names, problem_names, _, _, n_features, _ = datapreprocess_test(fileloca_test, num_problems, function_folder)
        _, X_test, _ = datapreprocess_user(fileloca_user, num_problems, function_folder)
    # looks redundant, is there a simpler way?
    predictions: dict = dict()
    for problem in problem_names:  #wenn man user_params nutzt hat man die problems nicht
        predictions[problem] = []

    for i in range(0, num_problems):
        modelloca = Path(__file__).parent / "models/cold_system_model_{}.h5".format(i)
        predictions[problem_names[i]] = predict_problem(modelloca, X_test)

    if 'test' in run_arg:
        if 'top' in run_arg:
            show_top_predictions(predictions, problem_names, Y_test, len(X_test))
        else:
            show_predictions(predictions, problem_names, Y_test, len(X_test))
    if 'user_room' in run_arg:
        show_user_predictions(predictions, problem_names, len(X_test))



elif 'shap' in run_arg: # used to find importance of features

    feature_names, problem_names, X_test, Y_test, n_features, n_classes = datapreprocess_test(fileloca_test, num_problems, function_folder)
    rel_feature_per_problem = []
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
        rel_feature_per_problem.append(top_value_positions)
        #rel_feature_per_problem[i].append(top_value_positions)
    print(rel_feature_per_problem)
    if 'similar' in run_arg:
        feature_names, problem_names, X_train, X_val, Y_train, Y_val, n_features, n_classes = datapreprocess_train(
            fileloca_train,
            num_problems,
            function_folder
        )
        _, X_test, _ = datapreprocess_user(fileloca_user, num_problems, function_folder)
        X_test[0, i]
        X_train[:, i]


# faulty needs an update, doesnt do what i have hoped
if 'user_room' in run_arg and 'similar' in run_arg:
    k = []
    problem_values = []
    for problem in problem_names:
        problem_values.append(predictions[problem][0])
    problem_array = np.array(problem_values)
    for m in range(0, len(problem_array)):
        problem_name_at_m = problem_names[m] # name of problem
        value_at_m = int(100 * problem_values[m]) # Prozent bei der jeweiligen Maßnahme
        if value_at_m > 60:
            k.append(m)
    print(k)
    _, _, X_train, _, Y_train, _, _, _, X, y_values = datapreprocess_calc(fileloca_train, num_problems, function_folder)

    for i in k:
        print(i)
        positiov = np.where(y_values[:, 7] == 1)[0]
        midX = X[positiov, 6].sum()/len(positiov)
        print(midX)

elif 'crTest' in run_arg:
    cr = ColdRoom(mode="user", length=5, width=4, height=3, t_person=8, n_person=3, load_fan_electrical=200)
    # print(cr.volume)
    # print(cr.n_person)
    # print(cr.problems)
    # print(cr.createDataRow()) 
    df_temp = cr.createDataFrame()
    print(df_temp)

    num_problems = 8
    predictions: dict = dict()

    for problem in possible_problems:
        predictions[problem] = []

    for i in range(0, num_problems):
        modelloca = Path(__file__).parent / "models/cold_system_model_{}.h5".format(i)
        scaler = joblib.load(str(function_folder) + '\\scaler.gz')
        X = df_temp.iloc[[0]]
        X_test = scaler.transform(X)
        predictions[possible_problems[i]] = predict_problem(modelloca, X_test)

    for problem in possible_problems:
        print(problem)
        print(predictions[problem])
        

    # Add top 3 predictions to cr.problems
    topProblems = []
    for problem in possible_problems:
        if predictions[problem] > 0.5 :
            topProblems.append(problem)
    
    # TEMPORARILY SOLVING THE "none" PROBLEM:
    # del topProblems[(len(topProblems)-1)]

    # print(topProblems)
    print("######################### CALCULATE SAVING POTENTIALS #########################")
    cr.calculateDefaultValues() 
    cr.problems = topProblems # Bei Bedarf so anpassen, dass alle Probleme in Klasse gespeichert sind auch wenn die Prozentzahl niedrig ist, dann dort ausfiltern 
    # cr.calculatebestCaseLoads()

    cr.add_problem_columns()
    # Use function to calcuate diff
    # print out possible diff in Euros and BestCase


elif 'generateData' in run_arg:
    # Liste mit ColdRoom Instanzen -> amount bestimmt Anzahl der generierten Daten, "mode2 ="setup" sorgt dafür, dass nur fehlerhafte daten mit maßnahmen und ohne Probleme generiert werden!" 
    coldRooms = generateRandomColdRooms(amount=10000, csv=False, filename="testNEW", fault_share=1, object=True, mode2="setup")
    # Dateiname für generierte Daten
    filename = "Data/" + "ProblemTestData" + ".csv"
    # DataFrame für ColdRooms mit problem
    df_ColdRoomsInclMeasures = pd.DataFrame()



    # Schleife über alle ColdRooms in Coldroom
    for cr in coldRooms: 

        df_temp = pd.DataFrame([cr.dataRow[:-1]], columns=[
            "load_transmission",
            "load_people",
            "n_person",
            "load_light",
            "load_fan",
            "load_total",
            "load_installed",
        ])
        temp_array = []
        print(possible_problems)
        for problem in possible_problems:
            print(problem)
            if problem in cr.dataRow[-1]: temp_array.append(1)
            else: temp_array.append(0)
        df_problems = pd.DataFrame([temp_array], columns=possible_problems)
        df_mid = df_temp.join(df_problems)

        # Wird nicht gebraucht, die Probleme sind bereits im coldRoom hinterlegt. Der predict Vorgang schluckt die Recourcen
        """
        predictions: dict = dict()
        for problem in problem_names:
            predictions[problem] = []

        for i in range(0, num_problems):
            modelloca = Path(__file__).parent / "models/cold_system_model_{}.h5".format(i)
            scaler = joblib.load(str(function_folder) + '\\scaler.gz')
            X = df_temp.iloc[[0]]
            X_test = scaler.transform(X)
            predictions[problem_names[i]] = predict_problem(modelloca, X_test)
        """

        # die Probleme sind bereits hinterlegt
        """
        topProblems = []
        for problem in problem_names:
            if predictions[problem] > 0.5 :
                topProblems.append(problem)
        """


        # print("################ Top Problems ################")
        # print("calculatingDefaultValues...")
        cr.calculateDefaultValues() 
        # print("adding Top Problems to ColdRoom-Instance... ")
        # print("adding measure columns...")
        #JoinDataFrames
        df_final = df_mid.join(cr.add_measure_columns())
        df_ColdRoomsInclMeasures = pd.concat([df_ColdRoomsInclMeasures, df_final], ignore_index=True)

    if 'csv' in run_arg:
        # print(df_ColdRoomsInclMeasures)
        exportPath = Path(__file__).parent / filename
        df_ColdRoomsInclMeasures.to_csv(exportPath, index=False)
        temp = "Saved Data as csv at " + str(exportPath)
        pass


elif 'predict_measure' in run_arg:




    pass