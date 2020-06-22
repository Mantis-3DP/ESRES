from create_model import datapreprocess, create_all_models
from pathlib import Path
import sys


create_models: int = sys.argv[1]
if create_models == 1:
    #create models
    #link to data
    fileloca_train = Path(__file__).parent / "data_sets/samleData_vectoroutput.csv"
    num_measures = 5

    feature_names, measure_names, X_train, X_val, Y_train, Y_val, n_features, n_classes = datapreprocess(fileloca_train,
                                                                                                         num_measures)

    model_number = 0
    for measure in measure_names:
        create_all_models(X_train, X_val, Y_train[measure], Y_val[measure], n_features, n_classes[measure], model_number)
        model_number += 1
else:
    print("use models")