package com.ddubois.automt

import com.ddubois.automt.com.dduboic.automt.voynich.VoynichBook
import com.ddubois.automt.com.dduboic.automt.voynich.downloadWholeThing
import com.ddubois.automt.com.dduboic.automt.voynich.loadFromFiles
import org.apache.logging.log4j.LogManager
import org.deeplearning4j.models.embeddings.loader.WordVectorSerializer
import org.deeplearning4j.models.embeddings.wordvectors.WordVectors
import org.deeplearning4j.models.word2vec.Word2Vec
import org.deeplearning4j.text.sentenceiterator.BasicLineIterator
import org.deeplearning4j.text.tokenization.tokenizer.preprocessor.CommonPreprocessor
import org.deeplearning4j.text.tokenization.tokenizerfactory.DefaultTokenizerFactory
import java.io.File

/**
 * Created by David on 06-Feb-16.
 */

val LOG = LogManager.getLogger("com.ddubois.automt.Driver");

fun loadVoynichModel(forceRetrain : Boolean) : WordVectors {
    var voynichVec : WordVectors;

    // Try to load the vectors from file
    var vectorsFile = File("corpa/voynich/vectors.w2v");
    if(vectorsFile.canRead() && !forceRetrain) {
        // Read the vectors from the file
        voynichVec = WordVectorSerializer.loadTxtVectors(vectorsFile);
    } else {
        voynichVec = learnVoynichVectors()
    }

    return voynichVec;
}

private fun learnVoynichVectors() : WordVectors {
    var voynichVec : WordVectors;
    var manuscript = loadFromFiles();
    LOG.info("Voynich manuscript loaded");

    saveToFile(manuscript);

    var iter = BasicLineIterator(manuscript.toString().byteInputStream());
    var tokenizerFactory = DefaultTokenizerFactory();
    tokenizerFactory.setTokenPreProcessor(CommonPreprocessor());

    voynichVec = Word2Vec.Builder()
            .minWordFrequency(1)
            .iterations(5)
            .layerSize(500)
            .seed(42)
            .windowSize(5)
            .iterate(iter)
            .tokenizerFactory(tokenizerFactory)
            .build();

    LOG.info("Fitting Voynich word vectors...");
    voynichVec.fit();

    WordVectorSerializer.writeWordVectors(voynichVec, "corpa/voynich/vectors.w2v");
    return voynichVec;
}

fun saveToFile(manuscript : VoynichBook) {
    var saveFile = File("corpa/voynich/manuscript.evt");
    saveFile.appendText(manuscript.toString());
}

fun loadEnglishModel(forceRetrain : Boolean) : WordVectors {
    var LOG = LogManager.getLogger("Driver");

    var englishVec : WordVectors;

    if(forceRetrain) {
        var file = File("corpa/english/tweets_clean.txt");
        var filePath = file.path;

        LOG.info("Load & vectorise sentences");
        var iter = BasicLineIterator(filePath);
        var tokenizerFactory = DefaultTokenizerFactory();
        tokenizerFactory.setTokenPreProcessor(CommonPreprocessor());

        LOG.info("Building model...");
        englishVec = Word2Vec.Builder()
                .minWordFrequency(3)
                .iterations(2)
                .layerSize(500)
                .seed(42)
                .windowSize(5)
                .iterate(iter)
                .tokenizerFactory(tokenizerFactory)
                .build();

        LOG.info("Fitting Word2Vec model...");
        englishVec.fit();

        LOG.info("Writing word vectors to file...");

        WordVectorSerializer.writeWordVectors(englishVec, "corpa/english/vectors.w2v");

        // Closest: [game, week, public, year, director, night, season, time, office, group]

    } else {
        LOG.info("Loading google model file");
        var gModelFile = File("corpa/english/GoogleNews-vectors-negative300.bin");
        englishVec = WordVectorSerializer.loadGoogleModel(gModelFile, true);
        // Closest: [afternoon, hours, week, month, hour, weekend, days, time, evening, morning]
    }

    return englishVec;
}

fun loadSpanishModel(): WordVectors {
    var spanishFolder = File("corpa/spanish");
    var spanishVecBuilder = Word2Vec.Builder()
            .minWordFrequency(5)
            .iterations(2)
            .layerSize(100)
            .seed(42)
            .windowSize(5);

    for(file in spanishFolder.listFiles()) {
        spanishVecBuilder.iterate(BasicLineIterator(file.path));
    }

    var tokenizerFactory = DefaultTokenizerFactory();
    tokenizerFactory.setTokenPreProcessor(CommonPreprocessor());
    var spanishVec = spanishVecBuilder.tokenizerFactory(tokenizerFactory).build();

    spanishVec.fit();

    return spanishVec;
}

fun main(args : Array<String>) {
    var voynichModel = loadVoynichModel(true);
    //var englishModel = loadEnglishModel(true);

    println(voynichModel.wordsNearest("octhey", 10))
    // [ytsho, oeeockhy, shocthol, opshody, oldaiin, opom, alchedar, dold, pcheeody, qoeeo]
    // [okchochor, dalam, shtey, dais, qopcheos, qokeeody, shcfhydaiin, qal, teolshy, pcheoly]
    // [dolo, otytchy, otyda, qofchy, otaray, chckheal, yshear, dcheedy, okshes, chcthosy]
    // [kechod, sheetey, ckhod, chokan, ypchedpy, sheeoly, sholkshy, oteoy, solchey, lkeedor]
    // [ykchdy, qolkeey, olald, korary, cheef, oteey, cthoary, kom, shelain, ytchodaiin]
    // [shcthal, chek, sheoldy, chsey, checkhy, ochkchar, ykcheor, shcheaiin, ksheody, ychoy]
    // [ytsho, aiin, yees, yfchor, chdy, chedal, okar, okeedy, qokeey, ds]
    // [daiioam, cphal, okos, oykshy, kchal, cheen, ykar, kchaiin, kcho, qodam]
    // [qokshe, sheekal, cheedy, ykair, loain, qokchaiin, chdal, chekeedy, cthorchy, keeey]
    // [chkchedaram, qodaim, pyoaly, qotolaiin, socthh, dalteoshy, qokomo, otoy, checthy, qocthy]
    // [ofaiin, ycheeal, charam, ykchom, oriin, otaral, kchain, qekey, shaiiin, cheady]
    // [qtchaly, teokaiin, otolor, oteody, ykedckhy, okochey, sheeodees, oriim, alchd, kech]
    // Changes to getting whole certain lines, not just word-by-word certainties
    // [shedy, okedy, qokedar, okeey, keedy, chech, chekey, qokedy, okeedy, qol]
    // Lots of processing on raw data
    // [okedy, aiin, ar, saiin, sair, okeey, ain, chockhy, okar, okeeos]
    // [shedy, saldy, qotedy, sches, oldar, chedy, eeeos, ykeedy, cheom, lkedy]
    // [ytedy, cthhy, qokar, cheedy, qoear, schy, chekey, oltchedy, chdal, qokchdy]

    //println(englishModel.wordsNearest("app", 10));
    // [bbq, streaming, select, android, streams, now, concertgoers, mapquest, free, guide]
    // [bbq, streaming, holler, his, android, concertgoers, disc, mapquest, free, platform]
    // [select, although, android, now, streams, concertgoers, hollergram, #iphone, grape, free]
    // [streaming, android, concertgoers, grape, k, time, mapquest, free, wall, platform]
}
