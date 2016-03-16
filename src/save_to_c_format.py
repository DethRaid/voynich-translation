#!/usr/bin/python2
"""
Saves my Spanish, English, and Voynich models to the origin al C format (which I hope has one word per line)
"""

import logging
from gensim.models import Word2Vec

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('save_to_c_format')

    logger.info('Starting processing...')
    
    spanish_model = Word2Vec.load('../corpa/spanish/model.w2v')
    logger.info('Loaded Spanish 300-dim model')

    spanish_model.save_word2vec_format('../corpa/spanish/model-ascii.w2v')
    logger.info('Saved Spanish 300-dim ASCII model')


    voynich_model = Word2Vec.load('../corpa/voynich/model.w2v')
    logger.info('Loaded Voynich 100-dim model')

    voynich_model.save_word2vec_format('../corpa/voynich/model-ascii.w2v')
    logger.info('Saved Voynish 100-dim ASCII model')


    english_model = Word2Vec.load_word2vec_format('../corpa/english/GoogleNews-vectors-negative300.bin', binary=True)
    logger.info('Loaded English 300-dim model')

    english_model.save_word2vec_format('../corpa/english/model-ascii.w2v')
    logger.info('Saved English 300-dim ASCII model')

