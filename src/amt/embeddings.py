"""
:mod:`embeddings` -- Learn embeddings for various languages
===========================================================

.. module:: embeddings
   :platform: Linux
   :synopsis: Learns embeddings for the morphs in various languages
.. modauthor:: David Dubois <dd4942@rit.edu>
"""
import gzip
import logging
import os
from collections import defaultdict
from enum import Enum

from gensim.models import Word2Vec
from gensim.models.wrappers import FastText

_log = logging.getLogger('embeddings')

_corpus_file_tempalte = 'corpa/%s/corpus.txt'


def _flatten(l):
    return [item for sublist in l for item in sublist]


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


class WordModel:
    """Represents a word that has been split into morphs"""
    def __init__(self, text):
        """Creates a word model object for the provided text
        
        :param text: The text that was spit out from Morfessor Cat-MAP. It has a sequence of space-separated tokens
        where each token is a morph, followed by a slash, followed by STM, PRE, or SUF
        """
        tokens = text.split(' ')

        self.stems = []
        self.prefixes = []
        self.suffixes = []

        for token in tokens:
            slashpos = token.index('/')
            morph = token[0:slashpos]
            if token.endswith('PRE'):
                self.prefixes.append(morph)
            elif token.endswith('STM'):
                self.stems.append(morph)
            elif token.endswith('SUF'):
                self.suffixes.append(morph)
            else:
                raise ValueError('Unknown token type for token ' + token)

    def get_whole_word(self):
        return ''.join(self.prefixes) + ''.join(self.stems) + ''.join(self.suffixes)

    def get_all_morphs(self):
        return self.prefixes + self.stems + self.suffixes


class EmbeddingsAlgorithm(Enum):
    FASTTEXT = 0
    WORD2VEC = 2


class LanguageModel:
    def __init__(self, language, dim=100):
        """Learns all the embeddings for a given language

        :param language: The name of the language to learn embeddings for. There must be a file
        `./corpa/<language>/corpus.txt` which provides the corpus to learn the language from
        :return: A tuple of (fastText model for morphs, Morfessor model for the language)
        """
        _log.info('Learning embeddings for language %s' % language)

        self._language = language
        self._language_dir = 'corpa/' + language + '/'

        from src.data_loading import load_language_data
        self._language_data = load_language_data(self._language_dir, 33000)

        self.segmentations = {}
        self._all_morphs = []

        self._word_model = self._generate_word_embeddings(dim=dim)

        _log.info('Embeddings learned')

    def get_all_word_embeddings(self):
        """Gets all the word embeddings known to this model
        
        :return: The word embeddings that this model knows about
        """
        return [self._word_model[word].tolist() for word in _flatten(self._language_data) if word in self._word_model.wv.vocab]

    def _prepare_words_for_catmap(self, catmap_input_filename):
        word_frequencies = defaultdict(int)
        all_words = _flatten(self._language_data)

        for word in all_words:
            word_frequencies[word] += 1

        with gzip.open(catmap_input_filename, 'wt') as catmap_input:
            for word, frequency in word_frequencies.items():
                catmap_input.write('%s %s\n' % (frequency, word))

        _log.info('CatMAP input data in file %s' % catmap_input_filename)

    def _split_corpus_into_morphs(self, force=False):
        """Splits the words of the corpus into their morphemes, then writes those morphemes to a new file called
        'corpus_morphemes.txt'
        """
        # Save the language data, use Morfessor CatMAP to morph it, then read in the morphed data
        # The input format of the data is one word per line, with the word frequency proceeding the word. Let's make
        # that map

        import subprocess
        catmap_input_filename = self._language_dir + 'catmap_input.gz'

        self._prepare_words_for_catmap(catmap_input_filename)
        should_run = force
        if not os.path.isfile(self._language_data + 'morphemes.txt'):
            # Missing the output of the morpheme task? Definitely need to re-run
            should_run = True

        _log.info('Segmenting words...')
        if not force:
            returncode = subprocess.call('make --makefile=morfessor_catmap0.9.2/train/Makefile GZIPPEDINPUTDATA=%s BINDIR=morfessor_catmap0.9.2/bin' % catmap_input_filename, shell=True)
            if returncode != 0:
                _log.fatal('Could not generate morphs')
                exit(returncode)

        _log.info('Segmented words')

        # Copy the segmentations to a better place, and save them internally
        with gzip.open('segmentation.final.gz', 'rt') as segmentations_file:
            with open(self._language_dir + 'morphemes.txt', 'w') as segmentations_output:
                segments = segmentations_file.read()
                segmentations_output.write(segments)

                for line in segments.split('\n'):
                    if len(line) > 0:
                        if line[0] == '#':
                            continue

                        _, word, morphs = _extract_info(line)
                        self.segmentations[word] = WordModel(' '.join(morphs))

        subprocess.call('./cleanup.sh', shell=True)
        _log.info('Cleaned up intermediate data')

        _log.info('Split corpus into morphemes')

    def _data_as_morphs(self):
        for sentence in self._language_data:
            new_sentence = []
            for word in sentence:
                new_sentence += self.segmentations[word].get_all_morphs()
            yield new_sentence

    def _generate_word_embeddings(self, algo=EmbeddingsAlgorithm.WORD2VEC, use_morphs=False, min_count=2, dim=100):
        """Generates the word embeddings for the current language
        
        :param use_morphs: If true, will use the morphed corpus to generate embeddings. If false, will use the raw 
        corpus
        :param min_count: The minimum number of times a word must occur in order for it to be processed
        :param dim: The number of dimensions of the output vectors
        :return: The embeddings for the current languagego
        """
        _log.info('Learning word vectors...')
        if algo == EmbeddingsAlgorithm.WORD2VEC:
            if use_morphs:
                return Word2Vec(sentences=self._language_data, size=dim, min_count=min_count)
            else:
                return Word2Vec(sentences=self._language_data, size=dim, min_count=min_count)
        elif algo == EmbeddingsAlgorithm.FASTTEXT:
            if use_morphs:
                self._split_corpus_into_morphs()
                self._save_language_data('fastTest_input.txt')
                return FastText.train('fastText/fasttext', self._language_dir + 'fasttext_input.txt',
                                      output_file=self._language_dir + 'ft_model', size=dim, min_count=min_count)
            else:
                self._save_language_data('fasttext_input.txt')
                return FastText.train('fastText/fasttext', self._language_dir + 'fasttext_input.txt',
                                      output_file=self._language_dir + 'ft_model', size=dim, min_count=min_count)
        else:
            _log.error('Unknown algorithm %s' % algo)

    def _save_language_data(self, filename):
        """Saves the current language data to the file in the language directory with the provided name
        
        :param filename: The name of the file in the language directory to save the language data to"""
        with open(self._language_dir + filename, 'w') as language_file:
            for sentence in self._language_data:
                language_file.write(' '.join(sentence))
                language_file.write('.\n')
