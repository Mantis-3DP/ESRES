import numpy as np


def show_predictions(predictions, measure_names, test_count):

    for i in range(0, 10): #test_count instead of 10
        measure_values = []
        for measure in measure_names:
            measure_values.append(predictions[measure][i])
        measure_array = np.array(measure_values)
        top_value_positions = measure_array.argsort()[-3:][::-1]
        print('testdata_{} top 3 measurs:'.format(i))
        for m in range(0, len(top_value_positions)):
            print('--- {} --- has probability of {}%'.format(measure_names[top_value_positions[m]], int(100*measure_values[top_value_positions[m]])))
    print('')