'''
Super main Python file to run the whole thing

Relies on gensim and python2
'''

import logging
from urllib2 import urlopen, HTTPError
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence

download = True
concatenate = False
train = False

# configure logging
logging.basicConfig(filename='all.log', level=logging.DEBUG)

def download_single_folio(quire, folio, code):
    try:
        base_url = "http://www.voynich.nu/"
        corpa_dir = "../corpa/voynich/"
        filename_base = "q{quire:02d}/f{folio:03d}{code}_tr.txt"

        filename_formatted = filename_base.format(quire=quire, folio=folio, code=code)

        logging.debug('Downloading folio from ' + base_url + filename_formatted)

        response = urlopen(base_url + filename_formatted)
        folio_text = response.read()

        target = open(corpa_dir + filename_formatted.replace('/', '_'), 'w')
        target.write(folio_text)

        logging.info('Downloaded folio ' + filename_formatted)
    except HTTPError:
        # Just log that downloading failed
        logging.error('Download failed')

def download_full_folio(quire, folio):
    quire += 1
    folio += 1

    download_single_folio(quire, folio, 'r')
    download_single_folio(quire, folio, 'v')

def download_files(): 
    pages_in_folios = [8, 8, 8, 8, 8, 8, 8, 10, 2, 2, 2, 2, 10, 2, 4, 2, 4, 2, 4, 14]
    
    cur_folio = 0
    for quire, num_folios in enumerate(pages_in_folios):
        for folio in range(num_folios):
            download_full_folio(quire, cur_folio)
            cur_folio += 1

def concatenate_files():
    '''Take all the files downloaded in the download_files step and process them

    After this funciton finishes, there should be a new file, manuscript.evt, with the full text of the Voynich
    manuscript arranged with one line of Voynich per line in the file, with only certain words and with spaces
    instead of periods
    '''

if __name__ == '__main__':
    # Download all the files
    if download:
        download_files()

    if concatenate:
        concatenate_files()

    if train:
        # Load in the voynich manuscript file and train word2vec on it
        # No need for us to re-parse the manuscript, it should already exist from the Korlin stuff

        # Load in the kinda useless sentences
        voynich_model = Word2Vec(LineSentence('../corpa/voynich/manuscript.evt'))
        logging.info('Loaded voynich model')

        english_model = Word2Vec(LineSentence('../corpa/english/raw_sentences.txt'))
        logging.info('Loaded english model')

        logging.info('Words most similar to day: ' + english_model.most_similar('day'))
        logging.info(voynich_model.most_similar('octhey'))

