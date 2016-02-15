'''
Super main Python file to run the whole thing
'''

from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
from nltk.corpus.reader.aligned import AlignedCorpusReader

if __name__ == '__main__':
    # Load in the voynich manuscript file and train word2vec on it
    # No need for us to re-parse the manuscript, it should already exist from the Korlin stuff

    # Load in the kinda useless sentences
    voynich_model = Word2Vec(LineSentence('../corpa/voynich/manuscript.evt'))
    print 'Loaded voynich model'
    #english_model = Word2Vec(LineSentence('../corpa/english/raw_sentences.txt'))
    #print 'Loaded english model'

    #print 'Words most similar to day:', english_model.most_similar('day')
    print(voynich_model.most_similar('octhey'))

