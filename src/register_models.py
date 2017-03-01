"""Registers the language models with each other"""

import matlab.engine


def run_registration(language_models):
    """Registers the provided language models with each other

    The models should be Gensim word2vec models

    :param language_models: A list of the language models to align
    :return: A list of matrices where each matrix transforms the corresponding language model into the aligned space
    """

    eng = matlab.engine.start_matlab()
    matrices = eng.jrmpc(language_models, [], nargout=1)


if __name__ == '__main__':
    run_registration([])