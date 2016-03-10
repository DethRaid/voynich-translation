#!/bin/python2

"""
Loads the Spanish words file, training a Word2Vec model on the Spanish words. Saves the model to "../../corpa/spanish/model.w2v" in the binary format
"""

import logging
import os
import multiprocessing
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence

class SpanishIterator(object):
    def __init__(self, dirname):
        self.dirname = dirname

    def __iter__(self):
        for fname in os.listdir(self.dirname):
            for line in open(os.path.join(self.dirname, fname)):
                yield line.split()

def train_model():
    # Iterate through all the files in the target directory
    # Load each one into Word2Vec
    # Save the resulting model

    spanish_sentences = SpanishIterator('../../corpa/spanish')
    spanish_model = Word2Vec(spanish_sentences, window=5, min_count=5, size=300, workers=multiprocessing.cpu_count())

    # save the model
    spanish_model.save('../../corpa/spanish/model.w2v')

