"""Runs the spanish test using the scripts in spanish
"""

import sys
import logging
import collections
import multiprocessing
from random import shuffle

from transmat.space import Space
from transmat.utils import train_tm, apply_tm
from spanish.train import __train_model, __get_anchor_words, __evaluate_translation
from gensim.models import Word2Vec


logging.basicConfig(filename='all.log', level=logging.DEBUG)

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

log = logging.getLogger('spanish_run')


def run(words_to_translate, english_model, gold):
    """Tries to translate all the words in words_to_translate into English, writing the results to gold

    :param words_to_translate: A list of tuples from word to embedding of the words to translate
    :param english_model: The English model to translate the words into
    :param gold: A multiproces.Queue that lets this function output the translated words
    """ 
    count = 0
    for word, embedding in words_to_translate:
        closest_words = english_model.get_closest_words(embedding, 10)
        gold.put((word, closest_words))
        count += 1
        if count % 10 == 0:
            log.info('Tranlsated %d words' % count)


def __print_most_likely_translations(evaluations, gold):
    """Looks through the evaluations and writes the most likely translation for each word

    :param evaluations: A dict from word to tuples of translations with their liklihoow from Google
    :param gold: The translations that my system generated
    """
    with open('../output/spanish-3/distances.csv', 'w') as f:
        # Write down the column names
        f.write('Spanish Word,Translation,Transmat Score,Google Score,Index')

        for word, trans in evaluations.iteritems():
            # Get the most likely evaluation
            best_word = ''
            best_score = -1000
            best_count = 0
            count = 0
            log.info('Translations: %s' % str(trans))
            for trans_word, score in trans:
                if score > best_score:
                    best_score = score
                    best_word = trans_word
                    best_count = count
                count += 1

            transmat_score = gold[word][best_count][1]

            # Write them down
            f.write('\n%s,%s,%f,%f,%d' % (word, best_word, transmat_score, best_score, best_count))


def run_spanish_test():
    """Runs the translation algorithm on the Spanish corpus, then evaluates the translations

    A lot of the comments and variable names in this function are inaccurate. They say 'thread' when they should say
    'process'. Any future maintainers should tkae heed of this and shouldn't actually expect threads
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

    anchor_words = __get_anchor_words(spanish_vocab, english_vocab, 1000)
    log.info('Generated anchor words')

    tm = train_tm(spanish_space, english_space, anchor_words)
    log.info('Generated translation matrix')

    translated_spanish_space = apply_tm(spanish_space, tm)
    log.info('Translated Spanish word vectors')

    # cores * 2 threads takes about 0:01:18 per word. That's about 0.2 words per second
    # cores threads takes about 0:01:00 per word. That's about 0.1333 words per second
    # cores / 2 threads takes about 30 seconds per word. Maybe a little less. That's about equal to the above
    num_threads = multiprocessing.cpu_count()
    thread_results = list()     # List to hold all the results that each thread comes up with
    threads = list()

    spanish_words = list()
    for word, idx in translated_spanish_space.row2id.iteritems():
        spanish_words.append((word, translated_spanish_space.mat[idx]))

    step = 7000 / num_threads
    step = 10    # Use a small amount of data to test things
    # Start a bunch of threads to handle translating different parts of the Spanish space
    shuffle(spanish_words)
    for i in range(num_threads):
        single_gold = multiprocessing.Queue()
        thread_results.append(single_gold)

        thread = multiprocessing.Process(target=run, args=(spanish_words[i * step:(i + 1) * step], english_space, single_gold))
        thread.start() 
        threads.append(thread)

    log.info('Started %d threads; each one is responsible for %d words' % (num_threads, step))

    # Wait until all threads finish
    for thread in threads:
        thread.join()

    # Acquire ALL the translations!

    gold = dict()

    for single_gold in thread_results:
        while not single_gold.empty():
            word, translations = single_gold.get()
            gold[word] = translations

    log.info('Found English translations')

    log.info('Loading English word2vec model')
    english_model = Word2Vec.load_word2vec_format('../corpa/english/GoogleNews-vectors-negative300.bin', binary=True)
    log.info('English model loaded')
    evaluations = __evaluate_translation(gold, english_model)
    log.info('Evaluated translations')

    # What data do I want? I want to know the most likely translation for each word, and I want to print those to a
    # csv file or something
    __print_most_likely_translations(evaluations, gold)
    log.info('Wrote translations to a file')


if __name__ == '__main__':
    run_spanish_test()

