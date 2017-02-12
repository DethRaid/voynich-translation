from collections import OrderedDict
from collections import defaultdict

import morfessor
import functools
import numpy as np
from matplotlib import pyplot as plt

__outdir = ''
__language = ''


def __calc_manuscript_stats(morphemed_corpus_name):
    """Calculates some per-corpus stats, such as morpheme frequencies

    :param morphemed_corpus_name: The name of the corpus to analyze. This corpus should be already split into morphemes
    """
    corpus = open(morphemed_corpus_name, 'r')

    morpheme_frequencies = defaultdict(int)
    for line in corpus:
        for morpheme in line.split():
            morpheme_frequencies[morpheme] += 1

    morpheme_counts = list(morpheme_frequencies.values())
    bins = np.arange(0, 200, 1)  # fixed bin size of 1

    plt.xlim([min(morpheme_counts) - 5, max(morpheme_counts) + 5])
    print('Maximum morpheme frequency: ' + str(max(morpheme_counts)))

    plt.hist(morpheme_counts, bins=bins, alpha=0.5)
    plt.title('Morpheme Frequencies - ' + __language)
    plt.xlabel('Morphemes')
    plt.ylabel('Count')

    plt.savefig(__outdir + 'Morpheme frequencies - ' + __language + '.png', bbox_inches='tight')


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

    global __language
    __language = language

    io = morfessor.MorfessorIO()
    words = io.read_corpus_file(corpus_filename)

    model = morfessor.BaselineModel()
    model.train_online(words)

    manuscript = open(corpus_filename, 'r')
    slash_pos = corpus_filename.rfind('/');
    global __outdir
    __outdir = corpus_file[0:slash_pos + 1]
    morphemed_corpus_name = __outdir + 'morpheme manuscript.txt'
    morphemed_manuscript = open(morphemed_corpus_name, 'w')

    lines = list()

    for line in manuscript:
        lines.append(line.split())

    morphemes_by_word = dict()
    morphemes_per_word = dict()
    all_words = str()

    for line in lines:
        for word in line:
            all_words += word
            morphemes_by_word[word] = model.viterbi_segment(word)
            morphemes_per_word[word] = len(morphemes_by_word[word][0])

            for morpheme in morphemes_by_word[word][0]:
                morphemed_manuscript.write(morpheme)
                morphemed_manuscript.write(' ')

        morphemed_manuscript.write('\n')

    __calc_manuscript_stats(morphemed_corpus_name)

    __calc_word_stats(morphemes_per_word)

    all_morphs = set()
    for segmentation in model.get_segmentations():
        segs = segmentation[2]
        for seg in segs:
            all_morphs.add(seg)

    __calc_morpheme_stats(all_morphs)
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

    left = range(len(sorted_frequencies))
    height = list(sorted_frequencies.values())
    plt.bar(left, height, width=1.0, align='center', tick_label=list(sorted_frequencies.keys()), linewidth=1)
    #    plt.xticks(range(len(sorted_frequencies)), sorted_frequencies.keys())

    plt.savefig(__outdir + str(n) + '-gram frequencies - ' + __language)
    plt.clf()


def __calc_word_stats(morphemes_per_word):
    '''Calculates word-level statistics, and shows the appropriate histograms

    Word-level statistics include things like the average number of morphemes per word

    Also graph how often each n-gram of letters appears

    :param morphemes_per_word: A map from word to all the morphemes in that word
    '''

    morphemes_per_word = list(morphemes_per_word.values())
    average_morphemes_per_word = __average(morphemes_per_word)
    print('There are an average of ' + str(average_morphemes_per_word) + ' morphemes per word')

    bins = np.arange(0, 10, 1)  # fixed bin size of 1

    plt.xlim([min(morphemes_per_word) - 5, max(morphemes_per_word) + 5])

    plt.hist(morphemes_per_word, bins=bins, alpha=0.5)
    plt.title('Morphemes per word - ' + __language)
    plt.xlabel('Morphemes')
    plt.ylabel('Count')

    plt.savefig(__outdir + 'Morphemes per word - ' + __language + '.png', bbox_inches='tight')
    plt.clf()


def __average(l):
    '''Calcualtes the averate value of a list of numbers

    :param l: A list of numbers to get the average of
    :return: The average of the given list
    '''
    return functools.reduce(lambda x, y: x + y, l) / len(l)


def __calc_morpheme_stats(all_morphs):
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
    plt.title('Morpheme length - ' + __language)
    plt.xlabel('Length')
    plt.ylabel('Count')

    plt.savefig('Morpheme length - ' + __language + '.png', bbox_inches='tight')
    plt.clf()


if __name__ == '__main__':
    import sys
    corpus_file = sys.argv[1]
    language = sys.argv[2]

    get_morpho_stats(corpus_file, language)
