import logging
import operator

import numpy as np


logger = logging.getLogger('space')


class __Node(object):
    """Represents a single node in a tree of word embeddings. Provides a method or two to acquire the embedding that's
    closest to a given embedding
    """

    def __init__(self, pos, children):
        """Simply saves the children internally

        :param pos: The position in the word embedding space where this __Node resides. This is used primarily when
        trying to get the closest word to a diven word, as I can look at the positions of different nodes to try and get
        the node that's closest to the given embedding
        :param children: A list __Node objects. The length of this list is not specified to allow for applications to
        use however many children per node that they want. If this value is None, then this __Node is assumed to be a
        leaf node
        """
        self.children = children

    def get_closest_word(self, word):
        """Finds the word in the tree that's closest to the given word

        :param word: The word embedding to get the closest word to
        :return: A tuple where the first element is the index of the word in the space that created this __Node, and the
        second element is the actual embedding
        """

        # First we'll loop through all the children of this node, returning the one that's the closest to this node.
        # Then, we'll call get_closest_word on that node and recursively traverse everything
        # The cycle will be broken when we get down to the __LeafNode objects, which hold the actual values. That class
        # overrides this method to return only its data

        small_dist = 1000
        small_idx = 0
        idx = 0
        for node in self.children:
            dist = np.dot(node.pos, self.pos)
            if dist < small_dist:
                small_dist = dist
                small_idx = idx
            idx += 1

        return self.children[small_idx].get_closest_word(word)


class __LeafNode(__Node):
    """This is a leaf node in my beautiful, wonderful tree
    """

    def __init__(self, data):
        """Simply saves the data

        :param data: The data for this tree to hold
        """
        self.data = data

    def get_closest_word(self, word):
        """Simply returns this thing's data, since that's all it has and there isn't any point in trying to compare
        anything to it. Not even gonna document that parameter here, it's so unused
        """

        return self.data


class Space(object):

    def __init__(self, matrix_, id2row_):
        self.mat = matrix_
        self.id2row = id2row_
        self.create_row2id()

        # Create the initial list. Don't worry, we'll build it up into a tree in a bit
        self.tree = list()
        for _, word in enumeraet(self.id2row):
            self.tree += __LeafNode(word)

        while len(self.tree) > 1:
            self.tree = create_node_layer(self.tree)

    def create_row2id(self):
        self.row2id = {}
        for idx, word in enumerate(self.id2row):
            if word in self.row2id:
                raise ValueError("Found duplicate word: %s" % (word))
            self.row2id[word] = idx

    def create_node_layer(self, nodes):
        """Builds a layer of nodes in the accelleration tree

        :param nodes: The nodes to build up into a higher-order layer
        :param num_children: The number of children that each node should have
        :return: The next layer in the tree
        """
        new_nodes = list()
        already_visited_nodes = list() 
        
        for idx1 in range(0, len(nodes)):
            if nodes[idx1] in already_visited_nodes:
                continue

            cur_children = [nodes[idx1]]
            closest_len = 1000
            closest_idx = idx1

            # look for the word that's closest to our target word
            for idx2 in range(idx1, len(nodes)):
                if leaf_nodes[idx2] in already_visited_nodes:
                    continue

                cur_len = np.dot(cur_children[0], nodes[idx2])
                if cur_len < closest_len:
                    closest_len = cur_len
                    closest_idx = idx2
            
            cur_children.append(nodes[closest_idx])
            node_pos = cur_children[0] + cur_children[1]
            node_pos /= 2
            new_nodes.append(__Node(node_pos, cur_children))

            already_visited_nodes += cur_children

        return new_nodes

    @classmethod
    def build(cls, fname, lexicon=None, total_count=1000000000, only_lower=False):

        #if lexicon is provided, only data occurring in the lexicon is loaded
        id2row = []
        def filter_lines(f):
            count = 0
            for i,line in enumerate(f):
                word = line.split()[0]
                if i != 0 and (lexicon is None or word in lexicon) and len(line.split()) > 2:
                    if only_lower and not word[0].islower():
                        continue
                    if count > total_count:
                        return

                    if 'None' in word or '_' in word or word[0].isupper():
                        # This causes my code to fail. Something about numpy interpreting the string "None" in a word as
                        # the value None, not the string None. Yay!
                        # Jon Nones, why'd you have to write things?
                        # Excludes multi-word proper nouns (most proper nouns) because they use RAM and proper nouns
                        # aren't useful for translation
                        # Also does the thing of removing words that start with an uppercase letter
                        # This includes proper nouns AND words at the beginning of sentences. Whoops. However, the program runs now, so all well
                        continue

                    line_len = len(line.split())
                    if line_len != ncols:
                        logger.error('Line \n%s\n has %d columns when it should have %d' % (line, line_len, ncols))

                    # if count > 193000:
                    #    logger.info(line)

                    count += 1
                    id2row.append(word)
                    if count % 7000 == 0:
                        logger.info('Read in %d words' % count)

                    yield line

        #get the number of columns
        with open(fname) as f:
            f.readline()
            ncols = len(f.readline().split())

        logger.debug('Working with %d columns' % ncols)

        with open(fname) as f:
            m = np.matrix(np.loadtxt(filter_lines(f), comments=None, usecols=range(1,ncols)))

        return Space(m, id2row)

    def normalize(self):
        row_norms = np.sqrt(np.multiply(self.mat, self.mat).sum(1))
        row_norms = row_norms.astype(np.double)
        row_norms[row_norms != 0] = np.array(1.0/row_norms[row_norms != 0]).flatten()
        self.mat = np.multiply(self.mat, row_norms)

    def get_closest_words(self, word, num):
        """Gets the closest num words to the given word

        Implements a simple linear search through the target space, calculating the cosing distance between the target
        word and all the words in this space. Then, sorts all the distances and returns the top num distances

        :param word: The embedding of the word to get the closest words to
        :param num: The number of words to return

        :return: A list of tuples, where the first element in each tuple is the word and the second element is the
        cosine distance from that word to the source word
        """

        word_matrix = word.transpose()

        similarities = dict()
        for idx, embedding in enumerate(self.mat):
            similarities[idx] = np.dot(embedding, word_matrix)

        sorted_words = sorted(similarities.items(), key=operator.itemgetter(1))

        top_words = sorted_words[-num:]

        return map(lambda x: (self.id2row[x[0]], x[1]), top_words)

