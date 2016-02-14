package com.ddubois.automt.com.dduboic.automt.voynich

import java.util.*

/**
 * Created by David on 10-Feb-16.
 */

class VoynichBook(var folios: MutableList<VoynichFolio>) {
    override fun toString() : String {
        var book : String = "";

        folios.forEach { page -> book += page }

        return book;
    }
}

class VoynichFolio(var lines : List<VoynichLine>, var num : Int) {
    override fun toString() : String {
        var text : String = "$num\n";

        lines.forEach { line -> text += line; }

        return text;
    }
}

class VoynichLine(var linePossibilities : List<List<VoynichWord>>) {
    override fun toString() : String {
        return getLineComplete()
    }

    private fun getLineComplete() : String {
        for(line in linePossibilities) {
            // If the whole line is certain, return it
            var certain = true;
            var lineText = "";
            for(word in line) {
                if(!word.certain) {
                    certain = false;
                }
                lineText += word.word + " ";
            }

            if(certain) {
                return lineText + "\n";
            }
        }

        // If none of the lines are certain, return the empty string
        return "";
    }

    private fun getLineVoting() : String {
        var line : String = "";

        // Go through the words in each line consecutively
        // Get the most certain proposed transcription
        // Add it to the list
        for (i in linePossibilities[0].indices) {
            var wordCounts = getWordCounts(i)

            var highestWord : String = getHighestWord(wordCounts)

            line += highestWord + " ";
        }

        return line + "\n";
    }

    private fun getHighestWord(wordCounts: HashMap<String, Int>): String {
        var highestWord: String? = null;
        var initialized = false;

        for (word in wordCounts.keys) {
            if (!initialized) {
                // Not sure
                highestWord = word;
                initialized = true;
            }

            if (wordCounts[word]!! > wordCounts[highestWord]!!) {
                highestWord = word;
            }
        }

        return highestWord!!;
    }

    private fun getWordCounts(i: Int): HashMap<String, Int> {
        var wordCounts = HashMap<String, Int>();

        for (wordInd in linePossibilities.indices) {
            if(linePossibilities[wordInd].size > i) {
                var curWord = linePossibilities[wordInd][i];

                // Do we have a good word?
                // Add more if we have a certain word so that certain words are more useful, but if everything is uncertain we can still get something
                var amountToAdd = 1;
                if (curWord.certain) {
                    amountToAdd = 4;
                }

                var count = wordCounts[curWord.word];
                if (count != null) {
                    wordCounts[curWord.word] = count + amountToAdd;
                } else {
                    wordCounts[curWord.word] = amountToAdd;
                }
            }
        }
        return wordCounts;
    }
}

data class VoynichWord(val word : String, val certain : Boolean);
