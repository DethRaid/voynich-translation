import morfessor
import functools
import numpy as np
from matplotlib import pyplot as plt


def get_morpho_stats(corpus_filename):
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

    for word in words:
        morphemes_by_word[word] = model.viterbi_segment(word)
        morphemes_per_word[word] = len(morphemes_by_word[word][0])

    __calc_word_stats(morphemes_per_word)

    all_morphs = set()
    for segmentation in model.get_segmentations():
        segs = segmentation[2]
        for seg in segs:
            all_morphs.add(seg)

    __calc_morpheme_stats(all_morphs)


def __calc_word_stats(morphemes_per_word):
    '''Calculates word-level statistics, and shows the appropriate histograms

    Word-level statistics include things like the average number of morphemes per word

    :param morphemes_per_word: A map from word to all the morphemes in that word
    '''
    morphemes_per_word = list(morphemes_per_word.values())
    average_morphemes_per_word = __average(morphemes_per_word)
    print('There are an average of ' + str(average_morphemes_per_word) + ' morphemes per word')

    bins = np.arange(0, 10, 1)  # fixed bin size of 1

    plt.xlim([min(morphemes_per_word) - 5, max(morphemes_per_word) + 5])

    plt.hist(morphemes_per_word, bins=bins, alpha=0.5)
    plt.title('Morphemes per word')
    plt.xlabel('Morphemes')
    plt.ylabel('Count')

    plt.savefig('Morphemes per word.png', bbox_inches='tight')


def __average(l):
    '''Calcualtes the averate value of a list of numbers

    :param l: A list of numbers to get the average of
    :return: The average of the given list
    '''
    return functools.reduce(lambda x, y: x + y, l) / len(l)


def __calc_morpheme_stats(all_morphs):
    '''Calculates morpheme-level statistics, such as the average length of morphemes, and shows the
    morpheme length histogram

    :param all_morphs: A list of all the morphemes in the corpus
    '''
    morpheme_length = [len(x) for x in all_morphs]

    average_morpheme_length = __average(morpheme_length)
    print('Morphemes have an average length of ' + str(average_morpheme_length) + ' characters')

    bins = np.arange(0, 50, 1)  # fixed bin size of 1

    plt.xlim([min(morpheme_length) - 5, max(morpheme_length) + 5])

    plt.hist(morpheme_length, bins=bins, alpha=0.5)
    plt.title('Morpheme length')
    plt.xlabel('Length')
    plt.ylabel('Count')

    plt.savefig('Morpheme length.png', bbox_inches='tight')

