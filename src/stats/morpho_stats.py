import codecs
import functools
import gzip
import json
import logging
import os
from collections import defaultdict

import morfessor
import numpy as np
from matplotlib import pyplot as plt
from nltk import sent_tokenize

from src.stats.aggregate_stats import aggregate_stats
from src.stats.markov_chain import calc_entropy

_log = logging.getLogger('morpho_stats')


# TODO: Actually get the Romani corpus


def load_compressed_wikipedia(corpus_filename, n):
    """Loads the first n words from the compressed wikipedia we're dealing with
    
    :param corpus_filename: The filename of the wikipedia data 
    :param n: the number of words to read in
    :return: An array of all the sentences in our data, where each sentence is an array of words
    """
    raw_data = _read_wiki_data(corpus_filename)

    return _get_n_words(raw_data, n)


def _read_wiki_data(corpus_filename):
    """Reads the data from the compressed Wikipedia file into memory

    In an effort to cut down on runtime, only the first 1200000 bytes are read into memory. This is a high estimate
    of the amount of data we want. A later step refines this number
    
    This function also counts the number of occurances of each character. Any character which appears less than 0.05% 
    of the time is removed from the data

    :return: The raw data from disk
    """
    import tarfile
    with tarfile.open(corpus_filename, 'r:xz') as tar_file:
        raw_data = ''
        for member in tar_file.getmembers():
            _log.info('Reading from file %s' % member.name)
            member_stream = tar_file.extractfile(member)

            count = 0
            binary_chunks = iter(functools.partial(member_stream.read, 1), "")
            for unicode_chunk in codecs.iterdecode(binary_chunks, 'utf-8'):
                raw_data += unicode_chunk
                count += 1
                if count % 10000 == 0:
                    _log.info('Read in %s characters' % count)
                # 32K words * 10 characters per word = 320000 characters total
                # This is a super high estimate, but all well.
                if count >= 320000:
                    break

    #character_frequencies = defaultdict(int)
    #character_increment = 1.0 / len(raw_data)
    #for char in raw_data:
    #    character_frequencies[char.lower()] += character_increment
    #_log.info('Counted occurrences of each character')

    #data_filtered = [char.lower() for char in raw_data if character_frequencies[char.lower()] > 0.005]
    #_log.info('Filtered out uncommon characters')

    #return ''.join(data_filtered)

    return raw_data


def _load_corpus_file(corpus_filename, n):
    """Reads in the given corpus, splitting it into sentences
    
    This function assumes that the corpus has one sentence per line
    
    :param corpus_filename: The name of the file with the corpus of text
    :param n: The number of words to read in
    :return: A list of sentences, where each sentence is a list of words
    """
    raw_data = _read_corpus_file(corpus_filename)
    return _get_n_words(raw_data, n)


def _read_corpus_file(corpus_filename):
    """Reads in all the data in the file with the name of corpus_filename
    
    This function reads in all the data in the corpus. The corresponding function to load in wikipedia data only loads
    some data. This is potentially a problem but for the purposes of this work it'll be fine, since the corpus files
    are pretty small
    
    :param corpus_filename: The name of the corpus file 
    :return: All the data in the corpus as a single glorious string. Lines are delineated with \\n
    """
    raw_data = ''
    with open(corpus_filename, 'r') as corpus_file:
        for line in corpus_file:
            raw_data += line
            raw_data += '\n'

    return raw_data


def _average(l):
    """Calcualtes the average value of a list of numbers

        :param l: A list of numbers to get the average of
        :return: The average of the given list
        """
    return functools.reduce(lambda x, y: x + y, l) / len(l)


def _flatten(l):
    return [item for sublist in l for item in sublist]


def _get_n_words(raw_data, num_words):
    """Gets N words in raw_data

    Currently, words are considered to be separated by spaces. This is incorrect for languages like vietnamese but 
    right now it's the best I have.

    Non-spoken tokens and tokens in non-native character sets might be included. Not sure yet.

    This method expects that raw_data is a string of Wikipedia data, where each article has [[\d+]] before it. We
    split the text on that token, then randomly select articles until we have enough tokens

    :param raw_data: The raw data to get the tokens from
    :param num_words: The number of words to acquire
    :return: An array of all the sentences we want to deal with. Each sentence is an array of words
    """
    lines = raw_data.split('\n')
    usable_data = []
    cur_num_words = 0

    while cur_num_words < num_words:
        import random
        line_num = random.randint(0, len(lines) - 1)
        line = lines[line_num].split()
        if len(line) == 0:
            continue
        if len(line[0]) == 0:
            continue
        if line[0][0] == '[':
            # The line starts with a [, which means it's probably an article header. We don't want that
            continue
        usable_data.append([x for x in line if x.isalnum()])
        cur_num_words += len(line)

    return usable_data


