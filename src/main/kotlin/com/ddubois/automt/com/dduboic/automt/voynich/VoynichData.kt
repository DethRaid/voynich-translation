package com.ddubois.automt.com.dduboic.automt.voynich

import java.util.*

/**
 * Created by David on 10-Feb-16.
 */

class VoynichBook(var folios: MutableList<VoynichFolio>) {
    override fun toString() : String {
        var book : String = "";

        folios.forEach { page -> book += page; }

        return book;
    }
}

class VoynichFolio(var lines : List<VoynichLine>) {
    override fun toString() : String {
        var text : String = "";

        lines.forEach { line -> text += line; }

        return text;
    }
}

class VoynichLine(var words : List<List<VoynichWord>>) {
    override fun toString() : String {
        var line : String = "";

        // Go through the words in each line consecutively
        // Get the most certain proposed transcription
        // Add it to the list
        for(i in words[0].indices) {
            var wordCounts = getWordCounts(i)

            var highestWord: String = getHighestWord(wordCounts)

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

        for (wordInd in words.indices) {
            if(words[wordInd].size > i) {
                var curWord = words[wordInd][i];

                // Do we have a good word?
                // Add more if we have a certain word so that certain words are more useful, but if everything is uncertain we can still get something
                var amountToAdd = 1;
                if (curWord.certain) {
                    amountToAdd = 2;
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
