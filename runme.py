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
import random

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

user_input = [
    "new_measure_preferred"
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



elif 'generateData' in run_arg:
    # Liste mit ColdRoom Instanzen -> amount bestimmt Anzahl der generierten Daten, "mode2 ="setup" sorgt dafür, dass nur fehlerhafte daten mit maßnahmen und ohne Probleme generiert werden!" 
    coldRooms = generateRandomColdRooms(amount=100, csv=False, filename="testNEW", fault_share=1, object=True)
    # Dateiname für generierte Daten
    filename = "Data/" + "ProblemTestData" + ".csv"
    # DataFrame für ColdRooms mit problem
    df_ColdRoomsInclMeasures = pd.DataFrame()



    # Schleife über alle ColdRooms in Coldroom
    for cr in coldRooms: 
        # DATA PREPROCESSING 
        # sorgt dafür, dass alle problem spalten existieren und jede zelle in jeder zeile mit 0 oder 1 gefüllt ist 
        df_temp_features = pd.DataFrame([cr.dataRow[:-1]], columns=feature_names) #contains features of one coldroom
        df_temp_userInput = pd.DataFrame([random.randint(9,11)/10], columns=user_input) #contains userInput -> in diesem fall nur eine spalte mit zufalls values
        #FUNFACT: Vielleicht sollten wir die Zufallswerte ändern...das sieht irgendwie komisch aus mit den Zahlen in der Reihenfolge...#insidejob xD
        temp_array_problems = []
        for problem in possible_problems:
            if problem in cr.dataRow[-1]: 
                temp_array_problems.append(1)
            else: 
                temp_array_problems.append(0)
        df_problems = pd.DataFrame([temp_array_problems], columns=possible_problems) #contains problems of one coldroom 
        df_preMid = df_temp_features.join(df_temp_userInput) # Das kann man sicherlich auch schöner lösen, wenn dus hinter problems haben willst, dann join es einfach einen join später
        # Falls wir das doch an einer bestimmten Stelle brauchen, kann man noch die insert Funktion bemühen, aber ich glaube so passt es 
        df_mid = df_preMid.join(df_problems)
        cr.calculateDefaultValues() 

        #JoinDataFrames
        df_final = df_mid.join(cr.add_measure_columns())
        if "new_fan" in df_final.columns:   #KeyError prevention weil die spalten noch nicht existieren -> kann man auch noch besser machen TODO
            df_final.at[0, "new_fan"] = (df_final.at[0, "new_fan"]*df_final.at[0, "new_measure_preferred"])
        elif "install_countdown" in df_final.columns:
            df_final.at[0, "install_countdown"] = (df_final.at[0, "install_countdown"]*df_final.at[0, "new_measure_preferred"])

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


