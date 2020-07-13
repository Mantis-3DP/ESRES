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
fileloca_user = Path(__file__).parent / "Data/ProblemTestDataUser.csv"
folder_problem_models = "models_problem"
folder_measure_models ="modeles_measure"
dataset_train = pd.read_csv(fileloca_train)
dataset_user =  pd.read_csv(fileloca_user)
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
possible_measures:dict = dict()
possible_measures["Fan consumes too much energy"] = ["clean_fan", "new_fan"]
possible_measures["People too long in the Room"] = ["install_countdown", "school_workers"]

imp_vars = function_folder, possible_problems, feature_names, user_input, possible_measures

for measure in possible_measures.values():
    for item in measure:
        print("Max value element : {} Min value element : {}".format(max(dataset_train[item]),  min(dataset_train[item])))


if 'create_models' in run_arg:
    train_1 = prepped_data(dataset_train, *imp_vars)
    train_1.get_data("train")
    save_folder = "problems"
    if 'for_problems' in run_arg:
        for model_num, problem in enumerate(possible_problems):
            create_all_models(train_1.X_machine, train_1.X_machine_split, train_1.Y_problems[problem],
                              train_1.Y_problems_split[problem], len(train_1.feature_names), train_1.n_classes_probs[problem], model_num, folder_problem_models, 0)

    if 'for_measures' in run_arg:
        for problem in possible_measures:
            train_2 = prepped_data(dataset_train, *imp_vars)
            train_2.drop_rows(problem)
            train_2.get_data("train")
            train_2.append_user()
            index_prob = possible_problems.index(problem)
            for measure_num, measure in enumerate(possible_measures[problem]):
                print(measure_num, measure)
                create_all_models(train_2.X_machine, train_2.X_machine_split, train_2.Y_measures[measure],
                              train_2.Y_measures_split[measure], len(train_2.feature_names), 1, index_prob,
                              folder_measure_models, measure_num=measure_num)


if "predict" in run_arg:
    user_1 = prepped_data(dataset_user, *imp_vars)
    user_1.dropped = 1
    user_1.get_data("test_known")

    predictions: dict = dict()
    for model_num, problem in enumerate(possible_problems):
        predictions[problem] = []
        model_loca = Path(__file__).parent / 'models/{}/cold_system_model_{}.h5'.format(folder_problem_models, model_num)
        predictions[problem] = predict_problem(model_loca, user_1.X_machine, 0)

    user_1.append_user()

    for measure in possible_measures.values():
        for item in measure:
            predictions[item] = np.zeros(len(user_1.X_machine))
    ein_array = []
    for user, row in enumerate(user_1.X_machine):
        print("results for user {}".format(user))
        for problem in possible_measures: # probelm = "Fan consumes too much
            model_index = possible_problems.index(problem) # 0 4
            if predictions[problem][user] > 0.5:
                print(predictions[problem][user])
                for measure_index, measure_name in enumerate(possible_measures[problem]):
                    model_loca = Path(__file__).parent / 'models/{}/cold_system_model_{}_{}.h5'.format(folder_measure_models, model_index, measure_index)
                    ein_array = predict_problem(model_loca, [list(user_1.X_machine[user])], 1)

                    predictions[measure_name][user] = ein_array
    predictions = user_1.invers_scal(predictions)


elif 'generate_data' in run_arg:
    # Liste mit ColdRoom Instanzen -> amount bestimmt Anzahl der generierten Daten, "mode2 ="setup" sorgt dafür, dass nur fehlerhafte daten mit maßnahmen und ohne Probleme generiert werden!" 
    coldRooms = generateRandomColdRooms(amount=20, csv=False, filename="testNEW", fault_share=1, object=True)
    # Dateiname für generierte Daten
    filename = "Data/" + "ProblemTestDataUser" + ".csv"
    # DataFrame für ColdRooms mit problem
    df_ColdRoomsInclMeasures = pd.DataFrame()

    # Schleife über alle ColdRooms in Coldroom
    for cr in coldRooms:
        # DATA PREPROCESSING
        # sorgt dafür, dass alle problem spalten existieren und jede zelle in jeder zeile mit 0 oder 1 gefüllt ist
        df_temp_features = pd.DataFrame([cr.dataRow[:-1]], columns=feature_names)  # contains features of one coldroom
        df_temp_userInput = pd.DataFrame([random.randint(9, 11) / 10],
                                         columns=user_input)  # contains userInput -> in diesem fall nur eine spalte mit zufalls values
        # FUNFACT: Vielleicht sollten wir die Zufallswerte ändern...das sieht irgendwie komisch aus mit den Zahlen in der Reihenfolge...#insidejob xD
        temp_array_problems = []
        for problem in possible_problems:
            if problem in cr.dataRow[-1]:
                temp_array_problems.append(1)
            else:
                temp_array_problems.append(0)
        df_problems = pd.DataFrame([temp_array_problems],
                                   columns=possible_problems)  # contains problems of one coldroom
        df_preMid = df_temp_features.join(
            df_temp_userInput)  # Das kann man sicherlich auch schöner lösen, wenn dus hinter problems haben willst, dann join es einfach einen join später
        # Falls wir das doch an einer bestimmten Stelle brauchen, kann man noch die insert Funktion bemühen, aber ich glaube so passt es
        df_mid = df_preMid.join(df_problems)
        cr.calculateDefaultValues()

        # JoinDataFrames
        df_final = df_mid.join(cr.add_measure_columns())
        if "new_fan" in df_final.columns:  # KeyError prevention weil die spalten noch nicht existieren -> kann man auch noch besser machen TODO
            df_final.at[0, "new_fan"] = (df_final.at[0, "new_fan"] * df_final.at[0, "new_measure_preferred"])
        elif "install_countdown" in df_final.columns:
            df_final.at[0, "install_countdown"] = (
                        df_final.at[0, "install_countdown"] * df_final.at[0, "new_measure_preferred"])

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


