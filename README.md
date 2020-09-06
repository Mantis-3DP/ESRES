# ESRES
Expert System for Refrigeration Systems

## Steps to make it work
1. Adjust filelocation of train data in runme.py 
2. Fill the lists possible_problems, feature_names, user_input, possible_measures with your feature names and labels
3. create models by running rumme.py with argument "create_models for_problems" and again with argument "create_models for_measures"
4. Adjust filelocation of user/test data in runme.py 
5. run runme.py with the argument predict

## changing model settings
open create_models.py and change model settings in function create_model

repeat step 3