def _morfessor_iterator_from_list(sentences):
    """Turns the list into the kind of iterator that morfessor likes
    
    :param sentences: A list of sentences, where each sentence is a list of words
    :return: A nice pretty iterator
    """
    io = morfessor.MorfessorIO()
    for sentence in sentences:
        sentence_string = ' '.join(sentence)
        for compound in io.compound_sep_re.split(sentence_string):
            if len(compound) > 0:
                yield 1, io._split_atoms(compound)
        yield 0, ()


def _tokenize_corpus(corpus_data):
    """Takes the incoming data and attempts to split it into sentences, and then into words
    
    :param corpus_data: A list of sentences, where each sentence is a list of words
    :return: A list of sentences, where each sentence is a list of words. Hopefully these are better segmented than the
    input data, though
    """

    from nltk import wordpunct_tokenize
    sentences = sent_tokenize(' '.join(corpus_data))
    lines = []
    for sentence in sentences:
        tokens = wordpunct_tokenize(sentence)
        line = ' '.join(tokens)
        line_alpha = [x for x in line if x.isalpha() or x == ' ']
        line = ''.join(line_alpha)
        lines.append(line.split())

    return lines


def _extract_info(line):
    """Extracts the information from the line
    
    The first token in the line is the count of the word. The other tokens can be combined to form a word, but we'll
    need to remove the tags from them first
    
    :param line: The line which has all the morphs
    :return: The count of the word, and the word
    """
    tokens = line.split()
    count = int(tokens[0])
    morphtokens = [x for x in tokens[1:] if x != '+']

    tokens_in_word = []
    for morph in morphtokens:
        slashpos = morph.find('/')
        tokens_in_word.append(morph[0:slashpos])

    return count, ''.join(tokens_in_word), morphtokens


