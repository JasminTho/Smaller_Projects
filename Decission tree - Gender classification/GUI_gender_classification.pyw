'''
---------------------------------------------
gender_classification.pyw
Predict if a dataset is male or female
Author: JT
Last modified: 2026-02-22
---------------------------------------------
'''

# Modules
import pandas as pd
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from tkinter import Tk,  Button, Label, Entry

# globale variables
dataset = None

# Eventhandling
def load():
    global dataset
    dataset = pd.read_csv('gender_classification.csv')
    loadtext.config(text = 'Data were loaded')
    
def machine_learning():
    if dataset is None:
        output.config(text = 'No datasets were loaded!')
    else:
        # Set feature and target variable
        target = dataset['gender']
        features = dataset.drop(columns = ['gender'])      
        # Train and test the model
        try:
            size_training = int(accuracy.get())
        except:
            if '.' in accuracy.get():
                try:
                    size_training = float(accuracy.get())
                except:
                    size_training = 75.0
            else:
                size_training = 75

        if not (1 <= size_training <= 99):
            output.config(text = 'Trainigs data share must be between 1 and 99%.')
        else:
            size_test = (100-size_training)/100
            size_test_percent = 100 - size_training
            X_train, X_test, y_train, y_test = train_test_split(features, target, test_size = size_test, random_state = 1) 

            clf = DecisionTreeClassifier()
            clf = clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)

            result = round(metrics.accuracy_score(y_test,y_pred)*100,2)

            output.config(text = 'Accuracy of the model: ' + str(result) + ' % (Share trainings data: ' + str(size_training) + ' %; Share test data: ' + str(size_test_percent) + ' %)')

# GUI definieren
window = Tk()
window.title('Gender classification')

# Widget
load_button = Button(text = 'Data set loaded',
               command = load)
loadtext = Label()
text = Label(text = 'Share of trainings data in percent:')
accuracy = Entry()
calculation= Button(text = 'Classified gender',
                   command = machine_learning)
output = Label()

# Layout GUI
load_button.grid(padx = 20, pady = 5)
loadtext.grid(row = 0, column = 1, pady = 5)

accuracy.grid(column = 1,row = 1, pady = 5, padx = 5)
text.grid(column = 0, row = 1, pady = 5)

calculation.grid(columnspan = 2,row = 2, pady = 10)
output.grid(columnspan = 2, row = 3)

window.mainloop()
