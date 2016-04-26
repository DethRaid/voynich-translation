"""Runs the spanish test using the scripts in spanish/
"""

import sys
import logging

from transmat.space import Space
from transmat.utils import train_tm, apply_tm
from spanish.train import __train_model, __get_anchor_words, __evaluate_translation


logging.basicConfig(filename='all.log', level=logging.DEBUG)

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

log = logging.getLogger('spanish_run')


def run_spanish_test():
    """Runs the translation algorithm on the Spanish corpus, then evaluates the translations
    """
    # __train_model('../corpa/spanish/evaluation-model.w2v')
    # log.info('Generated Spanish model')

    spanish_space = Space.build('../corpa/spanish/model-ascii.w2v', total_count=7000, only_lower=True)
    english_space = Space.build('../corpa/english/model-ascii.w2v')

    spanish_space.normalize()
    english_space.normalize()

    spanish_vocab = spanish_space.row2id.keys()
    english_vocab = english_space.row2id.keys()
    log.info('Read in Spanish and English vocabularies')

    anchor_words = __get_anchor_words(spanish_vocab, english_vocab, 7)
    log.info('Generated anchor words')

    tm = train_tm(spanish_space, english_space, anchor_words)
    log.info('Generated translation matrix')

    translated_spanish_space = apply_tm(spanish_space, tm)
    log.info('Translated Spanish word vectors')

    gold = collections.defaultdict(set)
    count = 0
    for word, idx in translated_spanish_space.row2id.iteritems():
        word_embedding = translated_spanish_space.mat[idx]
        
        closest_words = english_space.get_closest_words(word_embedding, 10)
        gold[word] = closest_words

        count += 1
        if count % 500 == 0:
            log.debug('Translated %d words' % count)
    log.info('Found English translations')

    evaluations = __evaluate_translation(gold, english_vocab)
    log.info('Evaluated translations')
    print evaluations


if __name__ == '__main__':
    run_spanish_test()

