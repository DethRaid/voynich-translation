"""Generates the word2vec model from the given Voynich manuscript file, saving the manuscript in C text format
"""

import logging
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence

from src.stats.morpho_stats import LanguageStats

log = logging.getLogger('generate')


def generate_word2vec_model(language, vector_size, output_filename):
    """Generates a word2vec model from the file with the given filename
    
    Note that this function assumes that one sentence is on each line. If there is more than one sentence per line,
    or less than one sentence per line, I don't expect that you'll get very good word embeddings.

    :param language: The name of the language to generate a model for
    :param vector_size: The number of dimensions you want in the embeddings
    :param output_filename: The file to write the word2vec model to
    """

    # Split the manuscript into morphemes
    morpho_model = LanguageStats(language)

    voynich_model = Word2Vec(LineSentence('corpa/' + language + '/corpus_morphemes.txt'), min_count=1, size=vector_size)
    voynich_model.save_word2vec_format(output_filename)

