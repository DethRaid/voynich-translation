'''Concatenates all the Voynich transcription files into a single pretty file

The files has spaces between words, rather than periods. It also has all the 
comments and metadata removed, so there's only the actual words

I'm unsure what to do about sentances or whatever. There's no clear sentance
boundaries in the transcription. I'l start out with lines being lines, and
maybe try folios being lines or maybe make the whole thing a line. Not sure,
I'll see what gives the prettiest results I guess.
'''

import logging

logging.basicConfig(filename='all.log', level=logging.DEBUG)

def concatenate_files():
    '''Take all the files downloaded in the download_files step and process them

    After this funciton finishes, there should be a new file, manuscript.evt,
    with the full text of the Voynich manuscript arranged with one line of
    Voynich per line in the file, with only certain words and with spaces
    instead of periods
    '''P
