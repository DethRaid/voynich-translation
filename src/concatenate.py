"""Concatenates all the Voynich transcription files into a single pretty file

The files has spaces between words, rather than periods. It also has all the
comments and metadata removed, so there's only the actual words

I'm unsure what to do about sentances or whatever. There's no clear sentance
boundaries in the transcription. I'l start out with lines being lines, and
maybe try folios being lines or maybe make the whole thing a line. Not sure,
I'll see what gives the prettiest results I guess.
"""

import logging
from os import listdir

logging.basicConfig(filename='all.log', level=logging.DEBUG)


def process_line(line):
    """Processes a single line to remove all comments and line breaks and everything

    :param line: A single line of text from an EVA file
    :return: The line of text as an array of words
    """
    chars_to_ignore = ['!', '-', '=', ' ']
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
        elif char == '-': 
            # Replace dashes with a period so we can split words where things infringe on the line
            final_string += '.'
        elif char == '=':
            # Emit a newline so the corpus gets split into paragraphs, and a peroid so my hacky 
            # tokenizer won't break
            final_string += '.=.'

        if char in end_chars:
            write_character = True

    # We've done through the line and removed gross characters
    # Replace all dots with spaces
    return final_string.replace('.', ' ').strip()


def process_line_group(cur_line_group):
    # look at each line in the group. If the line has a *, it's uncertain. Return the first certain 
    # line

    for line in cur_line_group:
        if '*' not in line:
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
        content = f.readlines()
        cur_line_group = list()
        cur_line = ''
        for line in content:
            if line[0] == '#':
                # We have a comment, take the last few lines and process them together
                processed_line = process_line_group(cur_line_group) 
                processed_file += processed_line
                cur_line_group = list()
            else:
                if line[-2] in ['-', '=']:
                    # If the line ends with a - or =, it's the end of the current line of text 
                    cur_line += line
                    cur_line_group.append(process_line(cur_line))
                    cur_line = ''
                else:
                    # There's no '-' or '=' at the end of the line, so it's an incomplete line and we
                    # can append it to the current line accumulator
                    cur_line += line
                

    # Splits the stirng on spaces, then joins with a space. Should remove duplicate spaces
    return '\n'.join(processed_file.split('='))

def concatenate_files():
    """Take all the files downloaded in the download_files step and process them

    After this funciton finishes, there should be a new file, manuscript.evt,
    with the full text of the Voynich manuscript arranged with one line of
    Voynich per line in the file, with only certain words and with spaces
    instead of periods
    """
    # Go through each file in the folder
    # Look at each group of lines
    # Return a list of good words
    # Concatenate the lines using the line concatenator
    files = [f for f in listdir('../../../corpa/voynich')]

    # The full string of the manuscript
    manuscript_string = ''

    folio_num = 1
    increment = False
    for file_path in files:
        # manuscript_string += file_path
        try:
            manuscript_string += process_file('../../../corpa/voynich/' + file_path) + '\n'
        except:
            print 'Failed to open file', file_path

    # Get rid of the stupid = signs
    manuscript_string = manuscript_string.replace('=', ' ')

    with open('../../../corpa/voynich/manuscript.evt', 'w') as f:
        f.write(manuscript_string)
