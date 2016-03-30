"""
Super main Python file to run the whole thing

Relies on gensim and python2
"""

import logging
import os.path
import sys
import getopt


# configure logging
logging.basicConfig(filename='all.log', level=logging.DEBUG)


def useage():
    """Prints the useage of this program
    """

    print """tvm - a utility to translate the Voynich manuscript into English

Useage: $ python -[dcgat] [params] tvm.py

This program has a number of steps, all of which can be controlled with a number of switches. If none of the switches
are given, the program performs all the steps.

    -d      Download. Downloads the Voynich Manuscript
    -c      Concatenate. Parses the manuscript files to extract the raw text, without comments.
    -g      Generate. Generates a word2Vec model for the text
    -a      Align. Generates an alignment matrix from the set of words in the alignment file
    -t      Translate. Translates all words in the Voynich Manuscript into English

Additionally, I have provided a number of parameters to specify which files to read/write data to/from.
        
        --manuscript            Specifies the file to write the concatenated Voynich Manuscript to when Concatenating,
                                    or the file to read the concatenated Voynich Manuscript from when Generating.
                                    Default is /corpa/voynich/manuscript.txt
        --voy-model-file        Specifies the file to write the Voynich word2vec model to when Generating, or the file
                                    to read the Voynich word2vec model from when Aligning. Defualt is
                                    /corpa/voynich/model.w2v
        --align-file            Specifies the name of the file to read the alignment anchor points from. Default is
                                    /en-voy-align.txt
        --ailgn-matrix          Specifies the file to write the alignment matrix to when Aligning, or the file to read
                                    the alignment file from when Translating. Default is /voy-en-matrix.txt
        --voy-en-dict           Specifies the file to write the dictionary of translates Voynich words to. Default is
                                    /voy-en-dict.txt

        -s, --vector-size       Specifies the dimensionality of the Voynich word2vec model to generate when Generating.
                                    Defulat is 100.
        -n, --num-possible      Specifies the number of potential translations to generate for each Voynich word when
                                    Translating. Default is 5.
    """


if __name__ == '__main__':
    log = logging.getLogger('main')

    # Parse arguments
    try:
        opts, argv = getopt.getopt(sys.argv[1:], 'hdcgats:n:', ['manuscript=', 'voy-model-file=', 'align-file=', 'align-matrix=', 'voy-en-dict=', 'vector-size=', 'num-possible='])

    except getopt.GetoptError, e:
        log.exception(e)
        useage()
        sys.exit(1)

    # default parameters
    download = False
    concatenate = False 
    generate = False 
    align = False
    translate = False
    do_all = True

    working_dir = '..'

    manuscript_file = working_dir + '/corpa/voynich/manuscript.txt'
    voynich_model_file = working_dir + '/corpa/voynich/model.w2v'
    align_file = working_dir + '/en-voy-align.txt'
    align_matrix_file = working_dir + '/voy-en-matrix.txt'
    voynich_to_englich_dict = working_dir + '/voy-en-dict.txt'
    vector_size = 100
    num_possible_translations = 5

    # Check what arguments we have
    for opt, val in opts:
        log.debug('Found option %s with value %s' % (opt, val))

        if opt in ['-d']:
            download = True
            do_all = False

        elif opt in ['-c']:
            concatenate = True
            do_all = False

        elif opt in ['-g']:
            generate = True
            do_all = False

        elif opt in ['-a']:
            align = True
            do_all = False

        elif opt in ['-t']:
            translate = True
            do_all = False

        elif opt in ['--manuscript']:
            manuscript_file = val

        elif opt in ['--voy-model-file']:
            voynich_model_file = val

        elif opt in ['--align-file']:
            align_file = val

        elif opt in ['--align-matrix']:
            align_matrix_file = val

        elif opt in ['--voy-en-dict']:
            voynich_to_englich_dict = val

        elif opt in ['-s', '--vector-size']:
            vector_size = int(val)

        elif opt in ['-n', '--num-possible']:
            num_possible_translations = int(val)

        else:
            useage()
            sys.exit(2)

    if do_all:
        # If the user didn't give us any options, do everything
        download = True
        concatenate = True
        generate = True
        align = True
        translate = True

    # Download all the files
    if download:
        log.info('Beginning manuscript download...')
        from download import download_files
        download_files()
        log.info('Downloaded files')

    if concatenate:
        log.info('Beginning manuscript concatenation...')
        from concatenate import concatenate_files
        concatenate_files(manuscript_file)
        log.info('Concatenated manuscript')

    if generate:
        log.info("Generating word2vec model...")
        from generate import generate_word2vec_model
        generate_word2vec_model(manuscript_file, vector_size, voynich_model_file)
        log.info('Word2Vec model generated')

    if align: 
        log.info('Generating translation matrix...')
        from transmat.train_tm import train_translation_matrix
        train_translation_matrix(voynich_model_file, working_dir + '/corpa/english/model.w2v', align_file, align_matrix_file)
        log.info('Translation matrix generated')

    if translate:
        from translate import translate_language
        translate_language(voynich_model_file, working_dir + '/corpa/english/model.w2v', align_file, voynich_to_englich_dict, num_possible_translations)
