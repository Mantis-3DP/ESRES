from create_model import create_all_models
from data_processing import  datapreprocess_test, datapreprocess_user
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
print(run_arg)


function_folder = Path(__file__).parent / "saved_functions"
fileloca_train = Path(__file__).parent / "Data/ProblemTestData.csv"
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
feature_names = [
    "load_transmission",
    "load_people",
    "n_person",
    "load_light",
    "load_fan",
    "load_total",
    "load_installed",
    ]


num_problems = len(possible_problems)
num_features = len(feature_names)
num_measure = 4


if 'create_models' in run_arg:
    # create models
    feature_names, problem_names, X_machine_train, X_machine_val, X_user_train, X_user_val, Y_problem_train, Y_problem_val, Y_measures_train, Y_measures_val = datapreprocess_train(
        fileloca_train,
        num_problems,
        num_features,
        num_measure,
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
    if 'measure_models' in run_arg:
        pass



elif 'generateData' in run_arg:
    # Liste mit ColdRoom Instanzen -> amount bestimmt Anzahl der generierten Daten, "mode2 ="setup" sorgt dafür, dass nur fehlerhafte daten mit maßnahmen und ohne Probleme generiert werden!" 
    coldRooms = generateRandomColdRooms(amount=10000, csv=False, filename="testNEW", fault_share=1, object=True)
    # Dateiname für generierte Daten
    filename = "Data/" + "ProblemTestData" + ".csv"
    # DataFrame für ColdRooms mit problem
    df_ColdRoomsInclMeasures = pd.DataFrame()



    # Schleife über alle ColdRooms in Coldroom
    for cr in coldRooms: 
        # DATA PREPROCESSING 
        # sorgt dafür, dass alle problem spalten existieren und jede zelle in jeder zeile mit 0 oder 1 gefüllt ist 
        df_temp = pd.DataFrame([cr.dataRow[:-1]], columns=feature_names)
        temp_array = []
        for problem in possible_problems:
            if problem in cr.dataRow[-1]: 
                temp_array.append(1)
            else: 
                temp_array.append(0)
        df_problems = pd.DataFrame([temp_array], columns=possible_problems)
        df_mid = df_temp.join(df_problems)


        # print("################ Top Problems ################")
        # print("calculatingDefaultValues...")
        cr.calculateDefaultValues() 
        # print("adding Top Problems to ColdRoom-Instance... ")
        # print("adding measure columns...")
        #JoinDataFrames
        df_final = df_mid.join(cr.add_measure_columns())
        df_ColdRoomsInclMeasures = pd.concat([df_ColdRoomsInclMeasures, df_final], ignore_index=True)
        df_ColdRoomsInclMeasures = df_ColdRoomsInclMeasures.fillna(0)

    if 'csv' in run_arg:
        # print(df_ColdRoomsInclMeasures)
        exportPath = Path(__file__).parent / filename
        df_ColdRoomsInclMeasures.to_csv(exportPath, index=False)
        temp = "Saved Data as csv at " + str(exportPath)
        print(temp)

    else:
        print('didnt read csv')


