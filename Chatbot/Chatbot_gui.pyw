'''
---------------------------------------------
Chatbot_gui.py
Model of a GUI for a easy chatbot
Author: JT
Last modified: 2026-02-22
---------------------------------------------
'''

# Modules
from tkinter import Tk, Text, Entry, Button
from PIL import Image, ImageTk
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_extraction.text import CountVectorizer
from random import choice

# Load chatbot dataset
dataset = pd.read_csv('ChatbotTraining.csv')

# Set feature and target value
target = dataset['tag']
features = dataset['patterns']


# Bag of words model
corpus = features
vectorizer = CountVectorizer()          
X = vectorizer.fit_transform(corpus)    
X_dense = X.toarray()                  

# Training of the model
clf = DecisionTreeClassifier()
clf = clf.fit(X_dense, target)

print('Chatbot loaded')

# Eventhandler
def chatbot():
    input_user = str(input_entry.get()) + '\n'
    output.insert('end', input_user)
    input_entry.delete(0, 'end')
    sentence_user = [input_user]

    X_1 = vectorizer.transform(sentence_user)
    X_1_dense = X_1.toarray()
    pred_category = clf.predict(X_1_dense)      # Predicted category

    print('Category:',pred_category)


    d_sentence = {}
    set_target = set(target)
    list_target = list(set_target)          # List of possible categories

    for n in range(dataset.shape[0]):
        category = dataset.iloc[n,0]            # set category on n-values of the first column
        l_text = dataset.iloc[n,2]
        if category not in d_sentence:
            d_sentence[category] = [l_text]
        else:
            d_sentence[category].append(l_text)

    for i in list_target:
        if i == pred_category.item():
            answer_chatbot = str(choice(d_sentence[pred_category.item()])) + '\n'
            output.tag_config('chatbot', foreground = 'blue', justify = 'right')
            output.insert('end', answer_chatbot,'chatbot')


# Main

# GUI
window = Tk()
window.title('My first chatbot')

img = Image.open('sending.png')
img = img.resize((25, 15))  
picture_arrow = ImageTk.PhotoImage(img)
# Widget
output = Text(window,
               width = 50,
               height = 10)
input_entry = Entry(window,
               width = 45)
input_entry.bind('<Return>', lambda event: chatbot())
button = Button(window,
                image = picture_arrow,
                height = 1,
                command = chatbot)

# Layout
output.grid(column = 0, columnspan = 2, row = 0, padx = 5, pady = 5)
input_entry.grid(column = 0, row = 1, pady = 5)
button.grid(column = 1, columnspan = 2, row = 1, sticky='ns', pady = 5)

window.mainloop()
