"""Handles downloading the files of the Voynich manuscript
"""

import logging
from urllib2 import urlopen, HTTPError

log = logging.getLogger('download')


def download_single_folio(quire, folio, code):
    try:
        base_url = "http://www.voynich.nu/"
        corpa_dir = "../corpa/voynich/"
        filename_base = "q{quire:02d}/f{folio:03d}{code}_tr.txt"

        filename_formatted = filename_base.format(quire=quire, folio=folio, code=code)

        log.debug('Downloading folio from ' + base_url + filename_formatted)

        response = urlopen(base_url + filename_formatted)
        folio_text = response.read()

        target = open(corpa_dir + filename_formatted.replace('/', '_'), 'w')
        target.write(folio_text)

        log.info('Downloaded folio ' + filename_formatted)
    except HTTPError:
        # Just log that downloading failed
        log.error('Download failed')


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

