"""
Super main Python file to run the whole thing

Relies on gensim and python2
"""

import logging
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence

from concatenate import concatenate_files
from download import download_files

download = False
concatenate = True
train = False

# configure logging
logging.basicConfig(filename='all.log', level=logging.DEBUG)

if __name__ == '__main__':
    # Download all the files
    if download:
        download_files()

    if concatenate:
        concatenate_files()

    if train:
        # Load in the voynich manuscript file and train word2vec on it
        # No need for us to re-parse the manuscript, it should already exist from the Korlin stuff

        # Load in the kinda useless sentences
        voynich_model = Word2Vec(LineSentence('../corpa/voynich/manuscript.evt'))
        logging.info('Loaded voynich model')

        english_model = Word2Vec(LineSentence('../corpa/english/raw_sentences.txt'))
        logging.info('Loaded english model')

        logging.info('Words most similar to day: ' + english_model.most_similar('day'))
        logging.info(voynich_model.most_similar('octhey'))

