"""Concatenates all the Voynich transcription files into a single pretty file

The files has spaces between words, rather than periods. It also has all the comments and metadata removed, so there's 
only the actual words. This code also tries to resolve unknown letters by searching for similar words in the text 
that don't have the same uncertain characters

I'm unsure what to do about sentences or whatever. There's no clear sentence boundaries in the transcription. I'll 
start out with lines being lines, and maybe try folios being lines or maybe make the whole thing a line. Not sure, I'll 
see what gives the prettiest results I guess.
"""

import logging
import re
import sys
from os import listdir
from collections import defaultdict

_log = logging.getLogger('concatenate')


def process_line(line):
    """Processes a single line to remove all comments and line breaks and everything

    :param line: A single line of text from an EVA file
    :return: The line of text as an array of words
    """ 
    start_chars = ['<']
    end_chars = ['>']
    write_character = True

    final_string = ''

    # Do one pass through the line to remove comments and null characters
    # Do another pass to break the line into words

    for char in line: 

        if char in start_chars: 
            write_character = False

        if write_character:
            final_string += char

        if char in end_chars:
            write_character = True

    return final_string


def process_line_group(cur_line_group):
    # Examine the lines in parallel. For each positino in the line, look for the most common character amoung the 
    # various transcriptions. If there's a tie, randomly chose one of the characters
    # If an unknown letter persists in the final line, we can try to figure out what the word is based on in some
    # downstream step

    # Remove any lines with a length of 0
    line_group = [line.strip() for line in cur_line_group if len(line) > 0]
    if len(line_group) == 0:
        return ''

    final_line = ''

    reading_line = []
    for _ in line_group:
        reading_line.append(True)

    start_chars = ['{']
    end_chars = ['}']

    # assume that all the lines are the same length. Pretty sure this is true
    for index in range(0, len(line_group[0])):
        characters = defaultdict(int) 
        for idx, line in enumerate(line_group):
            if line[index] in start_chars:
                reading_line[idx] = False

            if reading_line[idx]:
                characters[line[index]] += 1

            if line[index] in end_chars:
                reading_line[idx] = True

        common_char = ''
        if len(characters) > 0:
            common_char = next(iter(characters))[0]
            for key, value in characters.items():
                if value >= characters[common_char]:
                    common_char = key

        final_line += common_char

    _log.info('Derived line\n%s\nfrom line group\n%s' % (final_line, line_group))

    return final_line


def process_file(file_path):
    """Opens a single file and processes it

    The processing can happen a few different ways: There's a simple line
    processor which just gets the first line that's completely certain, and a
    voting processor which gets the most common and most certain transcription
    of each word

    :param file_path: The path to the file to process
    :return: A single string representing the whole processed file
    """
    processed_file = ''
    skipped_first = False

    with open(file_path) as f:
        _log.info('Beginning %s' % file_path)

        content = f.readlines()
        cur_line_group = list()
        cur_line = ''
        can_append = True
        for line in content:
            if not skipped_first:
                skipped_first = True
                continue

            if line[0] == '#':
                # We have a comment, take the last few lines and process them together
                cur_line_san = process_line(cur_line)
                cur_line_group.append(cur_line_san)
                _log.debug('Found a comment, processing group %s' % cur_line_group)
                processed_file += process_line_group(cur_line_group)
                cur_line_group = list()
                cur_line = ''
                # We've most recently seen a comment. The next line is probably a continuation of the comment that got
                # shoved to the next line, so we don't want to save it
                can_append = False
            else:
                if line[0] == '<': 
                    # If the line starts with a <, we should cut off the last line
                    cur_line_san = process_line(cur_line) 
                    _log.debug('Found a new line, adding "%s" to the current line group' % cur_line_san)

                    cur_line_group.append(cur_line_san)
                    cur_line = ''
                    cur_line += line
                    _log.debug('Appended "%s" to the new current line' % line)
                    # We've most recently seen a Real Line. The next line is probably a continuation of the Real Line
                    # that got shoved to the next line, so we want to save it
                    can_append = True
                elif can_append:
                    # There's no '-' or '=' at the end of the line, so it's an incomplete line and we
                    # can append it to the current line accumulator
                    cur_line += line 

        # We've done all the lines, but we still need to process the last line
        cur_line_san = process_line(cur_line)
        cur_line_group.append(cur_line_san)
        _log.debug('appended %s' % cur_line_san)
        processed_file += process_line_group(cur_line_group)

    line_with_spaces = re.sub('[\.\-]', ' ', processed_file) 
    line_with_spaces = re.sub('=', '\n', line_with_spaces)

    line_with_spaces = re.sub('!', '', line_with_spaces)

    return line_with_spaces


def word_similarity(good_word, bad_word):
    """Checks how similar good_word is to bad_word
    
    Anytime bad_word has a *, any letter from good_word is accepted. Anytime good_word has a * its letter is not 
    accepted
    
    > has_same_letters('okthy', 'o*thy')
    > 1.0
    
    > has_same_letters('okt*y', 'o*thy')
    > 0.8
    
    > has_same_letters('okthy', 'dar')
    > 0.0
    
    :param good_word: The word to check for similarity to our word
    :param bad_word: The word we want to generate hypotheses for
    :return: A number saying how similar the words are
    """
    if len(good_word) != len(bad_word):
        return 0

    num_same_chars = 0

    for idx in range(len(bad_word)):
        if good_word[idx] != '*' and (good_word[idx] == bad_word[idx] or bad_word[idx] == '*'):
            num_same_chars += 1

    return num_same_chars / len(good_word)


