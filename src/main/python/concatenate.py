'''Concatenates all the Voynich transcription files into a single pretty file

The files has spaces between words, rather than periods. It also has all the 
comments and metadata removed, so there's only the actual words

I'm unsure what to do about sentances or whatever. There's no clear sentance
boundaries in the transcription. I'l start out with lines being lines, and
maybe try folios being lines or maybe make the whole thing a line. Not sure,
I'll see what gives the prettiest results I guess.
'''

import logging
from os import listdir
from os.path import isfile, join

logging.basicConfig(filename='all.log', level=logging.DEBUG)


def process_line(line):
    """Processes a single line to remove all comments and line breaks and everything

    :param line: A single line of text from an EVA file
    :return: The line of text as an array of words
    """
    for char in line:
        if char == '<':
            # We're entering either a line description or a comment thing at the end


def process_file(file_path):
    """Opens a single file and processes it

    The processing can happen a few different ways: There's a simple line
    processor which just gets the first line that's completely certain, and a
    voting processor which gets the most common and most certain transcription
    of each word

    :param file_path: The path to the file to process
    :return: A single string representing the whole processed file
    """
    with open(file_path) as f:
        content = f.readlines()
        for line in content:
            line_san = process_line(line)


def concatenate_files():
    '''Take all the files downloaded in the download_files step and process them

    After this funciton finishes, there should be a new file, manuscript.evt,
    with the full text of the Voynich manuscript arranged with one line of
    Voynich per line in the file, with only certain words and with spaces
    instead of periods
    '''
    # Go through each file in the folder
    # Look at each group of lines
    # Return a list of good words
    # Concatenate the lines using the line concatenator
    files = [f for f in listdir('../../../corpa/voynich')]

    # The full string of the manuscript
    manuscript_string = ''

    for file_path in files:
        manuscript_string += process_file(file_path)

