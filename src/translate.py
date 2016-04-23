"""Reads in two word embedding language models and a translation matrix, then translates one language into the space
of the other and writes the translated language to a dictionary file
"""

import logging
import collections

import numpy as np
from transmat.space import Space
from transmat.utils import apply_tm

log = logging.getLogger('translate')


def translate_language(source_file, target_file, translation_matrix_file, output_file, num_translations):
    """Translates the language in the source file with the matrix in the translation_matrix_file, then searches the
    language in the target file for the closest words to each word in the source language. The translations are
    written one word per line to the output_file. The format of each line is as follows:

    [source word]: [target word 1] ([target word 1 probability]), [target word 2] ([target word 2 probability]) ...

    The source word is the first word on each line. The soruce word is followed by a colon. Then comes the first target
    word, followed by its probability in parenthesis, then the second possible translation, followed by its probability
    in parenthesis, and so on for however many possible translations you generate for each word.

    The probability of each translation is given by the cosing distance between the source word and the possible
    translation
    """
    
    log.info('Reading in source language')
    source_sp = Space.build(source_file)

    log.info('Reading in the target language')
    target_sp = Space.build(target_file)

    log.info('Reading in translation matrix')
    tm = np.loadtxt(translation_matrix_file)

    source_sp.normalize()
    target_sp.normalize()

    log.info('Transforming into target space')
    mapped_source_sp = apply_tm(source_sp, tm)

    gold = collections.defaultdict(set)
    count = 0

    # Go through all the words in the space's index, getting their closest x equivalents from the target space
    for word, idx in mapped_source_sp.row2id.iteritems():
        log.debug('Translating word %s' % word)
        word_embedding = mapped_source_sp.mat[idx]
        
        closest_words = target_sp.get_closest_words(word_embedding, num_translations)
        
        gold[word] = closest_words
        log.debug('Possible translations: %s' % closest_words)

        count += 1
        if count % 500 == 0:
            log.debug('Translated %d words' % count)

    log.info('Translated all words into the target language')

    with open(output_file, 'w') as f:
        f.write('\n'.join(gold))

