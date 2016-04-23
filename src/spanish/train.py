#!/bin/python2

"""Reads in the Spanish model file, tokenized the words, figures out which words are named entities, removes the
named entities, selects the 7000 most common words, selects five words at random, uses Google Translate to get
their translations, trains a translation matrix on those words, writes the translation matrix to a file, then evaluates
the translations.

That's a lot of things to do. No single-responsibility principle here!
"""

import logging
import os
import random
import multiprocessing
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
from googleapiclient.discovery import build


log = logging.getLogger('spanish')


class __SpanishIterator(object):
    def __init__(self, dirname):
        self.dirname = dirname
        self.named_entities = list()

    def __iter__(self):
        for fname in os.listdir(self.dirname):
            for line in open(os.path.join(self.dirname, fname)):
                self.___add_named_entities(line)
                yield line.split()

    def __add_named_entities(self, line):
        words = nltk.word_tokenize(line)
        tags = nltk.pos_tag(words)
        chunks = nltk.ne_chunk(tags)

        for tree in chunks:
            if hasattr(tree, 'label') and tree.label:
                if tree.label == 'NE':
                    # If the thing is a named entity, save it so we know what the named entities are
                    self.named_entities.append(tree[0])


def __filter_w2v_model(filename, words_to_remove, num_to_keep):
    """Filters the words in the Spanish model, removing all the words in the given list and returning the top x words

    :param filename: The name of the file to read the words in from
    :param words_to_remove: A list of all the words to get rid of
    :param num_to_keep: The number of words to keep
    """
    good_words = list()

    with open(filename, 'r') as f:
        for line in f:
            for word in words_to_remove:
                if not line.startswith(word):
                    good_words.append(line)

    random.shuffle(good_words)

    kept_words = good_words[:num_to_keep]

    with open('tempmodel', 'w') as f:
        for word in kept_words:
            f.write(word)
            f.write('\n')

    return Word2Vec.load_word2vec_format('tempmodel')


def __train_model(filename):
    """Iterate through all the files in the target directory, load each one into Word2Vec

    This file saves the word2vec model to a file. This is so I can operate on the vocab. I can't find any way to
    change the vocab once a word2vec model is trained, which makes me cry a lot

    I'm training the model on the whole Spanish corpus, then discarding all but 7000 words. Why would I do this? If I
    want to test if the Voynich model is accurate, shouldn't I have the same amount of training data as the Voynich
    model has? In theory, yes, but this test is to see how many words I need in order to properly align two vector,
    spaces not how accurate word2vec models are when given very little data. To that end, I train the Spanish word2vec
    model so that it has maximum accuracy, so I know that all the inaccuracy in my final results comes from the vector
    space alignment step, and not from any other part of the process.
    
    :param filename: The file to save the word2vec model to
    """

    spanish_sentences = __SpanishIterator('../../corpa/spanish')
    spanish_model = Word2Vec(spanish_sentences, window=5, min_count=5, size=300, workers=multiprocessing.cpu_count())

    named_entities = spanish_sentences.named_entities

    spanish_model.save_word2vec_format('model.w2v')

    spanish_model = __filter_w2v_model('model.w2v', named_entities, 7000)
    spanish_model.save_word2vec_format(filename)


def __get_anchor_words(spanish_vocab, english_vocab, num_words):
    """Randomly selects num_words words from the Spanish vocabulary and translates them with Google Translate,
    verifying that the translations are in the English vocabulary.

    :param spanish_vocab: A list of the words in the Spanish vocabulary
    :param english_vocab: A list of the words in the English vocab
    :param num_words: The number of anchor words to generate
    :return: A list of tuples, where each tuple is a Spanish word with its English translation
    """

    # Read in the API key
    key = ''
    with open('google-translate.key') as f:
        key = f.read().strip()

    # Get the translation service
    service = build('translate', 'v2', developerKey=key)

    anchor_words = list()
    counter = 0
    for word in spanish_vocab:
        translation = service.translations().list(source='es', target='en', q=[word]).execute()['translations'][0]['translatedText'] 
        log.debug('%s translated as %s' % (word, translation))
        
        if translation in english_vocab:
            anchor_words.append((word, translation))

        if len(anchor_words) >= num_words:
            return anchor_words


def __evaluate_translation(translations, english_model):
    """Evaluates the quality of the Spanish to English translations by sending all the translated words to Google
    Translate and checking how far the words that Google returned are from the word that the algorithm produced

    Google may return more than one translation, so the one that's closest to the translation that the model produced
    is used for evaluation

    :param translations: A list of tuples from Spanish word to English translations. Since these are the translations
    that are going to get validated, they should have been generated by the translation matrix
    :param english_model: The English word2vec model
    :return: A list of TranslationResult objects that show how close 
    """