class LanguageStats:
    """Generates statistics on the provided language

    Because I want to justify making this a class, each stat you can generate is a separate method. It's not just two
    methods but one of them is the constructor, I swear!
    """

    def __init__(self, language):
        """Loads the corpus from the provided language and trains the morfessor model on that corpus

        :param language: The name of the language to use
        """

        self._log = logging.getLogger('stats')
        self._log.info('Beginning stats for language %s' % language)

        self._language = language
        self._language_dir = 'corpa/' + language + '/'
        wiki_filename = self._language_dir + 'wiki_text.tar.lzma'

        if not os.path.isfile(wiki_filename):
            self._log.warning('Wikipedia data not available for language %s. Falling back to hand-created corpus file'
                            % self._language)

            corpus_filename = self._language_dir + 'corpus.txt'
            language_data_raw = _load_corpus_file(corpus_filename, 30278)
            try:
                self._language_data = _tokenize_corpus(language_data_raw)
            except:
                self._log.warning('Could not tokenize %s corpus' % self._language)
                self._language_data = language_data_raw
        else:
            self._log.info('Reading Wikipedia data for language %s' % self._language)
            self._language_data = load_compressed_wikipedia(wiki_filename, 30278)

        self.segmentations = {}
        self._created_morphed_corpus = False
        self._all_morphs = []

        try:
            with open('all_data.json', 'r') as jsonfile:
                self._all_data = json.load(jsonfile)
        except:
            self._all_data = json.loads('{}')

    def generate_morphed_corpus(self):
        """Splits the words of the corpus into their morphemes, then writes those morphemes to a new file called
        'corpus_morphemes.txt'
        """
        # Save the language data, use Morfessor CatMAP to morph it, then read in the morphed data
        # The input format of the data is one word per line, with the word frequency proceeding the word. Let's make
        # that map

        catmap_input_filename = self._language_dir + 'catmap_input.gz'

        self._prepare_words_for_catmap(catmap_input_filename)

        self._log.info('Segmenting words...')
        import subprocess
        returncode = subprocess.call('make --makefile=morfessor_catmap0.9.2/train/Makefile GZIPPEDINPUTDATA=%s BINDIR=morfessor_catmap0.9.2/bin' % catmap_input_filename, shell=True)
        if returncode != 0:
            self._log.fatal('Could not generate morphs')
            exit(returncode)

        self._log.info('Segmented words')
        word_counts = {}

        # Copy the segmentations to a better place, and save them internally
        with gzip.open('segmentation.final.gz', 'rt') as segmentations_file:
            with open(self._language_dir + 'morphemes.txt', 'w') as segmentations_output:
                segments = segmentations_file.read()
                segmentations_output.write(segments)

                for line in segments.split('\n'):
                    if len(line) > 0:
                        if line[0] == '#':
                            continue

                        count, word, morphs = _extract_info(line)
                        self.segmentations[word] = morphs
                        word_counts[word] = count

        subprocess.call('./cleanup.sh', shell=True)
        self._log.info('Cleaned up intermediate data')

        with open(self._language_dir + 'corpus_morphemes.txt', 'w') as morpheme_corpus:
            wordcount = 0
            for line in self._language_data:
                for word in line:
                    wordcount += 1
                    morphemes = self.segmentations[word]
                    morpheme_corpus.write('[')
                    morpheme_corpus.write(' '.join(morphemes))
                    morpheme_corpus.write('] ')

                    self._all_morphs += morphemes

                morpheme_corpus.write('\n')

        self._created_morphed_corpus = True
        self._log.info('Split corpus into morphemes')

    def _prepare_words_for_catmap(self, catmap_input_filename):
        word_frequencies = defaultdict(int)
        all_words = _flatten(self._language_data)
        for word in all_words:
            word_frequencies[word] += 1
        with gzip.open(catmap_input_filename, 'wt') as catmap_input:
            for word, frequency in word_frequencies.items():
                catmap_input.write('%s %s\n' % (frequency, word))
        self._log.info('CatMAP input data in file %s' % catmap_input_filename)

    def calc_ngram_frequencies(self, n):
        """Examines the n-grams in the corpus and generates a graph of their frequencies. The frequencies are sorted
        from most occurent to least occurent

        :param n: The length of the n-grams to look at
        """
        text = '\n'.join(_flatten(self._language_data))
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
        plt.title(str(n) + '-gram Frequencies - ' + self._language)
        plt.xlabel('Frequency')
        plt.ylabel('Number of ' + str(n) + '-grams')

        plt.savefig(self._language_dir + str(n) + '-gram frequencies - ' + self._language)
        plt.clf()

        self.__save_series(str(n) + '-gramFrequencies', frequencies)

        self._log.info('Calculated %s-gram frequency statistics' % n)

    def calc_morpheme_frequency(self):
        morpheme_frequencies = defaultdict(int)
        corpus_morphemed = open(self._language_dir + 'corpus_morphemes.txt', 'r')
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
        plt.title('Morpheme Frequencies > 1 - ' + self._language)
        plt.xlabel('Bins')
        plt.ylabel('Count')
        plt.savefig(self._language_dir + 'Morpheme Frequencies > 1 - ' + self._language + '.png', bbox_inches='tight')

        plt.clf()

        self.__save_series('morphemeFrequency', morpheme_frequencies)
        self._log.info('Calculated morpheme frequency statistics')

    def calc_word_frequency(self):
        """Calculates the frequencies of the words in the corpus"""
        word_frequencies = defaultdict(int)
        total_words = 0

        for line in self._language_data:
            for word in line:
                word_frequencies[word] += 1
                total_words += 1

        # Plot the graph without things that appear once
        frequent_words = {word: freq / total_words for (word, freq) in word_frequencies.items() if freq > 1}

        bins = np.arange(0, 1, 1.0 / len(frequent_words))

        plt.xlim([min(frequent_words.values()) - 0.1, max(frequent_words.values()) + 0.1])
        plt.hist(list(frequent_words.values()), bins=bins, alpha=0.5)
        plt.title('Word Frequencies > 1 - ' + self._language)
        plt.xlabel('Bins')
        plt.ylabel('Count')
        plt.savefig(self._language_dir + 'Word Frequencies > 1 - ' + self._language + '.png', bbox_inches='tight')

        plt.clf()

        self.__save_series('wordFrequency', word_frequencies)
        self._log.info('Calculated word frequency statistics')

    def calc_word_stats(self):
        '''Calculates word-level statistics, and shows the appropriate histograms

    Word-level statistics include things like the average number of morphemes per word

    Also graph how often each n-gram of letters appears

    :param morphemes_per_word: A map from word to all the morphemes in that word
    '''
        num_morphemes_per_word = dict()
        for word, morphs in self.segmentations.items():
            num_morphemes_per_word[word] = len(morphs)

        num_morphemes_per_word = list(num_morphemes_per_word.values())
        average_morphemes_per_word = _average(num_morphemes_per_word)
        self._log.info('There are an average of ' + str(average_morphemes_per_word) + ' morphemes per word')

        bins = np.arange(0, 10, 1)  # fixed bin size of 1

        plt.xlim([min(num_morphemes_per_word) - 5, max(num_morphemes_per_word) + 5])

        plt.hist(num_morphemes_per_word, bins=bins, alpha=0.5)
        plt.title('Morphemes per word - ' + self._language)
        plt.xlabel('Morphemes')
        plt.ylabel('Count')

        plt.savefig(self._language_dir + 'Morphemes per word - ' + self._language + '.png', bbox_inches='tight')
        plt.clf()

        self.__save_series('morphemesPerWord', num_morphemes_per_word)

        self._log.info('Calculated per-word statistics')

    def calc_morpheme_stats(self):
        '''Calculates morpheme-level statistics, such as the average length of morphemes, and shows the
        morpheme length histogram

        Also graph how often each morpheme occurs

        Maybe try to correllate morpheme relative frequencies across languages (morpheme x occurs with the same relative
        freqeuncy as -ed, for example)

        :param all_morphs: A list of all the morphemes in the corpus
        '''
        morpheme_length = [len(x) for x in self._all_morphs]

        average_morpheme_length = _average(morpheme_length)
        self._log.info('Morphemes have an average length of ' + str(average_morpheme_length) + ' characters')

        bins = np.arange(0, 50, 1)  # fixed bin size of 1

        plt.xlim([min(morpheme_length) - 5, max(morpheme_length) + 5])

        plt.hist(morpheme_length, bins=bins, alpha=0.5)
        plt.title('Morpheme length - ' + self._language)
        plt.xlabel('Length')
        plt.ylabel('Count')

        plt.savefig(self._language_dir + 'Morpheme length - ' + self._language + '.png', bbox_inches='tight')
        plt.clf()

        self.__save_series('morphemeLength', morpheme_length)

        self._log.info('Calculated per-morpheme statistics')

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

        self._log.info('Getting word entropy')
        calc_entropy(self.__word_iterator(), self._language_dir, 'word')

        self._log.info('Getting morpheme entropy')
        calc_entropy(self.__morpheme_iterator(), self._language_dir, 'morpheme')

        self._log.info('Getting character entropy')
        calc_entropy(self.__character_iterator(), self._language_dir, 'character')

        self.__save_stats_to_disk()

    def __word_iterator(self):
        """Provides an iterator over all the words in the corpus"""
        for line in self._language_data:
            for word in line:
                yield word
    
    def __character_iterator(self):
        """Provides an iterator over all the letters in the corpus"""
        for line in self._language_data:
            for word in line:
                for letter in word:
                    yield letter

    def __morpheme_iterator(self):
        """Provides an iterator over all the morphemes in the corpus"""
        with open(self._language_dir + 'corpus_morphemes.txt') as corpus:
            for line in corpus:
                for word in line.split():
                    yield word

    def __save_series(self, series_type, series):
        """Saves the data in a provided series to a json file. The goal here is to aggregate all the data from each of
        the analyzed languages so that we can easily compare languages

        :param series_type: The type of data we have. This is the primary key in the json file
        :param series: The actual data series. I expect this to be a list of data points
        """
        if series_type not in self._all_data.keys():
            self._all_data[series_type] = dict()
        self._all_data[series_type][self._language] = series

    def __save_stats_to_disk(self):
        """Saves all the stats for this language to the json file

        The idea here is that I'll only save the stats once per language, leading to less writing of a massive file and
        hopefully better performance"""
        with open('all_data.json', 'w') as jsonfile:
            json.dump(self._all_data, jsonfile)


