from pathlib import Path
from keras.models import Sequential
from keras.layers import Dense
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam


'''


In order to teach your model to detect more than one class per image, you will need to perform a few changes to your model and data, and re-train it.

    Your final activation will now need to be a sigmoid, since you will not predict a single class probability distribution anymore. Now you want each output neuron to predict a value between 0 and 1, with more than one neuron possibly having values close to 1.
    Your loss function should now be binary_crossentropy, since you will treat each output neuron as an independent prediction, which you will compare to the true label.
    As I see you have been using sparse_categorical_crossentropy, I assume your labels were integers. You will want to change your label encoding to one-hot style now, each label having a len equal to num_classes, and having 1's only at those positions where the image has that class, the rest being 0's.

With these changes, you can now re-train your model to learn to predict more than one class per image.

As for predicting bounding boxes around the objects, that is a very different and much more challenging task. Advanced models such as YOLO or CRNN can do this, but their structure is much more complex.



'''


def create_custom_model(input_dim, output_dim, nodes, n=2, name='model'):
    def create_model():
        # Create model
        model = Sequential(name=name)
        for i in range(n):
            model.add(Dense(nodes, input_dim=input_dim, activation='relu'))
        model.add(Dense(output_dim, activation='softmax'))

        # Compile model
        model.compile(Adam(lr=0.01), loss='categorical_crossentropy',
                      metrics=['accuracy'])
        return model

    return create_model

def create_all_models(X_train, X_val, Y_train, Y_val, n_features, n_classes, model_number):
    models = [create_custom_model(n_features, n_classes, 6, n=i, name='model_{}'.format(model_number))
              for i in range(2, 3)]

    for create_model in models:
        create_model().summary()

    for create_model in models:
        model = create_model()
        print('Model name:', model.name)
        # history_callback =\
        model.fit(X_train, Y_train,
                  batch_size=1,
                  epochs=5,
                  # verbose=0,
                  validation_data=(X_val, Y_val)
                  )
        model.save(Path(__file__).parent / 'models/cold_system_{}.h5'.format(model.name))
        ### we need a wait and confirmation of a succsesful write
        print(Path(__file__).parent / 'models/cold_system_{}.h5 saved'.format(model.name))
    return




'''

        # correlations
    
        corr_data = dataset_train
        corr_data['Measure'] = encoded_Y
        corr = corr_data.corr()
        heatmap_variables = sns.heatmap(corr, xticklabels=list(dataset_train.columns[:]), yticklabels=list(dataset_train.columns[:]))
        plt.show()    
        
        
model = Sequential()
model.add(Dense(20, input_dim=(17), activation='relu')) #hidden layer hat 12 Möglichkeiten, input sind 8 Datasets
model.add(Dense(15, activation='relu')) #das ist das zweite hidden layer mit 8 Knoten
model.add(Dense(3, activation='softmax')) #output ist dann ein Knoten
model.summary()
model.compile(Adam(lr=0.0001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(x=X_train, y=Y_train, validation_data=(X_test, Y_test), batch_size=1, epochs=100, shuffle=True)

score = model.evaluate(X_test, Y_test, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])
'''
'''
test_samples = dataset_vali[:, :17]
test_labels = dataset_vali[:, 17]
scaled_train_samples = scaler.fit_transform(test_samples)

predictions = model.predict(x=test_samples, batch_size=1)

print(predictions)
'''
