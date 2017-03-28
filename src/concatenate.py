"""Concatenates all the Voynich transcription files into a single pretty file

The files has spaces between words, rather than periods. It also has all the
comments and metadata removed, so there's only the actual words

I'm unsure what to do about sentances or whatever. There's no clear sentance
boundaries in the transcription. I'l start out with lines being lines, and
maybe try folios being lines or maybe make the whole thing a line. Not sure,
I'll see what gives the prettiest results I guess.
"""

import logging
import re
import sys
from os import listdir
from collections import defaultdict

_log = logging.getLogger('concatenate')


def process_line(line):
    """Processes a single line to remove all comments and line breaks and everything

    :param line: A single line of text from an EVA file
    :return: The line of text as an array of words
    """ 
    start_chars = ['<']
    end_chars = ['>']
    write_character = True

    final_string = ''

    # Do one pass through the line to remove comments and null characters
    # Do another pass to break the line into words

    for char in line: 

        if char in start_chars: 
            write_character = False

        if write_character:
            final_string += char

        if char in end_chars:
            write_character = True

    return final_string


def process_line_group(cur_line_group):
    # Examine the lines in parallel. For each positino in the line, look for the most common character amoung the 
    # various transcriptions. If there's a tie, randomly chose one of the characters
    # If an unknown letter persists in the final line, we can try to figure out what the word is based on in some
    # downstream step

    # Remove any lines with a length of 0
    line_group = [line.strip() for line in cur_line_group if len(line) > 0]
    if len(line_group) == 0:
        return ''

    final_line = ""

    # print 'Processing lines'
    # for line in line_group:
    #     print line + ' with length ' + str(len(line))

    # assume that all the lines are the same length. Pretty sure this is true
    for index in range(0, len(line_group[0])):
        characters = defaultdict(int) 
        for line in line_group:
            characters[line[index]] += 1

        common_char = next(iter(characters))[0]
        for key, value in characters.items():
            if value > characters[common_char]:
                common_char = key

        final_line += str(common_char)

    return final_line


def remove_fancy_chars(string):
    """Removes characters surrounded by {} from the manuscript by assuming that the characters are just regular
    Voynichese characters that have some embellishment
    
    Is this hypothesis wrong? Maybe. Maybe not.
    
    :param string: The string to remove fancy characters from
    :return: The input string, but with the fancy characters replaced by somewhat regular characters
    """

    string = re.sub("\{&o'\}", 'o', string)
    string = re.sub("\{&252\}", '', string)
    string = re.sub("\{&c'\}", 'c', string)
    string = re.sub("\{&253\}", '', string)

    return string


def remove_text_objects(string):
    """Removes Voynichese text object, such as {plant}, from the text, replacing them with spaces
    
    It's possible that the text didn't flow horizontally across the object, but instead the object separated columns.
    I sure hope that isn't the case, because my data doesn't think that's the case
    
    :param string: The data to operate on
    :return: The input data, with {plant} and {gap} replaced with spaces
    """

    string = re.sub('\{plant\}', ' ', string)
    string = re.sub('\{gap\}', ' ', string)

    # I am reasonably certain that these patterns indicate a column break. However, processing that is hard and I don't
    # feel like writing it right now so I won't. Replacing them with spaces will be mostly good for what I want, I think
    string = re.sub('\{\\\}', ' ', string)
    string = re.sub('\{||\}', ' ', string)

    return string


def process_file(file_path):
    """Opens a single file and processes it

    The processing can happen a few different ways: There's a simple line
    processor which just gets the first line that's completely certain, and a
    voting processor which gets the most common and most certain transcription
    of each word

    :param file_path: The path to the file to process
    :return: A single string representing the whole processed file
    """
    processed_file = ''
    skipped_first = False

    with open(file_path) as f:
        _log.info('Beginning %s' % file_path)

        content = f.readlines()
        cur_line_group = list()
        cur_line = ''
        for line in content:
            if not skipped_first:
                skipped_first = True
                continue

            if line[0] == '#':
                # We have a comment, take the last few lines and process them together
                cur_line_san = process_line(cur_line)
                cur_line_group.append(cur_line_san)
                _log.debug('Found a comment, processing group %s' % cur_line_group)
                processed_line = process_line_group(cur_line_group) 
                processed_file += processed_line
                cur_line_group = list()
                cur_line = ''
            else:
                if line[0] == '<': 
                    # If the line starts with a <. we should cut off the last line
                    cur_line_san = process_line(cur_line) 
                    _log.debug('Found a new line, adding "%s" to the current line group' % cur_line_san)

                    cur_line_group.append(cur_line_san)
                    cur_line = ''
                    cur_line += line
                    _log.debug('Appended "%s" to the new current line' % line)
                else:
                    # There's no '-' or '=' at the end of the line, so it's an incomplete line and we
                    # can append it to the current line accumulator
                    cur_line += line 

        # We've done all the lines, but we still need to process the last line
        cur_line_san = process_line(cur_line)
        cur_line_group.append(cur_line_san)
        _log.debug('appended %s' % cur_line_san)
        processed_file += process_line_group(cur_line_group)

    # Splits the stirng on spaces, then joins with a space. Should remove duplicate spaces
    line_with_spaces = re.sub('[\.\-]', ' ', processed_file) 
    line_with_spaces = re.sub('=', '\n', line_with_spaces)

    # Now we just need to resolve unknown letters
    # The code for that will be hard, so let's first just print out the number of unknown letters to see if we need to 
    # do anything about it

    line_with_spaces = remove_fancy_chars(line_with_spaces)
    line_with_spaces = remove_text_objects(line_with_spaces)

    return line_with_spaces


def concatenate_files(manuscript_file_name, manuscript_directory):
    """Take all the files downloaded in the download_files step and process them

    After this function finishes, there should be a new file, corpus.txt,
    with the full text of the Voynich manuscript arranged with one line of
    Voynich per line in the file, with only certain words and with spaces
    instead of periods

    :param manuscript_file_name: The name of the file to write the manuscript to
    :param manuscript_directory: the directory where all the files from the manuscript are
    """
    # Go through each file in the folder
    # Look at each group of lines
    # Return a list of good words
    # Concatenate the lines using the line concatenator
    files = [f for f in listdir(manuscript_directory)]

    # The full string of the manuscript
    manuscript_string = ''

    folio_num = 1
    increment = False
    for file_path in sorted(files):
        if not file_path[-3:] == 'txt':
            _log.info('Skipping non-text file %s' % file_path)
            continue
        if file_path == 'corpus.txt':
            continue
        try:
            manuscript_string += process_file(manuscript_directory + file_path) + '\n'
        except Exception as e:
            _log.error('Failed to process file %s' % file_path)
            _log.exception(e)

    # Get rid of the stupid = signs
    manuscript_string = manuscript_string.replace('=', ' ')

    with open(manuscript_file_name, 'w') as f:
        f.write(manuscript_string)


def print_help():
    print("""This script concatenates all the txt files for the Voynich Manuscript into
    a single model, trying to resolve as many unknown characters as possible

Try calling it with no arguments to see it work!""")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print_help()
        sys.exit()

    concatenate_files('corpus.txt', 'corpa/voynichese')
    _log.info('Input files concatenated')
