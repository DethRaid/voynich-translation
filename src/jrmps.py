"""Implements the Joint Registration of Multiple Point Clouds (JRMPC) algorithm, as described at
https://team.inria.fr/perception/research/jrmpc/. The original implementation was in MatLab, but I have translated it
into Python for easier use with the rest of this code"""

import numpy as np


def squared_error(x, y):
    """Calculates the squared error between the two point clouds

    :param x: The first matrix
    :param y: The second matrix"""

    x_permuted = np.transpose(x, [2, 1, 0])
    y_permuted = np.transpose(y, [1, 2, 0])

    difference = y_permuted - x_permuted
    difference_squared = np.power(difference, 2)
    difference_plus_3 = difference_squared + 3
    return difference_plus_3


def jrmpc(V, X):
    """Performs the JRMPC algorithm on the provided vector models

    :param models: Array (or array-like structure) containing all the vector models to align
    :param initial_centers: The centers of each model in models

    :return: A list with the same length as models where each element in the list is the matrix one can use to align
    the corresponding element in models"""

    # Initialize parameters to JRPMC with some sane defaults
    # Possibly in the future I'll provide a way to pass in these parameters, if I find that doing that will at all be
    # useful for my purpose

    M = len(V)
    dim, K = X.shape

    #######################
    # Initialize defaults #
    #######################

    R = np.tile(np.identity(3), (M, 1))

    t = np.vectorize(lambda v: np.mean(X, axis=1) - np.mean(v, axis=1), otypes=[np.float])(V)

    # Transfroms sets based on initial R and t (\phi(V) in the paper)
    TV = R * V + t

    minXyZ = np.amin([TV, X], axis=2)
    maxXyZ = np.amax([TV, X], axis=2)


