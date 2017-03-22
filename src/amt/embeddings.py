"""
:mod:`embeddings` -- Learn embeddings for various languages
===========================================================

.. module:: embeddings
   :platform: Linux
   :synopsis: Learns embeddings for the morphs in various languages
.. modauthor:: David Dubois <dd4942@rit.edu>
"""

import logging

import morfessor
import nltk

_logger = logging.getLogger('embeddings')

_corpus_file_tempalte = 'corpa/%s/corpus.txt'

def learn_embeddings(languages):
    pass


def _tokenize_corpus(corpus_file_location, language):
    """Tokenizes the corpus at the given location, outputting it to the tokenized corpus location

    If the corpus cannot be tokenized because nltk does not support its language then the tokenized corpus is exactly
    the same as the untokenized one

    :param corpus_file_location: The location of the corpus to tokenize
    :param language: The language of the corpus that you've tokenized
    :return: A list of lists. The inner lists are all the
    """
    lines = list()
    with open(corpus_file_location, 'r') as corpus_file:
        for line in corpus_file:
            lines.append(line)

    from nltk import word_tokenize

    all_tokens = list()
    try:
        for line in lines:
            # If the tokenizer for this language isn't available, it should have been caught when we segmented the text
            # into sentences and when we're here we shouldn't get an error, assuming nltk works like I assume it does
            all_tokens += word_tokenize(line, language=language)
    except:
        # Couldn't tokenize the text, let's just return the raw words
        _logger.warning("Could not tokenize language %s. Either install the nltk tokenizers if one is available for "
                        "this language, or ignore this message if your language doesn't have a tokenizer in nltk")
        return lines

    return all_tokens


def learn_embeddings_for_language(language):
    """Learns all the embeddings for a given language

    :param language: The name of the language to learn embeddings for. There must be a file
    `./corpa/<language>/corpus.txt` which provides the corpus to learn the language from
    :return: A tuple of (fastText model for morphs, Morfessor model for the language)
    """
    _logger.info('Learning embeddings for language %s' % language)

    corpus_file_location = _corpus_file_tempalte % language

    # Tokenize the language if we're able
    tokenized_corpus_location = corpus_file_location + '.tokens'
    tokens = _tokenize_corpus(corpus_file_location, language)
    with open(tokenized_corpus_location, 'w') as tokens_file:
        tokens_file.write(' '.join(tokens))

    # Train the Morfessor model
    io = morfessor.MorfessorIO()
    words = io.read_corpus_file(tokenized_corpus_location)  # how do I read in from memory help

    morfessor_model = morfessor.BaselineModel()
    morfessor_model.train_online(words)

    # Translate the corpus into morphs
    morphs = list()
    with open(corpus_file_location) as corpus_file:
        for line in corpus_file:
            for word in line.split():
                word_morphs = morfessor_model.viterbi_segment(word)[0]
                for morph in word_morphs:
                    morphs.append(morph)

    # Generate embeddings from