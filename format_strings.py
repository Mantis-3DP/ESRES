import numpy as np


def show_predictions(predictions, measure_names, Y_test, test_count):
    counter = 0
    test_count = 10  # remove later
    num_top_values = 3
    for i in range(0, test_count):
        measure_values = []
        for measure in measure_names:
            measure_values.append(predictions[measure][i])
        measure_array = np.array(measure_values)
        top_value_positions = measure_array.argsort()[-num_top_values:][::-1]
        print('testdata_{} top {} measurs:'.format(i, num_top_values))
        for m in range(0, len(top_value_positions)):
            measure_name_at_m = measure_names[top_value_positions[m]]
            value_at_m = int(100 * measure_values[top_value_positions[m]])
            Y_value_at_m = Y_test[measure_names[top_value_positions[m]]][i, 1]

            if np.round(measure_values[top_value_positions[m]], 0) == Y_test[measure_names[top_value_positions[m]]][
                i, 1]:
                counter += 1
            print('--- {} --- has probability of {}% --- true value is {}'.format(
                measure_name_at_m,
                value_at_m,
                Y_value_at_m
            ))
        print(' ')
    print('wrong predictions {}%'.format(int(100 * (1 - (counter / (num_top_values * test_count))))))
