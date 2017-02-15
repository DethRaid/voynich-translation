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

    print("""tvm - a utility to translate the Voynich manuscript into English

    Useage: $ python tvm.py -[dcgat] [params]
    
    This program has a number of steps, all of which can be controlled with a number of switches. If none of the
    switches are given, the program performs all the steps.
    
        -p      Prepare. Prepares an English corpus for use as an English language model
        -d      Download. Downloads the Voynich Manuscript
        -c      Concatenate. Parses the manuscript files to extract the raw text, without comments
        -g      Generate. Generates a word2Vec model for the text
        -a      Align. Generates an alignment matrix from the set of words in the alignment file
        -t      Translate. Translates all morphemes in the source text into English
        -o      Output. Read in all the files matching a certain pattern and replace their words with the words in the
                generated translation file
    
    Additionally, I have provided a number of parameters to specify which files to read/write data to/from.
        
        --en-text               Specifies the file to read the English corpus from when Preparing
        --corpus-type           Specifies if the English corpus is from Wikipedia or should be treated as Markdown when
                                    Preparing. Valid values are 'none', wiki' or 'md'. Default value is 'wiki'
        --manuscript            Specifies the file to write the concatenated Voynich Manuscript to when Concatenating,
                                    or the file to read the concatenated Voynich Manuscript from when Generating.
                                    Default is /corpa/voynichese/corpus.txt
        --voy-model-file        Specifies the file to write the Voynich word2vec model to when Generating, or the file
                                    to read the Voynich word2vec model from when Aligning. Defualt is
                                    /corpa/voynichese/model.w2v
        --align-file            Specifies the name of the file to read the alignment anchor points from. Default is
                                    /en-voy-align.txt
        --align-matrix          Specifies the file to write the alignment matrix to when Aligning, or the file to read
                                    the alignment file from when Translating. Default is /voy-en-matrix.txt
        --voy-en-dict           Specifies the file to write the dictionary of translates Voynich words to. Default is
                                    /voy-en-dict.txt
        --source-file           Specifies the file to translate. Default is /corpa/voynichese/corpus.txt
                                    manuscript website
        --output-file           Specifies the file to output the translated file to when Outputting. Default is
                                    /output/manuscript_en.txt

        -s, --vector-size       Specifies the dimensionality of the word2vec models to generate when Generating.
                                    Default is 100.
        -n, --num-possible      Specifies the number of potential translations to generate for each word when
                                    Translating. Default is 5.
    """)


if __name__ == '__main__':
    log = logging.getLogger('main')

    # Parse arguments
    try:
        opts, argv = getopt.getopt(sys.argv[1:], 'hpdcgatos:n:', ['en-text=', 'corpus-type=', 'manuscript=', 'voy-model-file=', 'align-file=', 'align-matrix=', 'voy-en-dict=', 'vector-size=', 'num-possible=', 'source-file=', 'output_file='])

    except getopt.GetoptError as e:
        log.exception(e)
        useage()
        sys.exit(1)

    # default parameters
    prepare = False
    download = False
    concatenate = False 
    generate = False 
    align = False
    translate = False
    output = False
    do_all = True

    working_dir = ''    # MUST end in a /

    english_corpus = ''
    english_corpus_type = 'none'
    manuscript_file = working_dir + 'corpa/voynichese/corpus.txt'
    voynich_model_file = working_dir + 'corpa/voynichese/model.w2v'
    align_file = working_dir + 'en-voy-align.txt'
    align_matrix_file = working_dir + 'voy-en-matrix.txt'
    voynich_to_englich_dict = working_dir + 'voy-en-dict.txt'
    source_file = working_dir + 'corpa/voynichese/corpus.txt'
    output_file = working_dir + 'output/manuscript_en.txt'
    vector_size = 100
    num_possible_translations = 5

    # Check what arguments we have
    for opt, val in opts:
        log.debug('Found option %s with value %s' % (opt, val))

        if opt in ['-p']:
            prepare = True
            do_all = False

        elif opt in ['-d']:
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

        elif opt in ['-o']:
            output = True
            do_all = False

        elif opt in ['--en-text']:
            english_corpus = working_dir + val

        elif opt in ['--corpus-type']:
            english_corpus_type = working_dir + val

        elif opt in ['--manuscript']:
            manuscript_file = working_dir + val

        elif opt in ['--voy-model-file']:
            voynich_model_file = working_dir + val

        elif opt in ['--align-file']:
            align_file = working_dir + val

        elif opt in ['--align-matrix']:
            align_matrix_file = working_dir + val

        elif opt in ['--voy-en-dict']:
            voynich_to_englich_dict = working_dir + val

        elif opt in ['--source-file']:
            source_file = working_dir + val

        elif opt in ['--output-file']:
            output_file = working_dir + val

        elif opt in ['-s', '--vector-size']:
            vector_size = int(val)

        elif opt in ['-n', '--num-possible']:
            num_possible_translations = int(val)

        else:
            useage()
            sys.exit(2)

    if do_all:
        # If the user didn't give us any options, do everything
        prepare = True
        download = True
        concatenate = True
        generate = True
        align = True
        translate = True
        output = True

    if prepare:
        log.info('Preparing English corpus...')
        from prepare import prepare_english_corpus
        prepare_english_corpus(working_dir + english_corpus, english_corpus_type, vector_size)
        log.info('Prepared corpus')
    
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
        translate_language(voynich_model_file, working_dir + '/corpa/english/model.w2v', align_matrix_file, voynich_to_englich_dict, num_possible_translations)

    if output:
        from output import output_files
        output_files(voynich_to_englich_dict, source_file, output_file)
