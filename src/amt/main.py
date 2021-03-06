"""
:mod:`AMT` -- Entry point for the Automatic Machine Translation program
=======================================================================

.. module:: AMT
   :platform: Linux
   :synopsis: Translate between languages with no prior information about the language
.. modauthor:: David Dubois <dd4942@rit.edu>

Automatic Machine Translation performs a number of steps:

1. **Train word embeddings:** The first step is to train word vector models for all of the languages that this
system will use. However, before word embeddings are learned, the words are segmented into morphs with `Morfessor
<http://www.cis.hut.fi/projects/morpho/>`. These morphs are the units that the vectors are learned on, so perhaps it
would be more accurate to call the vectors 'morph vectors'. The morph vectors are learned with the
`fastText <https://github.com/facebookresearch/fastText>` algorithm.
2. **Align languages:** After morph vectors are learned, the vector spaces must be aligned with each other. Automatic
Machine Translation uses a modified version of the `Joint Registration of Multiple Point Sets
<https://team.inria.fr/perception/research/jrmpc/>` algorithm (modified to allow vector spaces with more than three
dimensions) in order to achieve this.
3. **Learn Phrases:** Automatic Machine Translation is a phrase-based translation system. Thus, it needs to learn
phrases. Learning phrases takes much inspiration from Alexandre Klementiev, Ann Irvine, Chris Callison-Burch, and David
Yarowsky (2012), along with those who have followed in their footsteps. Since translating into analytic languages is
easier, the system uses the language with the fewest morphs per word as an internal interlingua. Thus, each language
that the AMT system recognizes needs to be translated to/from a single language, rather than every other langauge,
greatly reducing the number of languages pairs used
"""

import logging
import sys

import matlab.engine

from src.amt.embeddings import LanguageModel

logging.basicConfig(filename='all.log', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

_log = logging.getLogger('main')

if __name__ == '__main__':
    languages = ['voynichese', 'english']
    dimensions = 100
    models = []
    for language in languages:
        models.append(LanguageModel(language, dim=dimensions))

    matlab_engine = matlab.engine.start_matlab()

    results = matlab_engine.jrmpc([model.get_all_word_embeddings() for model in models], [0 for x in range(dimensions)])
