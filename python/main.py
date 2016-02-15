'''
Super main Python file to run the whole thing
'''

from gensim.models import Word2Vec
from nltk.corpus.reader.aligned import AlignedCorpusReader

if __name__ == '__main__':
    # Load in the voynich manuscript file and train word2vec on it
    # No need for us to re-parse the manuscript, it should already exist from the Korlin stuff

    manuscript = AlignedCorpusReader('../corpa/voynich', 'manusctips.evt')
    model = Word2Vec(manuscript.sents())

    print(model.most_similar('octhey'))

