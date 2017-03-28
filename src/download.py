"""Handles downloading the files of the Voynich manuscript
"""
import codecs
import logging
from urllib.error import HTTPError
from urllib.request import urlopen

import chardet

_log = logging.getLogger('download')


def download_single_folio(quire, folio, code, corpus_dir):
    try:
        base_url = "http://www.voynich.nu/"
        filename_base = "q{quire:02d}/f{folio:03d}{code}_tr.txt"

        filename_formatted = filename_base.format(quire=quire, folio=folio, code=code)

        _log.debug('Downloading folio from ' + base_url + filename_formatted)

        response = urlopen(base_url + filename_formatted)
        folio_text_raw = response.read()

        # Try to convert the files to UTF-8
        encoding = chardet.detect(folio_text_raw)['encoding']
        folio_text = codecs.decode(folio_text_raw, encoding=encoding)

        target = open(corpus_dir + filename_formatted.replace('/', '_'), 'w')
        target.write(folio_text)

        _log.info('Downloaded folio ' + filename_formatted)
    except HTTPError:
        # Just log that downloading failed
        _log.error('Download failed')


def download_full_folio(quire, folio, corpus_dir):
    quire += 1
    folio += 1

    download_single_folio(quire, folio, 'r', corpus_dir)
    download_single_folio(quire, folio, 'v', corpus_dir)


def download_files(corpus_dir):
    pages_in_folios = [8, 8, 8, 8, 8, 8, 8, 10, 2, 2, 2, 2, 10, 2, 4, 2, 4, 2, 4, 14]
    
    cur_folio = 0
    for quire, num_folios in enumerate(pages_in_folios):
        for folio in range(num_folios):
            download_full_folio(quire, cur_folio, corpus_dir)
            cur_folio += 1

