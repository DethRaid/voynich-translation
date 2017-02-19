from collections import OrderedDict
from collections import defaultdict

import morfessor
import functools
import numpy as np
from matplotlib import pyplot as plt

__outdir = ''
__language = ''


# TODO: Build language model to examine character, word, and morpheme entropies
# TODO: Get Arabic of Hebrew corpra (with and without vowels)
# TODO: Actually get the Romani corpus

class LanguageStats:
    """Generates statistics on the provided language

    Because I want to justify making this a class, each stat you can generate is a separate method. It's not just two
    methods but one of them is the constructor, I swear!
    """

    def __init__(self, language):
        """Loads the corpus from the provided language and trains the morfessor model on that corpus

        :param language: The name of the language to use
        """

        self.__language = language
        self.__language_dir = 'corpa/' + language + '/'
        self.__corpus_filename = self.__language_dir + 'corpus.txt'

        io = morfessor.MorfessorIO()
        words = io.read_corpus_file(self.__corpus_filename)

        self.__model = morfessor.BaselineModel()
        self.__model.train_online(words)
        self.__created_morphed_corpus = False
        self.__all_morphs = list()

        for segmentation in self.__model.get_segmentations():
            self.__all_morphs.append(segmentation[2])

    def generate_morphed_corpus(self):
        """Splits the words of the corpus into their morphemes, then writes those morphemes to a new file called
        'corpus_morphemes.txt'
        """
        corpus = open(self.__corpus_filename, 'r')
        morpheme_corpus = open(self.__language_dir + 'corpus_morphemes.txt', 'w')
        for line in corpus:
            words = line.split()
            for word in words:
                morphemes = self.__model.viterbi_segment(word)[0]
                for morpheme in morphemes:
                    morpheme_corpus.write(morpheme + ' ')

            morpheme_corpus.write('\n')

        corpus.close()
        morpheme_corpus.close()

        self.__created_morphed_corpus = True

    def calculate_ngram_freqiencies(self, n):
        """Examines the n-grams in the corpus and generates a graph of their frequencies. The frequencies are sorted
        from most occurent to least occurent

        :param n: The length of the n-grams to look at
        """
        corpus = open(self.__corpus_filename)
        text = corpus.read().replace(' ', '').replace('\n', '')
        frequencies = defaultdict(int)
        total_ngrams = 0

        for i in range(0, len(text), n):
            ngram = text[i:i + n]
            frequencies[ngram] += 1
            total_ngrams += 1

        for ngram, frequency in frequencies.items():
            frequencies[ngram] = frequency / total_ngrams

        bins = np.arange(0, 1, 1.0 / len(frequencies))
        plt.xlim([min(frequencies.values()) - 0.05, max(frequencies.values()) + 0.1])

        plt.hist(list(frequencies.values()), bins=bins, alpha=0.5)
        plt.title(str(n) + '-gram Frequencies - ' + self.__language)
        plt.xlabel('Frequency')
        plt.ylabel('Number of ' + str(n) + '-grams')

        plt.savefig(self.__language_dir + str(n) + '-gram frequencies - ' + self.__language)
        plt.clf()

    def calc_morpheme_frequency(self):
        morpheme_frequencies = defaultdict(int)
        corpus_morphemed = open(self.__language_dir + 'corpus_morphemes.txt', 'r')
        total_morphemes = 0

        # Collect morpheme counts
        for line in corpus_morphemed:
            for morpheme in line.split():
                morpheme_frequencies[morpheme] += 1
                total_morphemes += 1

        corpus_morphemed.close()

        # Normalize the counts
        morpheme_frequencies_norm = {morph: freq / total_morphemes for (morph, freq) in morpheme_frequencies.items()}

        bins = np.arange(0, 1, 1.0 / len(morpheme_frequencies_norm))

        plt.xlim([min(morpheme_frequencies_norm.values()) - 0.1, max(morpheme_frequencies_norm.values()) + 0.1])
        plt.hist(list(morpheme_frequencies_norm.values()), bins=bins, alpha=0.5)
        plt.title('Morpheme Frequencies - ' + self.__language)
        plt.xlabel('Bins')
        plt.ylabel('Count')
        plt.savefig(self.__language_dir + 'Morpheme Frequencies - ' + self.__language + '.png', bbox_inches='tight')

        plt.clf()

        # Plot the graph again, but without things that appear once
        frequent_morphemes = {morph: freq / total_morphemes for (morph, freq) in morpheme_frequencies.items() if freq > 1}

        bins = np.arange(0, 1, 1.0 / len(frequent_morphemes))

        plt.xlim([min(frequent_morphemes.values()) - 0.1, max(frequent_morphemes.values()) + 0.1])
        plt.hist(list(frequent_morphemes.values()), bins=bins, alpha=0.5)
        plt.title('Morpheme Frequencies > 1 - ' + self.__language)
        plt.xlabel('Bins')
        plt.ylabel('Count')
        plt.savefig(self.__language_dir + 'Morpheme Frequencies > 1 - ' + self.__language + '.png', bbox_inches='tight')

        plt.clf()


    def calc_word_frequency(self):
        """Calculates the frequencies of the words in the corpus"""
        word_frequencies = defaultdict(int)
        corpus = open(self.__corpus_filename, 'r')
        total_words = 0

        for line in corpus:
            for word in line.split():
                word_frequencies[word] += 1
                total_words += 1

        corpus.close()

        word_frequencies_normalized = {word: freq / total_words for (word, freq) in word_frequencies.items()}

        bins = np.arange(0, 1, 1.0 / len(word_frequencies_normalized))

        plt.xlim([min(word_frequencies_normalized.values()) - 0.1, max(word_frequencies_normalized.values()) + 0.1])
        plt.hist(list(word_frequencies_normalized.values()), bins=bins, alpha=0.5)
        plt.title('Word Frequencies - ' + self.__language)
        plt.xlabel('Bins')
        plt.ylabel('Count')
        plt.savefig(self.__language_dir + 'Word Frequencies - ' + self.__language + '.png', bbox_inches='tight')

        plt.clf()

        # Plot the graph again, but without things that appear once
        frequent_words = {word: freq / total_words for (word, freq) in word_frequencies.items() if freq > 1}

        bins = np.arange(0, 1, 1.0 / len(frequent_words))

        plt.xlim([min(frequent_words.values()) - 0.1, max(frequent_words.values()) + 0.1])
        plt.hist(list(frequent_words.values()), bins=bins, alpha=0.5)
        plt.title('Word Frequencies > 1 - ' + self.__language)
        plt.xlabel('Bins')
        plt.ylabel('Count')
        plt.savefig(self.__language_dir + 'Word Frequencies > 1 - ' + self.__language + '.png', bbox_inches='tight')

        plt.clf()


    def calc_word_stats(self):
        '''Calculates word-level statistics, and shows the appropriate histograms

    Word-level statistics include things like the average number of morphemes per word

    Also graph how often each n-gram of letters appears

    :param morphemes_per_word: A map from word to all the morphemes in that word
    '''
        num_morphemes_per_word = dict()
        for segments in self.__model.get_segmentations():
            num_morphemes_per_word[segments[1]] = len(segments[2])

        num_morphemes_per_word = list(num_morphemes_per_word.values())
        average_morphemes_per_word = self.__average(num_morphemes_per_word)
        print('There are an average of ' + str(average_morphemes_per_word) + ' morphemes per word')

        bins = np.arange(0, 10, 1)  # fixed bin size of 1

        plt.xlim([min(num_morphemes_per_word) - 5, max(num_morphemes_per_word) + 5])

        plt.hist(num_morphemes_per_word, bins=bins, alpha=0.5)
        plt.title('Morphemes per word - ' + self.__language)
        plt.xlabel('Morphemes')
        plt.ylabel('Count')

        plt.savefig(self.__language_dir + 'Morphemes per word - ' + self.__language + '.png', bbox_inches='tight')
        plt.clf()

    def calc_morpheme_stats(self):
        '''Calculates morpheme-level statistics, such as the average length of morphemes, and shows the
        morpheme length histogram

        Also graph how often each morpheme occurs

        Maybe try to correllate morpheme relative frequencies across languages (morpheme x occurs with the same relative
        freqeuncy as -ed, for example)

        :param all_morphs: A list of all the morphemes in the corpus
        '''
        morpheme_length = [len(x) for x in self.__all_morphs]

        average_morpheme_length = self.__average(morpheme_length)
        print('Morphemes have an average length of ' + str(average_morpheme_length) + ' characters')

        bins = np.arange(0, 50, 1)  # fixed bin size of 1

        plt.xlim([min(morpheme_length) - 5, max(morpheme_length) + 5])

        plt.hist(morpheme_length, bins=bins, alpha=0.5)
        plt.title('Morpheme length - ' + self.__language)
        plt.xlabel('Length')
        plt.ylabel('Count')

        plt.savefig('Morpheme length - ' + self.__language + '.png', bbox_inches='tight')
        plt.clf()

    def calculate_all_stats(self):
        """Calculates all the stats for the language given in the constructor
        """
        self.generate_morphed_corpus()
        self.calc_morpheme_frequency()
        self.calc_word_frequency()
        self.calc_morpheme_stats()
        self.calc_word_stats()
        self.calculate_ngram_freqiencies(1)
        self.calculate_ngram_freqiencies(2)
        self.calculate_ngram_freqiencies(3)

    def __average(self, l):
        '''Calcualtes the average value of a list of numbers

        :param l: A list of numbers to get the average of
        :return: The average of the given list
        '''
        return functools.reduce(lambda x, y: x + y, l) / len(l)


if __name__ == '__main__':
    import sys
    language = sys.argv[1]

    stats = LanguageStats(language)
    stats.calculate_all_stats()
