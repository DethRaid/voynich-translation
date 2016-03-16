#!/usr/bin/python2

"""
Goes through every word in the source file, generating a number of translations for it with a certainty for each one

Data is saved in a CSV file where the first column is the source word, and subsequent columns are the
translations, then their certainties
"""

import sys
import numpy as np
import collections
import random
import logging
from transmat.space import Space
from transmap.utils import read_dict, apply_tm, score, get_valid_data

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('translate_corpa')


def main(sys_args):
    log.debug('Starting program')

    try:
        opts, args = getopt.getopt(sys_args[1:], "ht:", ["help", "translations="])

    except getopt.GetoptError, e:
        logger.exception(e)
        useage()
        sys.exit(1)

    log.debug('Parsed command line arguments')

    out_file = './translated_words' 
    translations_per_word = 5
    for opt, val in opts:
        log.debug('Handling argument %s with value %s' % opt, val)

        if opt in ('-t', '--translations'):
            try:
                translations_per_word = int(val)
                log.debug('Providing %d translations per word' % translations_per_word)
            except ValueError:
                log.error("You didn't put a number for the number of translations per word!")
                useage()

        else:
            useage()

    
        tm_file = argv[0]
        source_file = argv[1]
        target_file = argv[2]

    else:
        log.error('I wanted three arguments, but you gave me %d' % len(argv))
        useage()

    log.debug('Loading translation matrix...')
    tm = np.loadtxt(tm_file)

    log.debug('Reading in source words from %s...' % source_file)
    source_sp = Space.build(source_file)

    log.debug('Reading in destination language from %s...' % target_file)
    target_sp = Space.build(target_file)

    log.info('Translating source language into the destination language space')
    mapped_source_sp = apply_tm(source_sp, tm)

    log.info('Translating source words...')
    # Turn the test data into a dictionary from source word to possible translations
    translations = collections.defaultdict(set)
    for word, _ in mapped_source_sp.id2row:
        # Get the x most likely translations for the given word
        log.debug('Translating word %s' % word)


if __name__ == '__main__':
    main(sys.argv)

