import functools
import json
import logging
from collections import defaultdict

import numpy as np
from matplotlib import pyplot as plt

import morfessor
from src.stats.markov_chain import calc_entropy


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

        self.__logger = logging.getLogger('stats')
        self.__logger.info('Beginning stats for language %s' % language)

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


        try:
            with open('all_data.json', 'r') as jsonfile:
                self.__all_data = json.load(jsonfile)
        except FileNotFoundError:
            self.__all_data = json.loads('{}')

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
        self.__logger.info('Split corpus into morphemes')

    def calc_ngram_frequencies(self, n):
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

        self.__save_series(str(n) + '-gramFrequencies', frequencies)

        self.__logger.info('Calculated %s-gram frequency statistics' % n)

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

        # Plot the graph without things that appear once
        frequent_morphemes = {morph: freq / total_morphemes for (morph, freq) in morpheme_frequencies.items() if freq > 1}

        bins = np.arange(0, 1, 1.0 / len(frequent_morphemes))

        plt.xlim([min(frequent_morphemes.values()) - 0.1, max(frequent_morphemes.values()) + 0.1])
        plt.hist(list(frequent_morphemes.values()), bins=bins, alpha=0.5)
        plt.title('Morpheme Frequencies > 1 - ' + self.__language)
        plt.xlabel('Bins')
        plt.ylabel('Count')
        plt.savefig(self.__language_dir + 'Morpheme Frequencies > 1 - ' + self.__language + '.png', bbox_inches='tight')

        plt.clf()

        self.__save_series('morphemeFrequency', morpheme_frequencies)
        self.__logger.info('Calculated morpheme frequency statistics')

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

        # Plot the graph without things that appear once
        frequent_words = {word: freq / total_words for (word, freq) in word_frequencies.items() if freq > 1}

        bins = np.arange(0, 1, 1.0 / len(frequent_words))

        plt.xlim([min(frequent_words.values()) - 0.1, max(frequent_words.values()) + 0.1])
        plt.hist(list(frequent_words.values()), bins=bins, alpha=0.5)
        plt.title('Word Frequencies > 1 - ' + self.__language)
        plt.xlabel('Bins')
        plt.ylabel('Count')
        plt.savefig(self.__language_dir + 'Word Frequencies > 1 - ' + self.__language + '.png', bbox_inches='tight')

        plt.clf()

        self.__save_series('wordFrequencies', word_frequencies)
        self.__logger.info('Calculated word frequency statistics')

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
        self.__logger.info('There are an average of ' + str(average_morphemes_per_word) + ' morphemes per word')

        bins = np.arange(0, 10, 1)  # fixed bin size of 1

        plt.xlim([min(num_morphemes_per_word) - 5, max(num_morphemes_per_word) + 5])

        plt.hist(num_morphemes_per_word, bins=bins, alpha=0.5)
        plt.title('Morphemes per word - ' + self.__language)
        plt.xlabel('Morphemes')
        plt.ylabel('Count')

        plt.savefig(self.__language_dir + 'Morphemes per word - ' + self.__language + '.png', bbox_inches='tight')
        plt.clf()

        self.__save_series('morphemesPerWord', num_morphemes_per_word)

        self.__logger.info('Calculated per-word statistics')

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
        self.__logger.info('Morphemes have an average length of ' + str(average_morpheme_length) + ' characters')

        bins = np.arange(0, 50, 1)  # fixed bin size of 1

        plt.xlim([min(morpheme_length) - 5, max(morpheme_length) + 5])

        plt.hist(morpheme_length, bins=bins, alpha=0.5)
        plt.title('Morpheme length - ' + self.__language)
        plt.xlabel('Length')
        plt.ylabel('Count')

        plt.savefig(self.__language_dir + 'Morpheme length - ' + self.__language + '.png', bbox_inches='tight')
        plt.clf()

        self.__save_series('morphemeLength', morpheme_length)

        self.__logger.info('Calculated per-morpheme statistics')

    def calculate_all_stats(self):
        """Calculates all the stats for the language given in the constructor
        """
        self.generate_morphed_corpus()
        self.calc_morpheme_frequency()
        self.calc_word_frequency()
        self.calc_morpheme_stats()
        self.calc_word_stats()
        self.calc_ngram_frequencies(1)
        self.calc_ngram_frequencies(2)
        self.calc_ngram_frequencies(3)

        self.__logger.info('Getting word entropy')
        calc_entropy(self.__word_iterator(), self.__language_dir, 'word')

        self.__logger.info('Getting morpheme entropy')
        calc_entropy(self.__morpheme_iterator(), self.__language_dir, 'morpheme')

        self.__logger.info('Getting character entropy')
        calc_entropy(self.__character_iterator(), self.__language_dir, 'character')

        self.__save_stats_to_disk()

    def __word_iterator(self):
        """Provides an iterator over all the words in the corpus"""
        corpus = open(self.__corpus_filename)
        for line in corpus:
            for word in line.split():
                yield word
                
        corpus.close()
    
    def __character_iterator(self):
        """Provides an iterator over all the letters in the corpus"""
        corpus = open(self.__corpus_filename)
        for line in corpus:
            for word in line.split():
                for letter in word:
                    yield letter

        corpus.close()
    
    def __morpheme_iterator(self):
        """Provides an iterator over all the morphemes in the corpus"""
        corpus = open(self.__language_dir + 'corpus_morphemes.txt')
        for line in corpus:
            for word in line.split():
                yield word

        corpus.close()

    @staticmethod
    def __average(l):
        """Calcualtes the average value of a list of numbers

        :param l: A list of numbers to get the average of
        :return: The average of the given list
        """
        return functools.reduce(lambda x, y: x + y, l) / len(l)

    def __save_series(self, series_type, series):
        """Saves the data in a provided series to a json file. The goal here is to aggregate all the data from each of
        the analyzed languages so that we can easily compare languages

        :param series_type: The type of data we have. This is the primary key in the json file
        :param series: The actual data series. I expect this to be a list of data points
        """
        if series_type not in self.__all_data.keys():
            self.__all_data[series_type] = dict()
        self.__all_data[series_type][self.__language] = series

    def __save_stats_to_disk(self):
        """Saves all the stats for this language to the json file

        The idea here is that I'll only save the stats once per language, leading to less writing of a massive file and
        hopefully better performance"""
        with open('all_data.json', 'w') as jsonfile:
            json.dump(self.__all_data, jsonfile)


