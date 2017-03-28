"""Aggregates the statistics from all the used languages into graphics which make comparisons between languages
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import logging

__logger = logging.getLogger('aggregate')


def get_distribution_similarities(language_data):
    """Checks how similar the data for each language is to the data for Voynichese
    
    :param language_data: A map from language to the data for the language
    :return: A map from language to how similar that language is to the Voynichese
    """

    from scipy.stats import ks_2samp

    voynichese_data = language_data['voynichese']
    similarities = dict()

    for language, data in language_data.items():
        if language is not 'Voynichese':
            similarities[language] = ks_2samp(data, voynichese_data)

    return similarities


def ngram_graph(language_data, n):
    """Graphs some data about the frequency of various n-grams.

    This code will always produce a histogram. This seems like the most useful to me.

    :param language_data: A dict from language to n-gram frequencies for that language
    :param n: The length of the grams. Used only for setting the plot's title and whatnot
    """
    x = list()
    labels = list()

    for language, data in language_data.items():
        x.append(list(data.values()))
        labels.append(language)

    plt.figure(figsize=(8, 8), dpi=80, facecolor='w', edgecolor='k')

    plt.hist(x, 10, normed=1, histtype='bar', label=np.array(labels))
    plt.title('%s-gram Frequencies' % n)
    plt.xlabel('Frequency')
    plt.ylabel('Count')
    plt.legend(prop={'size': 10})

    plt.savefig('%s-gram frequencies' % n)
    plt.clf()


def one_gram_graph(language_data):
    """Creates a graph for 1-gram frequencies

    :param language_data: A dict from language to 1-gram frequencies for that language
    """
    ngram_graph(language_data, 1)


def two_gram_graph(language_data):
    """Creates a graph for 2-gram frequencies

    :param language_data: A dict from language to 2-gram frequencies for that language
    """
    ngram_graph(language_data, 2)


def three_gram_graph(language_data):
    """Creates a graph for 3-gram frequencies

    :param language_data: A dict from language to 3-gram frequencies for that language
    """
    ngram_graph(language_data, 3)


def morpheme_frequency_graph(language_data):
    """Graphs out the morpheme frequencies

    :param language_data: A dist from language to morpheme frequency
    """

    x = list()
    labels = list()
    for language, data in language_data.items():
        total_frequencies = sum(list(data.values()))
        normalized_frequencies = [x / total_frequencies for (_, x) in data.items() if x > 1]
        x.append(normalized_frequencies)

        labels.append(language)

    plt.figure(figsize=(8, 8), dpi=80, facecolor='w', edgecolor='k')

    plt.hist(x, 10, label=labels)
    plt.title('Morpheme Frequencies > 1')
    plt.xlabel('Normalized Frequency')
    plt.ylabel('Count')
    plt.legend(prop={'size': 10})

    plt.savefig('Morpheme Frequencies > 1', bbox_inches='tight')

    plt.clf()


def word_frequency_graph(language_data):
    """Graphs information on word frequencies

    :param language_data: A dict from language to word frequency information
    """
    x = list()
    labels = list()
    for language, data in language_data.items():
        total_frequencies = sum(list(data.values()))
        normalized_frequencies = [x / total_frequencies for (_, x) in data.items() if x > 1]
        x.append(normalized_frequencies)

        labels.append(language)

    plt.hist(x, 10, label=labels)
    plt.title('Word Frequencies > 1')
    plt.xlabel('Normalized Frequency')
    plt.ylabel('Count')
    plt.legend(prop={'size': 10})
    plt.savefig('Word Frequencies > 1', bbox_inches='tight')

    plt.clf()


def morphemes_per_word_graph(language_data):
    """Graphs information about the morphemes per word

    :param language_data: A dict from language to morpheme per word information
    """
    x = list()
    labels = list()

    for language, data in language_data.items():
        x.append(data)
        labels.append(language)

    plt.figure(figsize=(8, 8), dpi=80, facecolor='w', edgecolor='k')

    plt.hist(x, 10, normed=1, histtype='bar', label=np.array(labels))
    plt.title('Morphemes Per Word')
    plt.xlabel('Frequency')
    plt.ylabel('Count')
    plt.legend(prop={'size': 10})

    plt.savefig('Morphemes per Word')
    plt.clf()


def morpheme_length_graph(language_data):
    """Graphs morpheme length information

    :param language_data: A dict from language to morpheme lengths
    """
    x = list()
    labels = list()

    for language, data in language_data.items():
        x.append(data)
        labels.append(language)

    plt.figure(figsize=(8, 8), dpi=80, facecolor='w', edgecolor='k')

    # plt.xlim(xmax=0.02)
    # TODO: only show data up to 0.02

    plt.hist(x, 10, normed=1, histtype='bar', label=np.array(labels))
    plt.title('Morpheme Length')
    plt.xlabel('Frequency')
    plt.ylabel('Count')
    plt.legend(prop={'size': 10})

    plt.savefig('Morpheme Length')
    plt.clf()


def aggregate_stats():
    """Reads in the stats in the saved json file, then prints all the stats for each language onto the same graph for
    easy comparison"""

    with open('all_data.json', 'r') as jsonfile:
        all_data = json.load(jsonfile)

        similarities_for_stats = dict()

        for series_type, language_data in all_data.items():
            __logger.info('Calculating stats for series type %s' % series_type)
            {
                '1-gramFrequencies': one_gram_graph,
                '2-gramFrequencies': two_gram_graph,
                '3-gramFrequencies': three_gram_graph,
                'morphemeFrequency': morpheme_frequency_graph,
                'wordFrequency': word_frequency_graph,
                'morphemesPerWord': morphemes_per_word_graph,
                'morphemeLength': morpheme_length_graph,

            }.get(series_type)(language_data)

            similarities_for_stats[series_type] = get_distribution_similarities(language_data)

        with open('similarities.json', 'w') as similaritiesfile:
            json.dump(similarities_for_stats, similaritiesfile)