"""Provides a couple functions to align two vector spaces. using a list of 
points that are known to represent the same concept
"""

def get_transformation_matrix(known_same):
    """Derives a linear transformation from one vector space to another

    The two vector spaces are represented in the known_same parameter.
    known_same should be a list of tuples where the first element in each
    tuple is the concept in one vector space and the second element in each
    tuple is the same element in the second vector space. This function uses
    stochastic gradient descent to derive the linear transformation, as in 
    Mikolov, Le, and Sutskever 2013, Exploiting Similarities among Languages
    for Machine Translation

    :param known_same: A list of tuples where the first element in each tuple
    is the vector for a concept in one vector space and the second element in
    each tuple is the same concept in a second vector space

    :return: A linear transformation matrix to transform from the first vector
    space to the second
    """

    length_of_vectors = len(known_same[0][0])
    for first, second in known_same:
        if not len(first) == length_of_vectors or not len(first) == length_of_vectors:
            raise ValueError('Vector spaces do not have the same number of dimensions')



