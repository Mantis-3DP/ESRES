import numpy as np


def show_top_predictions(predictions, measure_names, Y_test, test_count):

    counter = 0
    num_top_values = 3
    for i in range(0, test_count):
        measure_values = []
        for measure in measure_names:
            measure_values.append(predictions[measure][i])
        measure_array = np.array(measure_values)
        top_value_positions = measure_array.argsort()[-num_top_values:][::-1]
        print('testdata_{} top {} measures:'.format(i, num_top_values))
        for m in range(0, len(top_value_positions)):
            measure_name_at_m = measure_names[top_value_positions[m]]
            value_at_m = int(100 * measure_values[top_value_positions[m]])
            Y_value_at_m = Y_test[measure_names[top_value_positions[m]]][i, 1]

            if np.round(measure_values[top_value_positions[m]], 0) == Y_test[measure_names[top_value_positions[m]]][
                i, 1]:
                counter += 1
            if value_at_m > 50:
                print('--- {}% --- for {} --- true: {}'.format(
                    value_at_m,
                    measure_name_at_m,
                    Y_value_at_m
                ))
        print(' ')
    print('wrong predictions {}%'.format(int(100 * (1 - (counter / (num_top_values * test_count))))))

def show_predictions(predictions, measure_names, Y_test, test_count):

    counter = 0
    for i in range(0, test_count):   #100
        measure_values = []
        for measure in measure_names:
            measure_values.append(predictions[measure][i])
        measure_array = np.array(measure_values)
        for m in range(0, len(measure_array)):
            measure_name_at_m = measure_names[m]
            value_at_m = int(100 * measure_values[m])
            Y_value_at_m = Y_test[measure_names[m]][i]

            if np.round(measure_values[m], 0) == Y_test[measure_names[m]][i]:
                counter += 1
            print('{} --- {}% --- for {} --- true: {}'.format(
                m,
                value_at_m,
                measure_name_at_m,
                Y_value_at_m
            ))
        print(' ')
    print('wrong predictions {}%'.format(int(100 * (1 - (counter / (len(measure_array) * test_count))))))

def show_user_predictions(predictions, possible_problems, possible_measures, amount_user_data):
    print("############### EVALUATION COMPLETED ###############")
    print("###############  SEE RESULTS BELOW   ###############")
    for i in range(0, amount_user_data):   
        print("------ Results for user {} ------".format(i+1)) #i+1 to prevent "user0"
        temp_dict:dict = dict()
        for problem in possible_problems:
            temp_dict[problem] = predictions[problem][i]
        # Sort problems by value -> descending
        temp_dict = {k: v for k, v in sorted(temp_dict.items(), key=lambda item: item[1], reverse=True)}
        if temp_dict["none"] >= 0.75:
            print("Congratulations, there were no problems found by our system in your Coldroom.")
        else:
            print("\n The following problems were found in your Coldroom: \n")
            for count, problem in enumerate(temp_dict):
                print("{}. {} with an impact of {}%".format(count+1, problem, round(temp_dict[problem]*100 , 2)))
            temp_dict.clear()
            print("\n Based on those problems and your preferences, our system recommends the following measures: \n")

            for measure in possible_measures.values():
                for item in measure: #notwendig weil nested dictionary...
                    if item in predictions:
                        temp_dict[item] = predictions[item][i] 
            # Sort measures by value -> descending                    
            temp_dict = {k: v for k, v in sorted(temp_dict.items(), key=lambda item: item[1], reverse=True)}
            for count, measure in enumerate(temp_dict):
                # for problem, measure in 
                print("To solve the problem \"{}\": \n>> {}\nFor this measure we calculated an amortisation time of {} years\n".format(
                    getProblemByMeasure(possible_measures,measure), getMeasureDescription(measure), round(temp_dict[measure],2)))



def getMeasureDescription(input_measure):
    measureDescriptions = {
        "clean_fan" : "Clean the fan of the refridgerant unit.",
        "new_fan" : "Install a new fan in the Coldroom.",
        "install_countdown" : "Install a timer that counts and displays the time of your workers in the Coldroom.",
        "school_workers" : "Organize a workshop for your workers for time efficient working in the ColdRoom."
    }
    return measureDescriptions[input_measure]

def getProblemByMeasure(possible_measures, input_measure):
    linked_problem_measures:dict = dict()
    for problem in possible_measures:
        for measure in possible_measures[problem]:
            linked_problem_measures[measure] = problem
    return linked_problem_measures[input_measure]