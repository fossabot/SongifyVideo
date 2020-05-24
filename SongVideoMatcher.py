import Cleanser
import random
import os
from Timestamp import Timestamp
from Snippet import VideoSnippet, SongSnippet
from FileCourier import FileCourier

class SongVideoMatcher:

    def __init__(self, songName, movieLocation, movieNameList, speaker):
        self.matchCount = 10
        self.speaker = speaker
        self.songName = songName
        self.movieLocation = movieLocation
        self.movieNameList = movieNameList
        self.songSubtitleList = []
        self.songWordList = []
        self.videoDictionary = {}
        self.prunedVideoDictionary = {}  # contains only the words relevant to the song
        self.songSnippetList = []
        self.snippets = [] # only include unique words to reuse repeated words and save processing time
        self.songName = songName
        self.songStateFilename = "songs/songStatsList"

    def convertVideoToAudio(self):
        """ write movie video to mp3 format for future transcription"""
        for movieName in self.movieNameList:
            audio_destination = os.path.join(self.movieLocation, self.speaker, movieName, movieName + ".mp3")
            video_origin = os.path.join(self.movieLocation, self.speaker, movieName, ".mp4")
            os.system(
                "/usr/local/opt/ffmpeg/bin/ffmpeg -i " + video_origin + " " + audio_destination
            )

    def scrapeSubtitles(self, IBM_Dictionary, matchCount):
        try:
            self.matchCount = int(matchCount)
        except ValueError:
            print("you did not enter a valid number for match count. Defaulting to 10.")
        ''' scrape the movies first '''
        self.savedWordSnippetDict = IBM_Dictionary
        for movie in self.movieNameList:
            movieSubtitlePath = os.path.join(self.speaker, movie, movie + ".srt")
            self.getWordFromSRT(movieSubtitlePath, movie) # save movie subtitles
        self.getWordFromSRT(self.songName + ".srt", "", True) # save song subtitles
        return self.songSnippetList

    def extractTimestamp(self, timestamp):
        # 00: 00:40, 125 --> 00: 00:44, 170
        timestamp = timestamp.replace(" ", "")
        timestamp = timestamp.replace(",", ".")
        times = timestamp.split("-->")
        beginTime = times[0]
        endTime = times[1].rstrip()
        beginTS = Timestamp(beginTime)
        endTS = Timestamp(endTime)
        return beginTS, endTS

    def getWordFromSRT(self, subtitle_path, dirName, isSong = False):
        """ map words to Snippets (contain timestamps of sentences the word is contained in) """
        # read file line by line
        arrowCounter = 0 #  number of snippets
        subtitle_file = open(subtitle_path, "r", errors='ignore')
        lines = subtitle_file.readlines()
        song_snippet_word_array = [] #  store the words for multiple lines belonging to 1 subtitle
        subtitle_file.close()
        prevEndTimestamp = prevprevEndTimestamp = prevBeginTimestamp = None # combine lyrics with the previous timestamp (not the next one)
        for l in range(len(lines)): # iterate through the lines of the SRT file
            line = lines[l]
            line = Cleanser.Cleanser.cleanhtml(line) # remove html tags
            if "-->" in line or l == len(lines) - 1: #  if last lines add last snippet to list
                if arrowCounter == 1:
                    prevBeginTimestamp = Timestamp("00:00:00.0")
                arrowCounter += 1
                if l == len(lines) - 1:
                    song_snippet_word_array += line.rstrip().split()
                    self.saveSubtitleWords(song_snippet_word_array, dirName, prevBeginTimestamp, prevEndTimestamp, isSong)
                if isSong:
                    if prevEndTimestamp is not None: # len(song_snippet_word_array) > 0: # Cleanser.Cleanser.hasLetters(song_snippet_word_array)
                        clean_word_array = Cleanser.Cleanser.clean_sentence(song_snippet_word_array)
                        # song SRT subtitle length to be used in VideoAssembler for stretching/shrinking clips
                        if prevprevEndTimestamp is not None:
                            self.songSnippetList.append(SongSnippet(prevprevEndTimestamp, prevEndTimestamp, clean_word_array)) # include the pause between lyrics in a snippet
                        else:
                            self.songSnippetList.append(SongSnippet(prevBeginTimestamp, prevEndTimestamp, clean_word_array))
                    prevprevEndTimestamp = prevEndTimestamp
                song_snippet_word_array = []
                if l != len(lines) - 1:
                    prevBeginTimestamp, prevEndTimestamp = self.extractTimestamp(line)
                continue
            word_array = line.rstrip().split() # remove \n at end of sentence
            song_snippet_word_array += word_array
            self.saveSubtitleWords(word_array, dirName, prevBeginTimestamp, prevEndTimestamp, isSong)

    def saveSubtitleWords(self, subtitlewords, dirName, prevBeginTimestamp, prevEndTimestamp, isSong):
        for word in subtitlewords:
            cleaner_word = Cleanser.Cleanser.cleaning_word(word)
            if Cleanser.Cleanser.hasLetters(cleaner_word):  # dont add empty strings
                if isSong:
                    self.songWordList.append(cleaner_word)
                else:
                    # save matches as Video Snippet objects
                    subtitleSnippet = VideoSnippet(prevBeginTimestamp, prevEndTimestamp, cleaner_word, "", dirName)
                    # compare against IBM DICTIONARY FOR ENTRY CLEANER_WORD
                    if cleaner_word in self.savedWordSnippetDict:
                        isIdentical = subtitleSnippet.isIdentical(self.savedWordSnippetDict[cleaner_word])
                        if isIdentical:
                            # print("DOOP ALERT! Dont add subtitle containing word %s to dictionary because already included in IBM Dictionary" % cleaner_word)
                            continue
                    if cleaner_word not in self.videoDictionary:
                        subtitleSnippet.path = os.path.join(self.movieLocation, self.speaker, "subtitleAudio",
                                            cleaner_word + str(0) + ".mp3")
                        self.videoDictionary[cleaner_word] = [subtitleSnippet]
                    else:
                        if len(self.videoDictionary[cleaner_word]) < self.matchCount:  # limit to 10 matches
                            subtitleSnippet.path = os.path.join(self.movieLocation, self.speaker, "subtitleAudio",
                                                cleaner_word + str(len(self.videoDictionary[cleaner_word])) + ".mp3")
                            self.videoDictionary[cleaner_word].append(subtitleSnippet)

    def matchVideoWithSong(self):
        """ iterate over the song lyrics, find matches with subtitle
            return a list of Snippet (beginTS, endTS, subtitle) from movies
        """
        total_word = 0
        found_word_count = 0
        incomplete_song = ""
        unfound_word_set = set()
        print(self.songWordList)
        wordSet = set(self.songWordList)
        for word in wordSet:
            if word in self.videoDictionary:
                found_word_count += 1
                incomplete_song += word + " "
                videoSnippetList = self.videoDictionary[word] # [randSnippet]  # later choose random
                self.prunedVideoDictionary[word] = videoSnippetList
                for videoSnippet in videoSnippetList: # same word, multiple matches in the movie
                    # filter word
                    self.snippets.append(videoSnippet)
            else:
                unfound_word_set.add(word)
            total_word += 1
        if total_word > 0:
            found_word_pct = found_word_count / total_word
        FileCourier.writeToSongStatList(self.songStateFilename, self.songName, found_word_pct)
        print("found word percentage is ", found_word_pct)
        print("unique words", len(self.prunedVideoDictionary))
        print("couldn't find these words: " + str(unfound_word_set))
        print("incomplete song is: \n", incomplete_song)
        transcribe = input("would you like to transcribe this song? (Y/N)")
        ''' check if the found word percentage is high enough '''
        return self.prunedVideoDictionary, transcribe, found_word_pct