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
from os import listdir

log = logging.getLogger('concatenate')


def process_line(line):
    """Processes a single line to remove all comments and line breaks and everything

    :param line: A single line of text from an EVA file
    :return: The line of text as an array of words
    """
    chars_to_ignore = ['!', '-', ' ', ',']
    start_chars = ['{', '<']
    end_chars = ['}', '>']
    write_character = True

    final_string = ''

    # Do one pass through the line to remove comments and null characters
    # Do another pass to break the line into words

    for char in line: 

        if char in start_chars: 
            write_character = False

        if write_character and char not in chars_to_ignore: 
            final_string += char

        if char in end_chars:
            write_character = True

    # We've done through the line and removed gross characters
    # Replace all dots with spaces
    return final_string.replace('.', ' ').strip()


def process_line_group(cur_line_group):
    # look at each line in the group. If the line has a *, it's uncertain. Return the first certain 
    # line

    for line in cur_line_group:
        if '*' not in line and len(line) > 0:
            return line + '\n'

    return ''


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
    with open(file_path) as f:
        log.debug('Beginning %s' % file_path)

        content = f.readlines()
        cur_line_group = list()
        cur_line = ''
        for line in content:
            if line[0] == '#':
                # We have a comment, take the last few lines and process them together
                cur_line_san = process_line(re.sub('[\s+]', ' ', cur_line))
                cur_line_group.append(cur_line_san)
                log.debug('Found a comment, processing group %s' % cur_line_group)
                processed_line = process_line_group(cur_line_group) 
                processed_file += processed_line
                cur_line_group = list()
                cur_line = ''
            else:
                if line[0] == '<': 
                    # If the line starts with a <. we should cut off the last line
                    cur_line_san = process_line(re.sub('[\s+]', ' ', cur_line)) 
                    log.debug('Found a new line, adding "%s" to the current line group' % cur_line_san)

                    cur_line_group.append(cur_line_san)
                    cur_line = ''
                    cur_line += line
                    log.debug('Appended "%s" to the new current line' % line)
                else:
                    # There's no '-' or '=' at the end of the line, so it's an incomplete line and we
                    # can append it to the current line accumulator
                    cur_line += line 

        # We've done all the lines, but we still need to process the last line
        cur_line_san = process_line(re.sub('[\s+]', ' ', cur_line))
        cur_line_group.append(cur_line_san)
        log.debug('appended %s' % cur_line_san)
        processed_file += process_line_group(cur_line_group)

    # Splits the stirng on spaces, then joins with a space. Should remove duplicate spaces
    return '\n'.join(processed_file.split('='))


def concatenate_files(manuscript_file_name):
    """Take all the files downloaded in the download_files step and process them

    After this funciton finishes, there should be a new file, manuscript.evt,
    with the full text of the Voynich manuscript arranged with one line of
    Voynich per line in the file, with only certain words and with spaces
    instead of periods

    :param manuscript_file_name: The name of the file to write the manuscript to
    """
    # Go through each file in the folder
    # Look at each group of lines
    # Return a list of good words
    # Concatenate the lines using the line concatenator
    files = [f for f in listdir('../corpa/voynich')]

    # The full string of the manuscript
    manuscript_string = ''

    folio_num = 1
    increment = False
    for file_path in files:
        if not file_path[-3:] == 'txt':
            log.info('Skipping non-text file %s' % file_path)
            continue
        try:
            manuscript_string += process_file('../corpa/voynich/' + file_path) + '\n'
        except Exception, e:
            log.error('Failed to open file &s' % file_path)
            log.exception(e)

    # Get rid of the stupid = signs
    manuscript_string = manuscript_string.replace('=', ' ')

    with open(manuscript_file_name, 'w') as f:
        f.write(manuscript_string)
