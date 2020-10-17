import json
import os
import pickle
import random

import nltk
import numpy as np
import pandas as pd

import tensorflow as tf
import keras
# import tensorflow.keras as keras
import keras.backend as K
from keras.models import Sequential
from keras.layers import Activation, Dense, Dropout
from keras.optimizers import SGD


from nltk.stem.lancaster import LancasterStemmer
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')
nltk.download('punkt')
analyzer = SentimentIntensityAnalyzer()
stemmer = LancasterStemmer()
words = []
classes = []
documents = []
ignore_words = ['?']

bFile = "src/b-data.pkl"
bmod = "src/b-model.pkl"

def check_files():
    """
    Creates empty encrypted files 
    """
    files = { 
    }

    for filename, value in files.items():
        if not os.path.isfile("{}".format(filename)):
            print("Creating empty {}".format(filename))
            with open("{}".format(filename), 'wb') as outfile:
                json.dump(value, outfile)
                outfile.close()

class rinProcess():
    def __init__(self):
        check_files()
        self.model = pickle.load(open(bmod, 'rb'))
        self.data = pickle.load(open(bFile, "rb"))
        self.words = self.data['words']
        self.classes = self.data['classes']
    """
    in this class it will:
        Use pickle to load in the pre-trained model then generate probabilities from the model.
        After it will filter out predictions below a threshold, and provide intent index then sort by strength of probability.
        and values will return tuple of intent and probability
        Human-In-The-Loop(HITL)
    """

    def clean_up_sentence(self, sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
        return sentence_words


    def bow(self, sentence, words, show_details=True):
        sentence_words = self.clean_up_sentence(sentence)
        bag = [0]*len(self.words)
        for s in sentence_words:
            for i, w in enumerate(self.words):
                if w == s:
                    bag[i] = 1
                    if show_details:
                        print("found in bag: %s" % w)
        return(np.array(bag))


    def think(self, sentence):
        ERROR_THRESHOLD = 0.85

        input_data = pd.DataFrame([self.bow(sentence, self.words, show_details=False)], dtype=float, index=['input'])
        results = self.model.predict([input_data])[0]
        results = [[i, r] for i, r in enumerate(results) if r > ERROR_THRESHOLD]
        results.sort(key=lambda x: x[1], reverse=False)
        return_list = []
        for r in results:
            return_list.append((self.classes[r[0]], str(r[1])))
            
        return return_list


rinProcess().think("Hello")