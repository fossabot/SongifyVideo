import os
from ffprobe import FFProbe
from Timestamp import Timestamp

class VideoAssembler:
    def __init__(self, movieLocation, instrumentalLocation, videoTrimmer, speaker, songTitle):
        self.movieLocation = movieLocation
        self.speaker = speaker
        self.songTitle = songTitle
        self.instrumentalLocation = instrumentalLocation
        self.upperAtempoBound = 3.0 # must be less than or equal to tempo limits specified in string multiple atempo (1/4 < tempo < 4)
        # 50 - 50 RATIO means speed up/ slow down lyric / combined clip by same factor. Adjust if necessary
        self.combinePacePct = 0.7
        self.songPacePct = 1 - self.combinePacePct
        self.videoTrimmer = videoTrimmer
        self.paddingCounter = 0
        self.stretchCounter = 0

    def getLyricDuration(self, beginTimestamp, endTimestamp):
        """ return begin, end timestamp from SRT line """
        beginTS = beginTimestamp.replace(",", ":")
        endTS = endTimestamp.replace(".", ":")
        beginSplit = beginTS.split(":")
        endSplit = endTS.split(":")
        secBegin = beginSplit[2]
        secEnd = endSplit[2]
        msBegin = beginSplit[3]
        msEnd = endSplit[3]
        return (secEnd - secBegin)*1000 + (msEnd - msBegin) # return duration in milliseconds

    # INACCURATE eg 2763 ms rounded to 2.76 seconds
    def getFileLengthMs(self, fileName, isAudio=False):
        if not isAudio:
            ms = int(float(FFProbe(fileName).video[0].duration) * 1000)  # duration in milliseconds
        else:
            ms = int(float(FFProbe(fileName).audio[0].duration) * 1000)  # duration in milliseconds
        return ms

    def formatSubtitle(self, stamp):
        splitstamp = str(stamp).split(".")
        second = splitstamp[0]
        milli = splitstamp[1]
        second = second.zfill(2)
        subtitle = "00:00:" + second + "." + milli
        return subtitle

    def addSilence(self, silenceDuration, lyricItr):
        """ calculate duration of the pause between lyrics and trim the right amount of silence"""
        silenceTS = Timestamp()
        silenceEnd = silenceTS.convertTotalMsToString(silenceDuration)
        silenceVideoName = os.path.join(self.movieLocation, "silence", "silence" + str(lyricItr) + ".mp4")
        silenceVidInput = self.speaker.lower() + "swag" + ".mp4"
        os.system(
            "/usr/local/opt/ffmpeg/bin/ffmpeg -i /Users/edwardcox/Desktop/TomCruiseSing/silence/"+ silenceVidInput + "\
             -ss 00:00:00.0" + " -to " + silenceEnd + " -y " + silenceVideoName)  # removed -c copy to re-encode
        return silenceVideoName

    def getSavedIbmValues(self, IBMDictionary, songWord):
        ibmWordBeginTime = IBMDictionary[songWord][1]
        ibmWordBeginTimestamp = Timestamp(self.formatSubtitle(ibmWordBeginTime))
        ibmWordEndTime = IBMDictionary[songWord][2]
        ibmWordEndTimestamp = Timestamp(self.formatSubtitle(ibmWordEndTime))
        return ibmWordBeginTimestamp, ibmWordEndTimestamp

    def padClipWithSilence(self, silenceClip, combinedClip, outputFilename, instrumentalFilename, id):
        intermedStretchFilename = "stretchedCombineClip/stretchedCombineClip" + str(id) + "special.mp4"
        self.combineVideoClips([silenceClip, combinedClip], intermedStretchFilename) #  combine silence with combined clip
        self.mixVideoWithAudio(intermedStretchFilename, instrumentalFilename, outputFilename)

    def normalizeVideoClip(self, videoLocationList):
        """ to concatenate videos losslessly , must make sure all codoecs, timebases match (eg normalize) """
        newVideoLocationList = []
        for videoLocation in videoLocationList:
            oldVideoLocation = os.path.join(self.movieLocation, videoLocation)
            newVideoLocation = "normalized" + videoLocation.split("/")[-1]
            newVideoLocationFullPath = os.path.join(self.movieLocation, "normalizedClip", newVideoLocation)
            normalizecmd = "/usr/local/opt/ffmpeg/bin/ffmpeg -i " + oldVideoLocation + " -map 0:0 -map 0:1 -c:a aac -ar 48000 -ac 2 -vf scale=640x360 -c:v libx264 -profile:v baseline -video_track_timescale 60000 -y " + newVideoLocationFullPath
            os.system(normalizecmd)
            newVideoLocationList.append(newVideoLocationFullPath)
        return newVideoLocationList

    def combineVideoClips(self, videoLocationList, videoDestination):
        # normalize all the clips, combine all the clips
        videoLocationList = self.normalizeVideoClip(videoLocationList)
        vidClipLocationTxtFile = "/Users/edwardcox/Desktop/TomCruiseSing/combineClip/videoClipLocation.txt"
        f = open(vidClipLocationTxtFile,"w")
        # write video locations to file
        for vid in videoLocationList:
            f.write("file '" + vid + "'\n")
        f.close()
        combinecmd = "ffmpeg -f concat -safe 0 -i " + vidClipLocationTxtFile + " -codec copy -y " + videoDestination
        os.system(combinecmd)

    def mixVideoWithAudio(self, videoFilename, instrumentalFilename, outputFilename):
        os.system(
            "/usr/local/opt/ffmpeg/bin/ffmpeg -y -i " + videoFilename + " -i " + instrumentalFilename + \
            " -filter_complex '[0][1]amix=2,apad[a];[0:a][a]amerge[a]' -map 0:v -map [a] -c:v copy -ac 2 " + outputFilename
        )

    def trimAllSongWord(self, humanApprovedDictionary):
        for songWord in humanApprovedDictionary:
            wordSnippet = humanApprovedDictionary[songWord]
            mp4Path = os.path.join(self.movieLocation, self.speaker, wordSnippet.movieName,
                                   wordSnippet.movieName + ".mp4") #+ "Compress.mp4")  # use compressed video NOT original
            start_timestamp = wordSnippet.beginTime.addTimestamp(wordSnippet.parentBeginTime.totalms, modify=False)
            end_timestamp = wordSnippet.endTime.addTimestamp(wordSnippet.parentBeginTime.totalms, modify=False)
            video_destination = os.path.join(self.speaker, "wordVideo", "Preprocess" + songWord + ".mp4")
            print("Creating Video At", video_destination)
            os.system(
                "/usr/local/opt/ffmpeg/bin/ffmpeg -i " + mp4Path + " -ss " + start_timestamp +
                " -to " + end_timestamp + " -filter:a 'volume=" + str(wordSnippet.volume) + "' -y " + video_destination
            )  # removed -c copy to re-encode
            final_video_destination = os.path.join(self.speaker, "wordVideo", songWord + ".mp4")
            audioPaceStr = self.stringMultipleATempo(wordSnippet.speed)
            self.stretchClipCmd(video_destination, 1 / wordSnippet.speed, audioPaceStr, final_video_destination)
            # delete video destination
            os.remove(video_destination)

    def getSongWordLocations(self, wordList, songLine):
        wordFileList = os.listdir(os.path.join(self.speaker, "wordVideo"))
        for songWord in songLine:
            songWord = songWord.lower()
            filename = songWord + ".mp4"
            video_path = os.path.join(self.speaker, "wordVideo", filename)
            """ check if the word has been approved already. There should be a word video created for saved words """
            if filename in wordFileList:
                wordList.append(video_path)
        return wordList

    def stringMultipleATempo(self, tempo):
        """ tempoBound must be between 1/4 and 4 or will exceed ffmpeg limits (0.5 < x < 2.0)"""
        if tempo > 2.0 or tempo < 0.5:
            print("ADJUSTING ATEMPO!!!")
            smalltempo = tempo ** (1/2)
            tempoStr ="atempo=" + str(smalltempo) + "," + "atempo=" + str(smalltempo)
            return tempoStr
        else:
            return "atempo=" + str(tempo)

    def stretchClipCmd(self, videoOrigin, videoPace, audioPace, outputFilename):
        stretchCombineCmd = "/usr/local/opt/ffmpeg/bin/ffmpeg -i " + videoOrigin + " -filter_complex '[0:v]setpts=" + \
                            str(videoPace) + "*PTS[v];[0:a]" + str(audioPace) + "[a]' -map " + \
                            "'[v]' -map '[a]' -y " + outputFilename
        os.system(stretchCombineCmd)

    def stretchAudioCmd(self, instrumentalClipLocation, audioInstrumentalPaceStr, instrumentalStretchFilename):
        stretchInstrumentalCmd = "/usr/local/opt/ffmpeg/bin/ffmpeg -i " + instrumentalClipLocation + \
                                 " -filter_complex '[0:a]" + audioInstrumentalPaceStr + "[a]' -map " + \
                                 "'[a]' -y " + instrumentalStretchFilename
        os.system(stretchInstrumentalCmd)

    def stretchClip(self, videoOrigin, instrumentalClipLocation, id):
        """ stretch the combined clip to the subtitle duration """
        combineClipDuration = self.getFileLengthMs(videoOrigin)
        lyricDuration = self.getFileLengthMs(instrumentalClipLocation, True)
        """ Adjust tempo of instrumental and combined clips according to the ratio. Remember for both clips: 0.5 tempo < 2.0 """
        durationDelta = abs(combineClipDuration - lyricDuration)
        if combineClipDuration < lyricDuration:
            print("COMBINED CLIP ID %s IS FASTER THAN INSTRUMENTAL" % id)
            audioCombineClipPace = combineClipDuration / (combineClipDuration + self.combinePacePct * durationDelta)  # Less than 1 means slow down
            audioInstrumentalPace = lyricDuration / (combineClipDuration + self.combinePacePct * durationDelta) # speed up (compensate for offset)
        else:
            print("COMBINED CLIP ID %s IS SLOWER THAN INSTRUMENTAL" % id)
            audioInstrumentalPace =  lyricDuration / (lyricDuration + self.songPacePct * durationDelta) # slow down
            audioCombineClipPace = combineClipDuration / (lyricDuration + self.songPacePct * durationDelta) # speed up
        videoInstrumentalPace = 1 / audioInstrumentalPace
        videoCombineClipPace = 1 / audioCombineClipPace
        finalStretchFilename = "stretchedCombineClip/stretchedCombineClip" + str(id) + ".mp4"
        # print("LYRIC DURATION IS %s COMBINED CLIP DURATION IS %s" % (lyricDuration, combineClipDuration))
        # print("VIDEO INSTRUMENTAL PACE IS", videoInstrumentalPace)
        # print("videoCombineClipPace %s videoInstrumentalPace %s audioCombineClipPace %s audioInstrumentalPace %s" %
        #       (videoCombineClipPace, videoInstrumentalPace, audioCombineClipPace, audioInstrumentalPace))
        if videoCombineClipPace < self.upperAtempoBound and videoCombineClipPace > 1/self.upperAtempoBound and \
                videoInstrumentalPace < self.upperAtempoBound and videoInstrumentalPace > 1/self.upperAtempoBound:
            print("STRETCH VIDEO ID", id)
            combineStretchFilename =  "testing/testing" + str(id) + ".mp4"
            instrumentalStretchFilename = "testing/testing" + str(id) + ".mp3"
            audioCombineClipPaceStr = self.stringMultipleATempo(audioCombineClipPace)
            self.stretchClipCmd(videoOrigin, videoCombineClipPace, audioCombineClipPaceStr, combineStretchFilename)
            # stretchCombineCmd = "/usr/local/opt/ffmpeg/bin/ffmpeg -i " + videoOrigin + " -filter_complex '[0:v]setpts=" + \
            #               str(videoCombineClipPace) + "*PTS[v];[0:a]" + audioCombineClipPaceStr + "[a]' -map " + \
            #               "'[v]' -map '[a]' -y " + combineStretchFilename
            audioInstrumentalPaceStr = self.stringMultipleATempo(audioInstrumentalPace)
            self.stretchAudioCmd(instrumentalClipLocation, audioInstrumentalPaceStr, instrumentalStretchFilename)
            # stretchInstrumentalCmd = "/usr/local/opt/ffmpeg/bin/ffmpeg -i " + instrumentalClipLocation + \
            #                          " -filter_complex '[0:a]" + audioInstrumentalPaceStr + "[a]' -map " + \
            #               "'[a]' -y " + instrumentalStretchFilename
            """ combines both inputs """
            self.mixVideoWithAudio(combineStretchFilename, instrumentalStretchFilename, finalStretchFilename)
            # finalStretchFilename = combineStretchFilename # REMOVE FOR TESTING
            self.stretchCounter += 1
        else:  # add silence clip when the difference between instrumental and combined clip is too large
            print("PAD VIDEO ID", id)
            if combineClipDuration < lyricDuration:
                self.paddingCounter += 1
                print("CLIP ID %s MIX SILENT CLIP WITH INSTRUMENTAL CUZ COMBINED CLIP IS TOO SHORT! \
                      COMBINED CLIP SIZE %s, LYRIC CLIP SIZE %s " % (id, combineClipDuration, lyricDuration))
                silenceClip = self.addSilence(abs(lyricDuration - combineClipDuration), -1)
                self.padClipWithSilence(silenceClip, videoOrigin, finalStretchFilename, instrumentalClipLocation, id)
            else:
                print("LYRIC DURATION IS LESS THAN VIDEO DURATION !!! INSPECT LYRIC")
        return finalStretchFilename

    def combineVideoClipsIntoSentence(self, wordList, songSnippet, totalsilence, totalsilenceBeginTime, totalsilenceEndTime, lyricItr, id):
        # combine the words into the subtitle in a file called combineClip.mp4
        combinedClipDestination = os.path.join(self.movieLocation, "combineClip/combineClip" + str(id) + ".mp4")
        self.combineVideoClips(wordList, combinedClipDestination)
        instrumentalClipLocation = os.path.join(self.movieLocation, "instrumentalClip/instrumentalClip" + str(id) + ".mp3")
        self.videoTrimmer.trimAudioSnippet(songSnippet, self.instrumentalLocation, instrumentalClipLocation)
        sentenceFilePath = self.stretchClip(combinedClipDestination, instrumentalClipLocation, id)
        if totalsilence > 0: #   add silence clips until it matches length of lyric
            print("TOTAL SILENT LENGTH IS ", totalsilence)
            silenceVideoName = self.addSilence(totalsilenceEndTime.totalms - totalsilenceBeginTime.totalms, lyricItr)
            # what a mess ...
            instrumentalClipLocation = os.path.join(self.movieLocation,
                                                    "instrumentalClip/instrumentalClipPause" + str(id) + ".mp3")
            outputInstrumentalPath = os.path.join(self.movieLocation,
                                                    "instrumentalClip/outputInstrumentalPath" + str(id) + ".mp4")
            newSentenceFilePath = "stretchedCombineClip/stretchedCombineSilenceClip" + str(id) + ".mp4"
            print("CREATING SILENT CLIP FROM %s to %s" % (totalsilenceBeginTime.timestamp, totalsilenceEndTime.timestamp))
            os.system(
                "/usr/local/opt/ffmpeg/bin/ffmpeg -i " + self.instrumentalLocation + " -ss " + totalsilenceBeginTime.timestamp +
                " -to " + totalsilenceEndTime.timestamp + " -y " + instrumentalClipLocation
            )  # removed -c copy to re-encode
            self.mixVideoWithAudio(silenceVideoName, instrumentalClipLocation, outputInstrumentalPath)
            print("CONFIRM SILENT LENGTH IS", str(self.getFileLengthMs(outputInstrumentalPath)))
            self.combineVideoClips([outputInstrumentalPath, sentenceFilePath], newSentenceFilePath)
            sentenceFilePath = newSentenceFilePath
        return sentenceFilePath

    def assembleVideoClips(self, humanApprovedDictionary, songSnippetList):
        """ IBMDictionary contains movieEntry. key is word, value is a Snippet
            songDictionary contains Snippet. key is word, value is object with start, end times
        """
        id = 0
        lyricItr = 0
        prevLyricTimestamp = Timestamp("00:00:00.0")
        sentenceFileList = []
        totalsilence = 0 # silence between lyrics
        snippetidx = 0
        combinedClips = 0
        self.trimAllSongWord(humanApprovedDictionary) # cut all the word videos
        for songSnippet in songSnippetList:
            if totalsilence == 0:
                longSilenceStartTime = prevLyricTimestamp
            snippetidx += 1
            songLine = songSnippet.subtitle
            lyricEndTime = songSnippet.endTime
            wordList = []
            """ the length of silence is measured as the gap between the last subtitle end time and the current start time """
            prevLyricTimestamp = lyricEndTime
            lyricItr += 1  # track the first word found in IBMDictionary for silence timestamp duration calculation
            if len(songLine) > 0: #  takes care of empty song lines
                """ trim all song words belonging to a song line"""
                wordList = self.getSongWordLocations(wordList, songLine)
                if len(wordList) > 0: # words added to wordList. If couldn't find any words in line, replace with silence clip
                    combinedClips += 1
                    sentenceFilePath = self.combineVideoClipsIntoSentence(wordList, songSnippet, totalsilence, longSilenceStartTime, songSnippet.beginTime, lyricItr, id)
                    sentenceFileList.append(sentenceFilePath)
                    totalsilence = 0
                else: # songline contains words, but we couldn't find any from our speaker
                    totalsilence += songSnippet.endTime.totalms - songSnippet.beginTime.totalms
                id += 1
            else: # songline doesnt contain words
                totalsilence += songSnippet.endTime.totalms - songSnippet.beginTime.totalms

            # Delete combineClip.mp4 afterward
        parodyPath = os.path.join("finalVideo", self.speaker + "_" + self.songTitle + ".mp4")
        self.combineVideoClips(sentenceFileList, parodyPath)