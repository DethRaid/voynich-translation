import codecs
import functools
import logging
import os

_log = logging.getLogger('data_loading')


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

    # character_frequencies = defaultdict(int)
    # character_increment = 1.0 / len(raw_data)
    # for char in raw_data:
    #    character_frequencies[char.lower()] += character_increment
    # _log.info('Counted occurrences of each character')

    # data_filtered = [char.lower() for char in raw_data if character_frequencies[char.lower()] > 0.005]
    # _log.info('Filtered out uncommon characters')

    # return ''.join(data_filtered)

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


def _tokenize_corpus(corpus_data):
    """Takes the incoming data and attempts to split it into sentences, and then into words

    :param corpus_data: A list of sentences, where each sentence is a list of words
    :return: A list of sentences, where each sentence is a list of words. Hopefully these are better segmented than the
    input data, though
    """

    from nltk import wordpunct_tokenize
    from nltk import sent_tokenize
    sentences = sent_tokenize(' '.join(corpus_data))
    lines = []
    for sentence in sentences:
        tokens = wordpunct_tokenize(sentence)
        line = ' '.join(tokens)
        line_alpha = [x for x in line if x.isalpha() or x == ' ']
        line = ''.join(line_alpha)
        lines.append(line.split())

    return lines


def load_language_data(language_dir, num_words):
    wiki_filename = language_dir + 'wiki_text.tar.lzma'
    if not os.path.isfile(wiki_filename):
        _log.warning('Wikipedia data not available. Falling back to hand-created corpus file')

        corpus_filename = language_dir + 'corpus.txt'
        language_data_raw = _load_corpus_file(corpus_filename, num_words)
        try:
            _language_data = _tokenize_corpus(language_data_raw)
        except:
            _log.warning('Could not tokenize corpus')
            _language_data = language_data_raw
    else:
        _log.info('Reading Wikipedia data')
        _language_data = load_compressed_wikipedia(wiki_filename, num_words)

    return _language_data
