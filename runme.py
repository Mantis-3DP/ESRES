import random
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import tensorflow as tf
from ColdRoom import generateRandomColdRooms
from create_model import create_all_models
from data_processing import prepped_data
from format_strings import show_user_predictions
from predict_problems import predict_problem

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

# following section defines related folders scale function from the data preprocessing are saved in the function
# folder fileloca_train is the path to the Train data csv fileloca_user is the path to the input data of a user.
# similar to the train data, but without the problem and measure section
function_folder = Path(__file__).parent / "saved_functions"
fileloca_train = Path(__file__).parent / "Data/TrainData.csv"
fileloca_user = Path(__file__).parent / "Data/ProblemTestDataUser.csv"
folder_problem_models = "models_problem"
folder_measure_models = "modeles_measure"
# possible_problems is a list of the problems that could be detected of the data csv. These are the labels
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
# feature names is a list of the features
feature_names = [
    "load_transmission",
    "load_people",
    "n_person",
    "load_light",
    "load_fan",
    "load_total",
    "load_installed",
]
# user_input is a list of the features which a user could input
user_input = [
    "new_measure_preferred"
]
# possible_measures is a dict that connects possible_problems with measures that are related to that problem
possible_measures: dict = dict()
possible_measures["Fan consumes too much energy"] = ["clean_fan", "new_fan"]
possible_measures["People too long in the Room"] = ["install_countdown", "school_workers"]

# read data csv and save the data as an array
dataset_train = pd.read_csv(fileloca_train)
dataset_user = pd.read_csv(fileloca_user)
imp_vars = function_folder, possible_problems, feature_names, user_input, possible_measures

# to retrain the models runme.py needs "create_models" as argument
if "create_models" in run_arg:
    # differentiate between training of problem detection models or measure detection related to detected problems
    if "for_problems" in run_arg:
        train_1 = prepped_data(dataset_train, *imp_vars)
        train_1.get_data("train")
        for model_num, problem in enumerate(possible_problems):
            create_all_models(train_1.X_machine, train_1.X_machine_split, train_1.Y_problems[problem],
                              train_1.Y_problems_split[problem], len(train_1.feature_names),
                              train_1.n_classes_probs[problem], model_num, folder_problem_models)

    if "for_measures" in run_arg:
        for problem in possible_measures:
            train_2 = prepped_data(dataset_train, *imp_vars)
            train_2.drop_rows(problem)
            train_2.get_data("train")
            train_2.append_user()
            index_prob = possible_problems.index(problem)
            for measure_num, measure in enumerate(possible_measures[problem]):
                create_all_models(train_2.X_machine, train_2.X_machine_split, train_2.Y_measures[measure],
                                  train_2.Y_measures_split[measure], len(train_2.feature_names), 1, index_prob,
                                  folder_measure_models, measure_num=measure_num)

# use case: runme.py needs arg "predict"
if "predict" in run_arg:
    all_users_predictions: dict = dict()
    all_users = prepped_data(dataset_user, *imp_vars)
    all_users.dropped = 1
    all_users.get_data()
    for model_num, problem in enumerate(possible_problems):
        all_users_predictions[problem] = []
        model_loca = Path(__file__).parent / 'models/{}/cold_system_model_{}.h5'.format(folder_problem_models,
                                                                                        model_num)
        all_users_predictions[problem] = predict_problem(model_loca, all_users.X_machine, 0)
    all_users.append_user()
    for measure in possible_measures.values():
        for item in measure:
            all_users_predictions[item] = np.zeros(len(all_users.X_machine))
    predict_array = []
    for user, row in enumerate(all_users.X_machine):
        for problem in possible_measures:
            model_index = possible_problems.index(problem)
            if all_users_predictions[problem][user] > 0.5:
                for measure_index, measure_name in enumerate(possible_measures[problem]):
                    model_loca = Path(__file__).parent / 'models/{}/cold_system_model_{}_{}.h5'.format(
                        folder_measure_models, model_index, measure_index)
                    predict_array = predict_problem(model_loca, [list(all_users.X_machine[user])], 1)
                    all_users_predictions[measure_name][user] = predict_array
    # the data was scaled to make it processable by the ANN, to get the real values the scale needs to be reverted
    predictions = all_users.invers_scal(all_users_predictions)
    show_user_predictions(all_users_predictions, possible_problems, possible_measures, len(all_users.X_machine))


elif 'generate_data' in run_arg:
    # Liste mit ColdRoom Instanzen -> amount bestimmt Anzahl der generierten Daten, "mode2 ="setup" sorgt dafür,
    # dass nur fehlerhafte daten mit maßnahmen und ohne Probleme generiert werden!"
    coldRooms = generateRandomColdRooms(amount=3, csv=False, filename="testNEW", fault_share=1, object=True)
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
                                         columns=user_input)
        temp_array_problems = []
        for problem in possible_problems:
            if problem in cr.dataRow[-1]:
                temp_array_problems.append(1)
            else:
                temp_array_problems.append(0)
        df_problems = pd.DataFrame([temp_array_problems],
                                   columns=possible_problems)  # contains problems of one coldroom
        df_preMid = df_temp_features.join(
            df_temp_userInput)
        df_mid = df_preMid.join(df_problems)
        cr.calculateDefaultValues()

        # JoinDataFrames
        df_final = df_mid.join(cr.add_measure_columns())
        if "new_fan" in df_final.columns:
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
