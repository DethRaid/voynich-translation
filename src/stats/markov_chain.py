from collections import defaultdict

from math import log

import logging

import json


def calc_entropy(iter, base_path, type):
    """Creates a Markov chain thing

    :param iter: The iterator to build the markov chain from
    :param base_path: The path to output all things to
    :param type: The type of data that we're examining
    """
    logger = logging.getLogger('entropy')

    # all_predictions is a map from context to predictions. Context is a list of the items in the current context, and
    # the predictions is a list of all the items that follow the context, along with some additional information
    # about each item such as the number of times it was encountered and its probability
    # The prediction format is (item, count, probability)
    all_predictions = defaultdict(list)

    # A count of how many items follow each context
    counts = defaultdict(int)

    last_item = None

    # first pass: collect all the things that follow a context item
    for item in iter:
        predictions = all_predictions[last_item]

        pred = find(lambda n: n[0] == item, predictions)
        if pred is None:
            all_predictions[last_item].append([item, 1, 0])
        else:
            pred[1] += 1

        counts[last_item] += 1

        last_item = item

    # second pass: calculate the probabilities of all those predictions
    for context, predictions in all_predictions.items():
        for prediction in predictions:
            prediction[2] = prediction[1] / counts[context]

    with open(base_path + type + ' predictions.json', 'w') as outfile:
        json.dump(all_predictions, outfile, indent=2)

    # Now figure out some stats
    # Let's start with Shannon entropy
    shannon_entropy = 0
    for item, predictions in all_predictions.items():
        shannon_entropy += sum([x[2] * log(1 / x[2]) for x in predictions])
    logger.info('Shannon entropy: %s' % shannon_entropy)

    # How many words are followed by only one word?
    num_items_with_one_following_word = len([x for _, x in all_predictions.items() if len(x) == 1])

    logger.info('Number of items followed by only one items: %s' % num_items_with_one_following_word)
    logger.info('Number of items followed by more than one items: %s' % (len(all_predictions) - num_items_with_one_following_word))

    num_doubled_items = 0
    for item, predictions in all_predictions.items():
        for prediction in predictions:
            if prediction[0] == item:
                num_doubled_items += 1
                break

    logger.info('Number of items which were followed by themselves: %s' % num_doubled_items)

    logger.info('Calculated entropy statistics for %ss in path %s' % (type, base_path))


def find(pred, iterable):
    return next(filter(pred, iterable), None)
