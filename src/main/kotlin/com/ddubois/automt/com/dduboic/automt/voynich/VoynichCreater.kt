package com.ddubois.automt.com.dduboic.automt.voynich

import org.apache.http.client.methods.HttpGet
import org.apache.http.impl.client.HttpClients
import org.apache.http.util.EntityUtils
import org.apache.logging.log4j.Level
import org.apache.logging.log4j.LogManager
import java.io.File
import java.io.FileNotFoundException
import java.util.*

/**
 * Created by David on 10-Feb-16.
 */

val BASE_URL = "http://www.voynich.nu/";
val LOG = LogManager.getLogger("VoynichDownloader");

val PAGES_IN_FOLIOS         = intArrayOf(8, 8, 8, 8, 8, 8, 8, 10, 2, 2, 2, 2, 10, 2, 4, 2, 4, 2, 4, 14);
val NUM_FOLIOS              = PAGES_IN_FOLIOS.reduce { accum, value -> accum + value };

val client = HttpClients.createDefault();

/**
 * Downloads a single page of the Voynich manuscript and returns it as a string
 *
 * Downloads both the v and r folio
 *
 * @param quire The number of the quire to get the folio from
 * @param folio The number of the folio to get
 *
 * @return The full text of each folio
 */
private fun getFolioText(quire : Int, folio : Int) {
    /*var folioText =*/ getSingleFolio(quire, folio, "v");
    /*folioText +=*/ getSingleFolio(quire, folio, "r");

    //return folioText;
}

private fun getSingleFolio(quire: Int, folio: Int, code: String) {
    var quireName = String.format("q%02d", quire);
    var folioName = String.format("f%03d${code}_tr.txt", folio);

    var getRequest = HttpGet(BASE_URL + quireName + "/" + folioName);
    getRequest.addHeader("accept", "application.text");

    LOG.debug("Sending GET to " +getRequest);

    var response = client.execute(getRequest);

    if (response.statusLine.statusCode != 200) {
        LOG.error("Could not get file for quire $quire and folio $folio. Full status line: ${response.statusLine}");
        response.close();
        return;
    }

    var responseString = EntityUtils.toString(response.entity);

    var saveFile = File(folioName);
    saveFile.appendText(responseString);
}

/**
 * Checks if any of the characters in the text are an exclamation point. If so, removes the exclamation mark and
 * marks the word as uncertain
 *
 * @param text The text of the word
 *
 * @return The new VoynichWord
 */
private fun makeVoynichWord(text : String) : VoynichWord {
    var word = "";
    var certain = true;

    text.forEach { char ->
        if(char == '!') {
            certain = false;
        } else {
            word += char;
        }
    }

    return VoynichWord(word, certain);
}

/**
 * Parses the proposed transcription lines to generate a structure with all the lines
 *
 * @param lines The proposed transcription lines. Each line should have the <> stuff removed, but should be otherwise
 *  untouched. Each lines should also not be a comment line, but an actual transcription line.
 *
 * @return A VoynichLine that represents all the given transcription lines
 */
private fun makeVoynichLine(lines : MutableList<String>) : VoynichLine {
    var fullWords : MutableList<MutableList<VoynichWord>> = ArrayList();
    lines.forEach { line ->
        var wordsInLine : MutableList<VoynichWord> = ArrayList();
        // Split the line on periods, because those delimit words
        var words = line.splitToSequence('.');

        words.forEach { word ->
            var wordSan = sanitize(word);

            wordsInLine.add(makeVoynichWord(wordSan));
        }

        fullWords.add(wordsInLine);
    }

    return VoynichLine(fullWords);
}

/**
 * Removes any {} stuff from the word
 *
 * @param word The word to remove things from
 *
 * @return The sanitized word
 */
private fun sanitize(word: String): String {
    // Get rid of anything between a - and }, inclusive
    if(word.contains('-')) {
        return word.substringBefore('-');
    } else {
        return word;
    }
}

/**
 * Generates a VoynichPage from the given text
 *
 * TODO: Make this function include the image description as a page comment
 *
 * @param text The full text of the folio, comments and all
 *
 * @return The VoynichFolio that comes from the given text
 */
private fun makeVoynichFolio(text : String) : VoynichFolio {
    var lines = text.lines();
    var curLineGroup : MutableList<String> = ArrayList();
    var voynichLines : MutableList<VoynichLine> = ArrayList();

    lines.forEach { line ->
        if (line.startsWith("#")) {
            // If the line starts with a #, it's a comment and we can ignore it for right now.

            // Although, being in a comment means we should make a new VoynichLine from the current line group
            if (curLineGroup.isNotEmpty()) {
                voynichLines.add(makeVoynichLine(curLineGroup));
                curLineGroup.clear();
            }

        } else {
            // Get everything past the last whitespace
            curLineGroup.add(line.substringAfterLast(' '));
        }
    }

    return VoynichFolio(voynichLines);
}

/**
 * Downloads the full Voynich manuscript from http://www.voynich.nu/
 *
 * If any pages are unavailable, they're not added and nothing bad happens.
 *
 * Saves all pages to separate files
 *
 * @return The Voynich Book
 */
fun downloadWholeThing() {
    var folioToGet = 1;

    for(curQuire in PAGES_IN_FOLIOS.indices) {
        for (curFolio in 1..PAGES_IN_FOLIOS[curQuire]) {
            getFolioText(curQuire + 1, folioToGet);

            folioToGet++;
        }
    }
}

fun loadFromFiles() : VoynichBook {
    var folios : MutableList<VoynichFolio> = ArrayList();

    for(i in 1..NUM_FOLIOS) {
        // Get both the v and r folios
        var folioFile : File;

        try {
            LOG.info("Trying to load folio ${i}r");

            folioFile = File(String.format("corpa/voynich/f%03dr_tr.txt", i));
            folios.add(makeVoynichFolio(folioFile.readText()));

            LOG.info("Loaded folio " + folioFile.name);
        } catch(e : FileNotFoundException) {
            LOG.log(Level.ERROR, "Could not read folio ${i}v", e);
        }

        try {
            LOG.info("Trying to load folio ${i}v");

            folioFile = File(String.format("corpa/voynich/f%03dv_tr.txt", i));
            folios.add(makeVoynichFolio(folioFile.readText()));

            LOG.info("Loaded folio " + folioFile.name);
        } catch(e : FileNotFoundException) {
            LOG.log(Level.ERROR, "Could not read folio ${i}r", e);
        }
    }

    return VoynichBook(folios);
}