def aggregate_stats():
    """Reads in the stats in the saved json file, then prints all the stats for each language onto the same graph for
    easy comparison"""

    with open('all_data.json', 'r') as jsonfile:
        all_data = json.load(jsonfile)

        for series_type, language_data in all_data.items():
            for language, data in language_data.items():
                bins = np.arange(0, 50, 1)  # fixed bin size of 1

                if isinstance(data, list):
                    plt.xlim([min(data) - 5, max(data) + 5])
                    plt.hist(data, bins=bins, alpha=0.5, label=language, histtype='bar')

                elif isinstance(data, dict):
                    plot_data = list(data.values())
                    plt.xlim([min(plot_data) - 5, max(plot_data) + 5])
                    plt.hist(plot_data, bins=bins, alpha=0.5, label=language, histtype='bar')

            plt.title(series_type)
            plt.legend()
            plt.xlabel('Length')
            plt.ylabel('Count')

            plt.savefig(series_type + '.png', bbox_inches='tight')
            plt.clf()


if __name__ == '__main__':
    import sys
    language = sys.argv[1]
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    if language == 'all':
        languages = ['voynichese', 'english', 'finnish', 'arapaho', 'arabic', 'hebrew']
        for language in languages:
            stats = LanguageStats(language)
            stats.calculate_all_stats()

        aggregate_stats()

    elif language == 'agg':
        # Hack for debugging
        aggregate_stats()

    else:
        stats = LanguageStats(language)
        stats.calculate_all_stats()
