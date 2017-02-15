"""Prepares an English corpus for fun time
"""

import chardet
import os
import codecs
import io
import logging
import re
import nltk
import nltk.data
import time
from gensim.models import Word2Vec


log = logging.getLogger('prepare')


def __handle_markdown_corpus(corpus_file):
    """Reads in a corpus as markdown, saving it to /corpa/english/corpus.txt

    :param corpus_file: The name of the file to get the corpus from
    """

    log.info('Opening corpus file %s' % corpus_file)

    lines = []
    cur_line = ''
    with open(corpus_file) as f:
        # Read in all the lines of the corpus. If we find two lines with only a single newline between them, insert a
        # space between them and continue. If we find two spaces between a line, insert a newline between them

        for line in f: 
            log.debug('looking at line "%s"' % line)
            # Is the current line just a newline?
            if re.match('[a-zA-Z0-9"\'(]', line[0]) is None:
                # Cool. Whatever the last line is, append it to cur_line. Add cur_line to the lines array, and
                # reset cur_line
                cur_line += line[:-2]
                log.debug('Appending current line to the lines array. Line is: %s' % cur_line)
                lines.append(cur_line)
                cur_line = ''

            else:
                # Oh, so the current line is more than just a newline. Append it to cur_line with a space before it
                cur_line += ' ' + line[-1]
                log.debug('Appending line from file to cur_line')
        lines.append(cur_line)

    log.info('Read in all data')
    log.debug('\n'.join(lines))
 
    # Okay, we have all the lines in the lines array. I should iterate over all those lines and split them into
    # sentences
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    with open('../corpa/english/corpus.txt', 'w') as f:
        for line in lines:
            line_split = tokenizer.tokenize(line)
            f.write('\n'.join(line_split))

    log.info('Wrote sentences to the corpus file')
    return lines


def __handle_wikipedia_corpus(corpus_file):
    """Reads in a corpus as a Wikipedia data dump, saving the corpus to /corpa/english/corpus.txt

    :param corpus_file: The name of the file to get the corpus from
    """


def __handle_nice_corpus(corpus_file):
    """Handles a corpus that's already kinda nicely formatted. We just have to split it into sentences
    
    Also removes some dumb characters, like underscores

    :param corpus_file: The name of the file that the English corpus resides in
    :return: The array of sentences in the file
    """

    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    # Try to figure out the encoding of our file
    num_bytes = min(32, os.path.getsize(corpus_file))
    raw = open(corpus_file, 'rb').read(num_bytes)
    result = chardet.detect(raw)
    encoding = result['encoding']
    log.debug('Encoding of file is %s' % encoding)

    lines = []
    with io.open(corpus_file, 'r', encoding=encoding) as f:
        for line in f:
            line_no_understores = str()
            for char in line:
                if char != '_':
                    line_no_understores += char
            line_split = tokenizer.tokenize(line_no_understores)   # The lines just got punk't!
            lines += line_split

    return lines


def __tag_parts_of_speech(sentences):
    """Figures out the parts of speech of each words, outputting the words with their parts of speech

    :param sentences: An array of all the sentences to tag the words in
    :return: The sentences, where each words is like <word>|<POS>
    """
    tagged_sentences = list()
    for sentence in sentences: 
        tokens = nltk.word_tokenize(sentence) 
        tags = nltk.pos_tag(tokens)
        tagged_sentence = list()
        for tag in tags:
            tagged_sentence.append('|'.join(tag))
        tagged_sentences.append(' '.join(tagged_sentence))

    return tagged_sentences


def prepare_english_corpus(corpus_file, corpus_type, vector_size):
    """Prepares the English corpus for use as a word2vec model
    
    This function does a couple things. First, it takes the English corpus and puts it into a new file, corpus.txt,
    with one sentence per line. Then, it trains a word2vec model on that corpus, outputting the model (In C format!) to
    /corpa/english/model.v2w.
    
    :param corpus_file: The file to read the corpus from
    :param corpus_type: The tyoe of the corpus. Valid values are 'wiki' for a Wikipedia corpus and 'md' for a corpus
    that should be treated like markdown

    :return: The Word2Vec model of the English corpus
    """

    log.setLevel(logging.INFO)
    log.info("Starting corpus processing at " + str(time.time()))

    if corpus_type == 'md':
        lines = __handle_markdown_corpus(corpus_file)

    elif corpus_type == 'wiki':
        lines = __handle_wikipedia_corpus(corpus_file)

    elif corpus_type == 'none':
       lines = __handle_nice_corpus(corpus_file)

    else:
        log.error('Incorrect corpus format given')
        raise ValueError('Incorrect corpus format given')

    log.info('Split file into sentences')

    tagged_lines = __tag_parts_of_speech(lines)
    with open('corpa/english/corpus.txt', 'w') as f:
        f.write('\n'.join(tagged_lines))

    log.info('tagged parts of speech')

    split_lines = list()
    for line in tagged_lines:
        split_line = line.split(' ')
        split_lines.append(split_line)

    english_model = Word2Vec(split_lines, size=vector_size, min_count=2)
    english_model.save_word2vec_format('corpa/english/model.w2v')

    log.info('Generated word2vec model')
    log.info('Corpus processing done at ' + str(time.time()))
    return english_model

