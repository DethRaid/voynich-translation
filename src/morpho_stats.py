from collections import OrderedDict
from collections import defaultdict

import morfessor
import functools
import numpy as np
from matplotlib import pyplot as plt

__language = ''


def get_morpho_stats(corpus_filename, language):
    '''Determines the morphological statistics of the given corpus file and prints those statistics for all the world
    too see.

    The printed statistics are as follows:
    - Average number of morphemes per word
    - Average number of suffixes per word
    - Average number of prefixes per word
    - Average number of characters per morpheme

    In addition, the following charts are calculated:
    - A histogram of the number of morphemes per word
    - A histogram of the number of prefixes per word
    - A histogram of the number of suffixes per word
    - A histogram of the length of morphemes
    - A histogram of the length of suffixes
    - A histogram of the length of prefixes

    :param corpus_filename: The name of the file to read the corpus from
    :param language: The name of the language you're processing
    '''

    io = morfessor.MorfessorIO()
    words = io.read_corpus_file(corpus_filename)

    model = morfessor.BaselineModel()
    model.train_online(words)

    manuscript = open(corpus_filename, 'r')

    words = list()

    for line in manuscript:
        words += line.split()

    morphemes_by_word = dict()
    morphemes_per_word = dict()
    all_words = str()

    for word in words:
        all_words += word
        morphemes_by_word[word] = model.viterbi_segment(word)
        morphemes_per_word[word] = len(morphemes_by_word[word][0])

    __calc_word_stats(morphemes_per_word, language)

    all_morphs = set()
    for segmentation in model.get_segmentations():
        segs = segmentation[2]
        for seg in segs:
            all_morphs.add(seg)

    __calc_morpheme_stats(all_morphs, language)
    __calculate_ngram_frequencies(all_words, 1)
    __calculate_ngram_frequencies(all_words, 2)


def __calculate_ngram_frequencies(text, n):
    """Calculates the frequencies of all n-grams in the corpus

    :param text: The text to operate on as a raw string
    :param n: The length of the n-grams to operate on
    """
    frequencies = defaultdict(int)

    for i in range(0, len(text), n):
        ngram = text[i:i + n]
        frequencies[ngram] += 1

    sorted_frequencies = OrderedDict(sorted(frequencies.items(), key=lambda t: t[1]))

    plt.bar(range(len(sorted_frequencies)), sorted_frequencies.values(), align='center')
    plt.xticks(range(len(sorted_frequencies)), sorted_frequencies.keys())

    plt.savefig(str(n) + '-gram frequencies - ' + __language)


def __calc_word_stats(morphemes_per_word, language):
    '''Calculates word-level statistics, and shows the appropriate histograms

    Word-level statistics include things like the average number of morphemes per word

    Also graph how often each n-gram of letters appears

    :param morphemes_per_word: A map from word to all the morphemes in that word
    '''

    __language = language

    morphemes_per_word = list(morphemes_per_word.values())
    average_morphemes_per_word = __average(morphemes_per_word)
    print('There are an average of ' + str(average_morphemes_per_word) + ' morphemes per word')

    bins = np.arange(0, 10, 1)  # fixed bin size of 1

    plt.xlim([min(morphemes_per_word) - 5, max(morphemes_per_word) + 5])

    plt.hist(morphemes_per_word, bins=bins, alpha=0.5)
    plt.title('Morphemes per word - ' + language)
    plt.xlabel('Morphemes')
    plt.ylabel('Count')

    plt.savefig('Morphemes per word - ' + language + '.png', bbox_inches='tight')


def __average(l):
    '''Calcualtes the averate value of a list of numbers

    :param l: A list of numbers to get the average of
    :return: The average of the given list
    '''
    return functools.reduce(lambda x, y: x + y, l) / len(l)


def __calc_morpheme_stats(all_morphs, language):
    '''Calculates morpheme-level statistics, such as the average length of morphemes, and shows the
    morpheme length histogram

    Also graph how often each morpheme occurs

    Maybe try to correllate morpheme relative frequencies across languages (morpheme x occurs with the same relative
    freqeuncy as -ed, for example)

    :param all_morphs: A list of all the morphemes in the corpus
    '''
    morpheme_length = [len(x) for x in all_morphs]

    average_morpheme_length = __average(morpheme_length)
    print('Morphemes have an average length of ' + str(average_morpheme_length) + ' characters')

    bins = np.arange(0, 50, 1)  # fixed bin size of 1

    plt.xlim([min(morpheme_length) - 5, max(morpheme_length) + 5])

    plt.hist(morpheme_length, bins=bins, alpha=0.5)
    plt.title('Morpheme length - ' + language)
    plt.xlabel('Length')
    plt.ylabel('Count')

    plt.savefig('Morpheme length - ' + language + '.png', bbox_inches='tight')

