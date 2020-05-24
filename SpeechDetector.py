import os
import subprocess
from FileCourier import FileCourier
from Snippet import VideoSnippet
from Timestamp import Timestamp
import Cleanser
from AudioFX import AudioFX

class SpeechDetector:

    def __init__(self, movieLocation, IBM_Filename, speaker):
        # IBM credentials
        self.api_key = YOUR_API_KEY
        self.url = "https://stream.watsonplatform.net/speech-to-text/api/v1/recognize"
        self.movieLocation = movieLocation
        self.IBM_Dictionary = {}
        self.duplicateIBM_Dictionary = {} #  used to check for duplicates
        self.humanApprovedDictionary = {}
        self.previouslyApprovedList = []
        self.wordid = 0
        self.IBM_Filename = IBM_Filename
        self.speaker = speaker

    def splitSentenceToWord(self, videoSnippet):
        songWord = videoSnippet.word
        audio_origin = videoSnippet.path
        """ open a process for each sentence transcription. Optimize by using the same process for all sentences """
        batcmd = "curl -X POST -u 'apikey:" + self.api_key + \
                 "' --header 'Content-Type: audio/mp3'" + \
                 " --data-binary @" + audio_origin + " '" + \
                 self.url + "' '" + self.url + "/?timestamps=true&max_alternatives=3'"
        wordBytes = subprocess.check_output(batcmd, shell=True)
        wordString = wordBytes.decode("utf-8")
        wordString = wordString.replace("\n", "")
        wordString = wordString.replace(" ", "")
        wordString = wordString.replace("true", "True")
        lastResult = wordString.rfind('{"results"')
        wordStampDict = wordString[lastResult:]
        try:
            resultDictionary = eval(wordStampDict)  # encode as dictionary
        except SyntaxError:
            print("Skipping this videosnippet for word %s Syntax error in string %s"%(songWord, wordStampDict))
            return None
        result = resultDictionary["results"]
        timeStampedSubtitle = []  # format: ["several":, 1.0, 1.51],["tornadoes":, 1.51, 2.15],["touch":, 2.15, 2.5] ...
        """ convert string to JSON to dictionary """
        for i in range(len(result)):
            r = result[i]
            timeStampedWords = r["alternatives"][0]["timestamps"]  # choose first alternative
            timeStampedSubtitle += timeStampedWords
        """ save transcribed subtitle as video snippets in IBM_DICTIONARY """
        return self.saveListAsSnippet(timeStampedSubtitle, videoSnippet.movieName, songWord, videoSnippet)

    def addVerifiedWordsToList(self):
        totalApprovedList = self.previouslyApprovedList.copy()
        for verifiedWord in self.humanApprovedDictionary:
            totalApprovedList.append(verifiedWord)
        return totalApprovedList

    def addVerifiedSongWord(self, wordSnippet):
        """ this word has been human-approved for the final video """
        self.humanApprovedDictionary[wordSnippet.word] = wordSnippet

    def splitUnformatTime(self, time):
        time = str(time)
        timeList = time.split(".")
        sec = timeList[0].zfill(2)
        ms = timeList[1]
        return sec, ms

    def disposePaths(self, pathSet):
        #  remove word from wordAudio folder after it has been approved / disapproved
        print("dispose path set ", pathSet)
        for path in pathSet:
            try:
                os.remove(path)
            except FileNotFoundError:
                print("cant delete because file %s not found" % path)

    def filterIBMWord(self, wordSnippet):
        """ play clips from movie that match a song word. Select the clearest one """
        adjustLeft = adjustRight = 0
        pathCollection = set()
        pathCollection.add(wordSnippet.path)
        while True:
            os.system(
                "afplay " + wordSnippet.path
            )
            isGoodAudio = input("could you hear the word: '%s' (Y(es)/A(djust)/N(o),S(ubtitle)/I(ncrease)/D(ecrease)/Spd/Slo/R(evert)" % wordSnippet.word)
            if isGoodAudio == "Y":
                self.disposePaths(pathCollection)
                return True, int(adjustLeft), int(adjustRight)
            elif isGoodAudio == "N":  # this word is incoherent
                self.disposePaths(pathCollection)
                return False, -1, -1
            elif isGoodAudio == "A":
                beginBuffer = wordSnippet.beginTime.totalms
                parentSnippetDuration = wordSnippet.parentBeginTime.findDuration(wordSnippet.parentEndTime)
                endBuffer = parentSnippetDuration - wordSnippet.endTime.totalms
                print("clip is padded with %s ms at beginning and %s ms at end" % (beginBuffer, endBuffer))
                adjustLeft = input("how much should I adjust beginning (ms)")
                adjustRight = input("how much should I adjust ending (ms)")
                return True, int(adjustLeft), int(adjustRight)
            elif isGoodAudio == "I":
                AudioFX.raiseVolumeBy50(wordSnippet)
            elif isGoodAudio == "D":
                AudioFX.lowerVolumeBy50(wordSnippet)
            elif isGoodAudio == "Spd":
                AudioFX.speedUpBy50(wordSnippet)
            elif isGoodAudio == "Slo":
                AudioFX.slowDownBy50(wordSnippet)
            elif isGoodAudio == "R":
                wordSnippet.path = wordSnippet.originalPath
            elif isGoodAudio == "S":
                os.system(
                    "afplay " + wordSnippet.parentPath
                )
            pathCollection.add(wordSnippet.path)

    def initializeIdCounter(self):
        for entry in self.IBM_Dictionary:
            entryList = self.IBM_Dictionary[entry]
            c = len(entryList)
            self.wordid += c

    def saveListAsSnippet(self, timeStampedSubtitle, movieName, songWord, parentSnippet):
        """ save word as VideoSnippet, then save to a dictionary """
        songWordVideoSnippet = None
        print("timestamped subtitle is ", timeStampedSubtitle)
        for aiWordList in timeStampedSubtitle:
            word = Cleanser.Cleanser.cleaning_word(aiWordList[0]) #  get rid of apostrophes and other annoyances
            path = os.path.join(self.movieLocation, self.speaker, "wordAudio", word + str(self.wordid) + ".mp3")
            beginSec, beginMs = self.splitUnformatTime(aiWordList[1])  # format: ["several":, 1.0, 1.51]
            endSec, endMs = self.splitUnformatTime(aiWordList[2])
            beginTS = "00:00:" + beginSec + "." + beginMs
            endTS = "00:00:" + endSec + "." + endMs
            beginTSObject = Timestamp(beginTS)
            endTSObject = Timestamp(endTS)
            videoSnippet = VideoSnippet(beginTSObject, endTSObject, word, path, movieName, parentSnippet.path, parentSnippet.beginTime, parentSnippet.endTime)
            """ save the file path of the video snippet containing word to reuse words in future songs """
            aiWordList.append(parentSnippet.path)
            if songWord == word:
                songWordVideoSnippet = videoSnippet
                continue  # dont add to IBM saved dictionary
            if word in self.IBM_Dictionary:
                wordIsDuplicate = videoSnippet.isIdentical(self.duplicateIBM_Dictionary[word]) # if so, then we have already rejected this IBM word
            else:
                wordIsDuplicate = False
            if not wordIsDuplicate:
                if word in self.IBM_Dictionary:
                    self.duplicateIBM_Dictionary[word].append(videoSnippet) # will removing videosnippet from one list delete from other dictionary?
                    self.IBM_Dictionary[word].append(videoSnippet)
                else:
                    self.duplicateIBM_Dictionary[word] = [videoSnippet]
                    self.IBM_Dictionary[word] = [videoSnippet]
                FileCourier.writeDictionaryListOfObjects(self.IBM_Filename, self.IBM_Dictionary)
                self.wordid += 1
            else:
                print("DOOP ALERT!. Word %s is a duplicate" % word) # NOT WORKING!!!
        return songWordVideoSnippet