def resolve_unkonwn_characters(manuscript_string):
    """Tries to resolve words with unknown characters by comparing the words to other words in the manuscript
    
    There's a number of tricks here:
    - If the word in question is missing letters, and there's only one word with the same letters save for the missing 
    ones), we use that word.
    - If the word in question is missing letters, and there's words available which miss letters in other places, we 
    take known letters from whatever word has them
    - If there's multiple hypothesis for what the word with missing letters could be, we examine the words before and 
    after current word and all its hypothesis to try to match the context of the word in question with the context of
    a single hypothesis
    - The code here should rely on word context more as the word in question is missing more and more letters
    
    :param manuscript_string: The full text of the manuscript
    :return: The full text of the manuscript, with as many unknown letters resolved as possible
    """
    word_frequencies = defaultdict(int)

    # a map from word to the previous two words. The number 2 was chosen because Statistical Machine Translations often
    # use a 3-gram language model when evaluating if a sentence if valid in the target language. If 3-grams are good
    # enough for them, they're good enough for me
    contexts = defaultdict(list)

    words_needing_resoling = []

    for line in manuscript_string.split('\n'):
        words = line.split()
        for idx, word in enumerate(words):
            if idx == 0:
                previous_word = 'BEG'
            else:
                previous_word = words[idx - 1]

            if idx < 2:
                previous_previous_word = 'BEG'
            else:
                previous_previous_word = words[idx - 2]

            contexts[word].append((previous_previous_word, previous_word))

    for word, _ in contexts.items():
        word_frequencies[word] += 1
        if '*' in word:
            words_needing_resoling.append(word)

    # Map from word with unknown letters to its hypothesis. Hypotheses are a tuple of (word, frequency, fitness)
    substitution_hypotheses = defaultdict(list)
    for bad_word in words_needing_resoling:
        for good_word, count in word_frequencies:
            word_fitness = word_similarity(good_word, bad_word)
            substitution_hypotheses[bad_word].append((good_word, count, word_fitness))

    for bad_word, hypotheses in substitution_hypotheses.items():
        # Find the most fit hypothesis. Hopefully there's only one with a fitness of 1.0 and we can party
        # If there's more than one with a fitness of 1.0, find the one with the highest count
        highest_fitness = 0
        for hypothesis in hypotheses:
            if hypothesis[2] > highest_fitness:
                highest_fitness = hypothesis[2]

        hypotheses_with_max_fitness = []
        for hypothesis in hypotheses:
            if hypothesis[2] > highest_fitness - 0.01:  # Floating-point comparison, so we don't want to test equality
                hypotheses_with_max_fitness.append(hypothesis)

        if len(hypotheses_with_max_fitness) == 1:
            # This is awesome. We know exactly what the word should be
            # Now we just need to cross-reference to resolve unknown characters
            final_word = build_final_word([bad_word, hypotheses_with_max_fitness[0]])

        else:
            # This is the tricky bit. We have multiple hypothesis with the same fitness, so we need to figure out which
            # one has the most similar context
            # Someone observed that Voynichese seems to have a link between morphology and semantics, such that words
            # which look similar are similar. Imma use a bag-of-letters for word similarity. It probably won't be
            # great, but it should work?
            context_similarities = {}
            bad_context = contexts[bad_word]

            for hypothesis in hypotheses_with_max_fitness:
                maybe_good_word = hypothesis[0]
                context = contexts[maybe_good_word]


def build_final_word(words):
    """Builds the final word out of all the words that might be the one we want
    
    :param words: A list of all the words that might substitute for the words in question, plus the word in question
    :return: The word we want (probably)
    """
    final_letters = []
    for idx in range(len(words[0])):
        char_counts = defaultdict(int)
        for word in words:
            if word[idx] != '*':
                char_counts[word[idx]] += 1

        if len(char_counts) == 1 and '*' in char_counts:
            # The only character we could find is a star, so let's just append that
            final_letters.append('*')

        else:
            most_common_char = 'f'  # Doesn't matter what this is. defaultdict gives us 0 for unknowns
            for char, count in char_counts:
                if count < char_counts[most_common_char]:
                    most_common_char = char

            final_letters.append(most_common_char)

    return ''.join(final_letters)


def concatenate_files(manuscript_file_name, manuscript_directory):
    """Take all the files downloaded in the download_files step and process them

    After this function finishes, there should be a new file, corpus.txt,
    with the full text of the Voynich manuscript arranged with one line of
    Voynich per line in the file, with only certain words and with spaces
    instead of periods

    :param manuscript_file_name: The name of the file to write the manuscript to
    :param manuscript_directory: the directory where all the files from the manuscript are
    """
    # Go through each file in the folder
    # Look at each group of lines
    # Return a list of good words
    # Concatenate the lines using the line concatenator
    files = [f for f in listdir(manuscript_directory)]

    # The full string of the manuscript
    manuscript_string = ''

    for file_path in sorted(files):
        if not file_path[-3:] == 'txt':
            _log.info('Skipping non-text file %s' % file_path)
            continue
        if file_path == 'corpus.txt':
            continue
        try:
            manuscript_string += process_file(manuscript_directory + file_path) + '\n'
        except Exception as e:
            _log.error('Failed to process file %s' % file_path)
            _log.exception(e)

    # Get rid of the stupid = signs
    manuscript_string = manuscript_string.replace('=', '\n')

    resolve_unkonwn_characters(manuscript_string)

    with open(manuscript_file_name, 'w') as f:
        f.write(manuscript_string)


def print_help():
    print("""This script concatenates all the txt files for the Voynich Manuscript into
    a single model, trying to resolve as many unknown characters as possible

Try calling it with no arguments to see it work!""")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print_help()
        sys.exit()

    concatenate_files('corpus.txt', 'corpa/voynichese')
    _log.info('Input files concatenated')
