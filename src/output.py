"""Allows one to translate a bunch of texts from a given folder, slapping them down in a specified output folder
"""

import os
import re
import logging


log = logging.getLogger('output')


def __get_top_translation(line):
    """Parses the line in order to find the word that the line provides the top translations for and returns the word
    and its top translation

    Note that this algorithm assumes that the potential translations are sorted. If the potential translations are not
    sorted, you're going to have a bad time

    :param line: A line, read from the dictionary file
    :return: The word that the line provides a translation for and the most likely translation for that word
    """
    word = ''
    top_translation = ''
    accumulator = ''
    should_read = True

    for char in line:
        if char == ':':
            # We have already read in the whole word to translate
            word = accumulator
            accumulator = ''
            should_read = False 
        elif char == "'":
            should_read = not should_read 
            if not should_read:
                top_translation = accumulator
                return word, top_translation
        elif should_read:
            accumulator += char


def __read_translation_dict(dict_file):
    """Reads in a translation dictionary from the dict file, outputting it as a map from source word to target word

    :param dict_file: The name of the file to read the dictionary from
    :return: A dictionary from source word to most likely target word
    """

    translation_dictionary = dict()

    with open(dict_file) as f:
        for line in f:
            word, top_translation = __get_top_translation(line)
            translation_dictionary[word] = top_translation

    return translation_dictionary


def __translate(source_file, translation_dictionary):
    """Translates the given file using the given translation dictionary

    :param source_file: The file (NOT filename) to translate
    :param translation_dictionary: A dict from source language word to target language word, to be used in translating
    the given file
    :return: An array of lines from the source file, where each line has been translated using the translation dictionary
    """

    all_lines = list()

    for line in source_file:
        words = line.split()
        out_line = list()

        for word in words:
            if word in translation_dictionary:
                log.debug('Translating word %s as %s' % (word, translation_dictionary[word]))
                out_line.append(translation_dictionary[word])
            else:
                log.warn('Could not translate word %s' % word)
                out_line.append(word)   # Preserve non-translatable words

        all_lines.append(' '.join(out_line))

    return all_lines


def output_files(dict_file, source_file_name, output_file):
    """Translates the source file into the target language using the dict_file, outputting the translated files to the
    output folder.
    
    It's worth noting that this only uses the most likely translation. It makes no attempts to find a translation
    that fits the target language, just one that's a likely translation of the given word. Crude, I know, but
    effective at removing human bias.
    
    :param dict_file_name: The name of the file that holds the dictionary from the source language to English
    :param source_file_name: The name of the file to translate
    :param file_pattern: A regex that all files must match if they wish to be translated
    :param output_file: The file to write the translated text to
    """

    translation_dictionary = __read_translation_dict(dict_file)

    log.info('Opening file %s for translation % source_file_name')
    with open(source_file_name) as f:
        translated_file = __translate(f, translation_dictionary)

    log.info('Translation complete')
 
    with open(output_file, 'w') as out_file:
        out_file.write('\n'.join(translated_file))
    
    log.info('Wrote translation to %s' % output_file)

