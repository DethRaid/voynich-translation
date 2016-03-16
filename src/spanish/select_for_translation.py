#!/usr/bin/python2

"""
Select 30,000 random Spanish words from the Spanish corpa, then selects nine at random to use as anchor points. The anchor point words are printed to a
file so that human can generate their translations
"""

import logging
import random


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('select_for_translation')

    # Read in the Spanish file
    logger.info('Opening Spanish file...')
    lines = []
    with open('../../corpa/spanish/model-ascii.w2v') as f:
        for line in f:
            lines.append(line)

    logger.info('Spanish file read in')

    random.shuffle(lines)
    spanish_vocab = lines[:30000]
    logger.info('Shuffled Spanish words and got the first 30K')

    with open('../../corpa/spanish/model-ascii-30k.w2v', 'w') as f:
        file_data = '\n'.join(spanish_vocab)
        f.write(file_data)

    logger.info('Wrote selected lines to a file')