if __name__ == '__main__':
    import sys
    language = sys.argv[1]
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    if language == 'all':
        try:
            os.remove('all_data.json')  # We want clean data!
        except:
            pass
        open('all_data.json', 'w').close()
        romance_languages = ['french', 'italian', 'spanish']
        germanic_languages = ['german', 'english', 'danish', 'dutch']
        uralic_languages = ['finnish', 'hungarian']
        semitic_languages = ['arabic', 'hebrew']
        slavic_languages = ['russian']
        algonquin_languages = ['arapaho']
        indo_aryan_languages = ['hindi']
        iranian_languages = ['farsi']
        turkic_languages = ['turkish']
        vietic_languages = ['vietnamese']

        languages = []
        languages += romance_languages
        languages += germanic_languages
        languages += uralic_languages
        languages += semitic_languages
        languages += slavic_languages
        languages += algonquin_languages
        languages += indo_aryan_languages
        languages += iranian_languages
        languages += turkic_languages
        languages += vietic_languages
        languages += ['voynichese']
        for language in languages:
            try:
                stats = LanguageStats(language)
                stats.calculate_all_stats()
            except FileNotFoundError as e:
                print('Could not process corpus for language %s' % language)
                print(e)

        aggregate_stats()

    elif language == 'agg':
        # Hack for debugging
        aggregate_stats()

    else:
        stats = LanguageStats(language)
        stats.calculate_all_stats()
