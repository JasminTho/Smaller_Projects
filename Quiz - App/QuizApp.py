'''
---------------------------------------------
QuizApp.py
Object-oriented GUI App of a quiz, with random questions, a timer, and result saving as JSON file
Author: JT
Last modified: 2026-02-22
---------------------------------------------
'''

# Modules
from tkinter import Tk, Label, Radiobutton, StringVar, Button
from tkinter import filedialog
from random import shuffle, choice
from threading import Thread
from time import sleep, asctime
from queue import Queue
from json import dump, load
from questionnaire import questionnaire


# Classes
class QuizApp ():
    dict_start_game = {'number' : 0,            # Current question
                       'score' : 0,             # Score: right answers per game round
                       'number_questions': 3,   # Number of questions per game round
                       'available_time':30,     # Time to answer each question
                       'needed_time':0}         # Time the user needed to answer the questions per game round
    def __init__(self):
        self.dict_round = self.dict_start_game.copy()
        self.selection_questions = list(range(len(questionnaire)))
        self.window = Tk()
        self.window.title('Quiz - App')
        
        # Widget
        self.question = Label(master = self.window,
                           text ='''The quiz consists of three questions. Click on the button 'Next Question' to start. For each question, you have 30 seconds to answer!''',
                           wraplength = 350,
                           justify = 'left',
                           relief = 'ridge',
                           width = 40,
                           height = 3,
                           font = ('Arial',12))
        self.answer = StringVar()
        self.answer.set(None)
        self.answer_a = Radiobutton(master = self.window,
                                     text = 'a)',
                                     font = ('Arial',12),
                                     justify = 'left',
                                     value = '',
                                     variable = self.answer)
        self.answer_b = Radiobutton(master = self.window,
                                     text = 'b)',
                                     font = ('Arial',12),
                                     value = '',
                                     variable = self.answer)
        self.answer_c = Radiobutton(master = self.window,
                                     text = 'c)',
                                     font = ('Arial',12),
                                     value = '',
                                     variable = self.answer)
        self.answer_d = Radiobutton(master = self.window,
                                     text = 'd)',
                                     font = ('Arial',12),
                                     value = '',
                                     variable = self.answer)
        self.timer = Label(master = self.window,
                           text = 'Remaining seconds:',
                           font = ('Arial',10))
        self.seconds = Label( master = self.window,
                               font = ('Arial',10))
        self.queue = Queue()
        self.timer_thread = None
        self.timer_active = False
        self.next_question = Button(master = self.window,
                                    text = 'Next question',
                                    font = ('Arial',12),
                                    command = self.askquestion)
        self.save_results = Button(master = self.window,
                                           text = 'save',
                                           font = ('Arial',12),
                                           command = self.save)
        self.load_results = Button(master = self.window,
                                       text = 'load',
                                       font = ('Arial',12),
                                       command = self.load)

        # Layout
        self.question.grid(column = 0, row =0, columnspan = 3, padx = 10)
        self.answer_a.grid(column = 0, columnspan = 3, row = 2, sticky = 'w', padx = 10)
        self.answer_b.grid(column = 0, columnspan = 3, row = 3, sticky = 'w', padx = 10)
        self.answer_c.grid(column = 0, columnspan = 3, row = 4, sticky = 'w', padx = 10)
        self.answer_d.grid(column = 0, columnspan = 3, row = 5, sticky = 'w', padx = 10)
        self.timer.grid(column = 0, row =1, pady = 10)
        self.seconds.grid(column = 1, row =1, sticky = 'w')
        self.next_question.grid(column = 0, row =6, pady = 15, sticky = 'e')
        self.save_results.grid(column = 1, row =6)
        self.load_results.grid(column = 2, row =6, sticky = 'w')
        
        self.update_gui()
        self.window.mainloop()

    def askquestion(self):             # Controlling Quiz - App
        self.dict_round['number'] += 1
        self.timer_active = False
        if self.dict_round['number'] < int(self.dict_round['number_questions'] + 1):
            if self.dict_round['number'] > 1:       # For the first question an evaluation is not available
                self.check_answer()
                self.select_question()
                self.window.after(1500, self.new_question)
            else:
                self.select_question()
                self.new_question()
        else:
            self.check_answer()
            self.window.after(1500, self.show_result)
            self.next_question.config(state='normal')

    def select_question(self):            # Search a question randomly from the questionaire and delete it out of them, to avoid douuble selection
            number = choice(self.selection_questions)
            self.dict_question = questionnaire[number]
            self.selection_questions.remove(number)
 
    def new_question(self):
        self.init_question()
        text_question = 'Question ' + str(self.dict_round['number']) + ': ' + str(self.dict_question['question'])
        self.question.config(text = text_question)
        self.read_answer()
        self.next_question.config(state='normal')

    def init_question(self):           # At the beginning of each question, the timer is started and all answers are reset to black
        self.timer_active = True
        self.timer_thread = Thread(target=self.set_timer, daemon=True)
        self.timer_thread.start()
        self.update_gui()
        self.answer_a.config(fg = 'black')
        self.answer_b.config(fg = 'black')
        self.answer_c.config(fg = 'black')
        self.answer_d.config(fg = 'black')

    def read_answer(self):           # Read the answer of the dictionairy and mixes these
        self.answers = []
        for word in self.dict_question['false']:
            self.answers.append(word)
        self.answers.append(self.dict_question['right'])
        shuffle(self.answers)
        self.answer_a.config(text = 'a) ' + self.answers[0],
                              value = self.answers[0])
        self.answer_b.config(text = 'b) ' + self.answers[1],
                              value = self.answers[1])
        self.answer_c.config(text = 'c) ' + self.answers[2],
                              value = self.answers[2])
        self.answer_d.config(text = 'd) ' + self.answers[3],
                              value = self.answers[3])
        
    def check_answer(self):              
        self.next_question.config(state='disabled')        
        # Button is set to disable. The reason is that in test runs the button was push to early (next question was available and the answer were false)
        user_answer = self.answer.get()
        # Mark the right answer and if necessary the false answer
        if user_answer == self.dict_question['right']:
            self.dict_round['score'] += 1
            self.question.config(text = 'Right')
            if user_answer == self.answers[0]:
                self.answer_a.config(fg = 'green')
            elif user_answer == self.answers[1]:
                self.answer_b.config(fg = 'green')
            elif user_answer == self.answers[2]:
                self.answer_c.config(fg = 'green')
            elif user_answer == self.answers[3]:
                self.answer_d.config(fg = 'green')
        else:
            self.question.config(text = 'Unfortunately incorrect')
            if user_answer == self.answers[0]:
                self.answer_a.config(fg = 'red')
            elif user_answer == self.answers[1]:
                self.answer_b.config(fg = 'red')
            elif user_answer == self.answers[2]:
                self.answer_c.config(fg = 'red')
            elif user_answer == self.answers[3]:
                self.answer_d.config(fg = 'red')
            right_answer = self.dict_question['right']
            if right_answer  == self.answers[0]:
                self.answer_a.config(fg = 'green')
            elif right_answer == self.answers[1]:
                self.answer_b.config(fg = 'green')
            elif right_answer == self.answers[2]:
                self.answer_c.config(fg = 'green')
            elif right_answer == self.answers[3]:
                self.answer_d.config(fg = 'green')

        # Calculation of needed time
        state_timer = self.seconds.cget('text')
        available_time = self.dict_round['available_time']
        previous_needed_time = self.dict_round['needed_time']
        need_time = int(available_time) - int(state_timer) + int(previous_needed_time)
        self.dict_round['needed_time'] = need_time

    def show_result(self):
        self.answer_a.config(text = 'a)',
                              fg = 'black')
        self.answer_b.config(text = 'b)',
                              fg = 'black')
        self.answer_c.config(text = 'c)',
                              fg = 'black')
        self.answer_d.config(text = 'd)',
                              fg = 'black')
        # Individual result output for user based on number of right ansered questions
        if self.dict_round['score'] == 3:
            self.question.config(text = 'Result: Super! You answered all questions correctly.')
        elif self.dict_round['score'] == 2:
            self.question.config(text = 'Result: You answered 2 questions correctly. Great!')
        elif self.dict_round['score'] == 1:
            self.question.config(text = 'Result: You answered 1 questions correctly. Keep your chin up!')
        else:
            self.question.config(text = 'Result: Unfortunately, you could not answer any questions correctly! But do not give up!')

        # Result text to save the result
        date = asctime()
        self.result_text = ('Right_answered: ' + str(self.dict_round['score']) + ' from '+
                              str(self.dict_round['number_questions']) + '; needed_time: ' +
                              str(self.dict_round['needed_time']) + ' seconds; ' + str(date))
        self.dict_round = self.dict_start_game.copy()
        
        

    def set_timer(self):                # Timer runs in a thread and with queue save
        for i in range (int(self.dict_round['available_time']),-1,-1):
            if not self.timer_active:
                break 
            self.queue.put(i)
            sleep(1)

    def update_gui(self):               # Change timer in the GUI. Numbers are change to red wenn time <5 seconds
        value = None
        if not self.queue.empty():
            value = self.queue.get()
            self.seconds.config(text=str(value))
            if 0 < value < 6 :
                self.seconds.config(fg = 'red')
            else:
                self.seconds.config(fg = 'black')
            if value == 0:                           # If the timer runs out  (is equal zero), than the next question should be loaded.
                self.timer_active = False
                self.check_answer()
                self.window.after(1500, self.askquestion)
        self.window.after(100, self.update_gui)

    def save(self):
        text = self.question.cget('text')
        if not text.startswith('Result:'):        # Quiz must be done, before the results can be saved
            self.question.config(text = 'You must finish the game before you can save the result. Click on "Next question"')
        else:
            path = filedialog.asksaveasfilename()
            if path:
                if not path.endswith('.json'):
                    path += '.json'
                with open(path,'w', encoding = 'utf-8') as file:    
                    dump(self.result_text, file)

    def load(self):
        path = filedialog.askopenfilename()
        if path:
            if not path.endswith('.json'):
                path += '.json'
            with open(path,'r', encoding = 'utf-8') as file:    
                readed_text = load(file)
                
                self.question.config(text = readed_text)
                    
# Start the Quiz App, all other functions are implemented in the class
QuizApp()
