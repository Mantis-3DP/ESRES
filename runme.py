from create_model import create_all_models
from data_processing import prepped_data
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
fileloca_train = Path(__file__).parent / "Data/ProblemTestDataPref.csv"
dataset_train = pd.read_csv(fileloca_train)
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
user_input = [
    "pref"
]
measures:dict = dict()
measures["Fan consumes too much energy"] = ["clean_fan", "new_fan"]
measures["People too long in the Room"] = ["install_countdown", "school_workers"]

num_problems = len(possible_problems)
num_features = len(feature_names)
num_measure = len(measures["Fan consumes too much energy"])+len(measures["People too long in the Room"])
num_user_input = len(user_input)

data_categos = ["possible_problems", "feature_names", "user_input", "measures"]



train_data_1 = prepped_data(dataset_train, function_folder, possible_problems, feature_names, user_input, measures, num_problems, num_features, num_measure, num_user_input)



if 'create_models' in run_arg:
    datapreprocess_train(dataset_train, function_folder, possible_problems, feature_names, user_input, measures, num_problems, num_features, num_measure, num_user_input)
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


