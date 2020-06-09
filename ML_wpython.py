from pandas import read_csv
from pandas.plotting import scatter_matrix
from matplotlib import pyplot
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.wrappers.scikit_learn import KerasClassifier
from keras.utils import np_utils
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
# Load dataset
url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/iris.csv"
names = ['sepal-length', 'sepal-width', 'petal-length', 'petal-width', 'class']
dataset = read_csv(url, names=names)    #DataFrame

print(dataset.shape)

print(dataset.head(20))

print(dataset.describe())

print(dataset.groupby('class').size())

dataset.plot(kind='box', subplots=True, layout=(2,2), sharex=False, sharey=False)
pyplot.show()

dataset.hist()
pyplot.show()
scatter_matrix(dataset)
pyplot.show()


array = dataset.values
X = array[:,0:4].astype(float)
Y = array[:,4]
#warum wird das so geteilt? ich teile die Werte von den Sorten
#im nächsten Schritt, teile ich die Daten dann in 80% train und 20% validation
#so müsste ich das dann auch machen. Die ersten 8 Maschinen werden zum Trainieren verwendet und dann die letzten Zwei zur validation

#Ich verstehe das jetzt so: Ich nehme die Längen und versuche damit das abgetrennte vorherzusagen.
#Wir haben aber eine vielzahl an Daten die wir vorhersagen möchten. Somit müssen wir erkennen was die relevanten Input Daten sind
#Ich nehme im ersten die Daten und versuche die Lichtleistung vorherzusagen. Dann nehme ich das Modell, dass ich testen will
# und vergleiche den Wert mit dem vorhergesagten Wert. Bei einer Differenz von X schreibe ich, dass das getestete System abweicht.


#supervised learning heißt, dass die Daten bereits Labels haben