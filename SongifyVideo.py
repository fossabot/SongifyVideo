from SongVideoMatcher import SongVideoMatcher
from SpeechDetector import SpeechDetector
from VideoTrimmer import VideoTrimmer
from VideoAssembler import VideoAssembler
from FileCourier import FileCourier
import copy
import os

def test_Word_Snippet(songWordVideoSnippet, parentSnippetPath, optionsRemaining):
    """ present the Word Snippet to the HUMAN for final check """
    videoTrimmer.trimVideoSnippet(songWordVideoSnippet, parentSnippetPath, songWordVideoSnippet.path) #  wait until file is written before reading. FFmpeg cannot edit existing files in-place.
    print("parent subtitle path", parentSnippetPath)
    print("there are %s options remainining" % optionsRemaining)
    print("snippet begin time:", songWordVideoSnippet.beginTime.timestamp)
    print("snippet end time:", songWordVideoSnippet.endTime.timestamp)
    try:
        isHumanApproved, adjustLeft, adjustRight = speechDetector.filterIBMWord(songWordVideoSnippet)
    except ValueError:
        isHumanApproved = True
        adjustLeft = adjustRight = -1
    """ while adjustments need to be made to the clip, keep prompting user for input """
    if not isHumanApproved:
        return False
    while adjustLeft != 0 or adjustRight != 0:
        videoTrimmer.adjustSnippetTimestamp(songWordVideoSnippet, adjustLeft, adjustRight)
        videoTrimmer.trimVideoSnippet(songWordVideoSnippet, parentSnippetPath,  # overwrite old file
                                      songWordVideoSnippet.path)
        try:
            isHumanApproved, adjustLeft, adjustRight = speechDetector.filterIBMWord(songWordVideoSnippet)
        except ValueError:
            adjustLeft = adjustRight = -1
            continue
        if not isHumanApproved:  # if after adjusting, still unable to hear the word, don't use word
            return False
    return True

def IBM_Master_Select(videoDictionary, IBM_Dictionary, humanApprovedDictionary, exhaustedWordSet):
    """ IBM transcription part with a human in the loop """
    """ IBM_Dictionary word snippet list is a subset of videoDictionary list. """
    notFoundSet = set()  # contains the words IBM couldn't find in the snippets provided
    foundSet = set()
    totalWordSearched = 0
    while totalWordSearched < len(videoDictionary):
        verifyWordSnippetDictionary = {}
        """ make one pass through all the words in the video dictionary before prompting use for approval """
        print("Finished searching %s words, still have %s words left to search" % (totalWordSearched, len(videoDictionary) - totalWordSearched))
        for word in videoDictionary:
            if word in exhaustedWordSet:
                notFoundSet.add(word)
                continue
            if word not in humanApprovedDictionary and word not in speechDetector.previouslyApprovedList: # haven't found this word yet
                if word in IBM_Dictionary and len(IBM_Dictionary[word]) > 0: #  use saved word snippet
                    print("use word '%s' saved in IBM Dictionary" % word)
                    songWordVideoSnippet = IBM_Dictionary[word].pop(0)  # remove the first element of the video snippet list
                    # Reference by id
                elif len(videoDictionary[word]) > 0: # split scraped subtitle entry into word snippets
                    print("call the IBM AI lords to cull words from this subtitle containing the word '%s'"% word)
                    subtitleSnippet = videoDictionary[word].pop(0)
                    songWordVideoSnippet = speechDetector.splitSentenceToWord(subtitleSnippet)
                    print()
                else:
                    print("word %s is not in human approved dictionary, previously approved list or videoDictionary")
                    continue
                verifyWordSnippetDictionary[word] = songWordVideoSnippet
            else:
                foundSet.add(word)
                print("user already approved word: ", word)
        # alert the user that the words are ready for review
        for word in verifyWordSnippetDictionary:
            print("EXAMINE WORD ", word)
            wordSnippet = verifyWordSnippetDictionary[word]
            if wordSnippet is None:
                print("IBM couldn't find '%s' in video snippet" % word)
            else:
                optionsRemaining = len(videoDictionary[word])
                isHumanApproved = test_Word_Snippet(wordSnippet, wordSnippet.parentPath, optionsRemaining)
                if isHumanApproved:
                    speechDetector.addVerifiedSongWord(wordSnippet)
                    foundSet.add(word)
                    print("successfully verified word %s path is %s" % (word, wordSnippet.path))
            if (word not in IBM_Dictionary or len(IBM_Dictionary[word]) == 0) and len(videoDictionary[word]) == 0 and \
                    word not in humanApprovedDictionary:
                print("exhausted all word matches for the word: '%s'" % word)
                notFoundSet.add(word)
        print("EXIT LOOP VERIFY WORD SNIPPET DICTIONARY")
        totalWordSearched = len(foundSet) + len(notFoundSet)
    #  remove all mp3 from audio folder after verification is over
    # deleteMp3Files()
    exhaustedWordSet |= notFoundSet # combine both sets
    totalApprovedWordList = speechDetector.addVerifiedWordsToList() #  after done verifying, add these finalized words to the set of saved found words
    FileCourier.writeList(human_Approve_Filename, totalApprovedWordList)
    FileCourier.writeList(exhausted_Filename, list(exhaustedWordSet))

def transcribeSong():
    saveIBMFile = open(IBM_Filename, "r") #  r+ mode creates, reads and writes to file
    saveIBMFile.seek(0) # move pointer to the beginning of the file  (OSX bug)
    exhaustedWordList = FileCourier.readList(exhausted_Filename)
    speechDetector.previouslyApprovedList = FileCourier.readList(human_Approve_Filename)
    exhasutedWordSet = set(exhaustedWordList)
    """ to reuse file paths saved in saveIBMFile, always append new videos to the movieNameList (because id are incremented in order)"""
    speechDetector.IBM_Dictionary = FileCourier.readDictionaryListOfObjects(saveIBMFile.read())
    speechDetector.duplicateIBM_Dictionary = copy.deepcopy(speechDetector.IBM_Dictionary)
    speechDetector.initializeIdCounter() # initialize word id by length of IBM dictionary
    # uplist = speechDetector.IBM_Dictionary["up"]
    # speechDetector.isDuplicateDuplicate(speechDetector.IBM_Dictionary["up"][0], speechDetector.IBM_Dictionary["up"][1])
    matchCount = input("How many matches would you like for each word?")
    songSnippetList = songVideoMatcher.scrapeSubtitles(speechDetector.IBM_Dictionary, matchCount) # dont queue up identical subtitles for review
    prunedVideoDictionary, transcribe, foundWordPct = songVideoMatcher.matchVideoWithSong() # check if song is qualified
    if transcribe.lower() != "y":
        return
    videoTrimmer.trimVideoSnippetList(songVideoMatcher.snippets, exhasutedWordSet, speechDetector.previouslyApprovedList)  # cut audio to feed short sentences to IBM DISABLED FOR DEBUGGING
    IBM_Master_Select(prunedVideoDictionary, speechDetector.IBM_Dictionary, speechDetector.humanApprovedDictionary, exhasutedWordSet)  # pass the subtitle snippets parsed from the videos
    """ save all the IBM detected words (including the human approved words) to save computing time in future """
    videoAssembler.assembleVideoClips(speechDetector.humanApprovedDictionary, songSnippetList)

def replaceVideoAudioTrack(movieNameList):
    # not needed anymore
    """ replace the video's audio with audio compressed with Audacity """
    for videoFolder in movieNameList:
        outputVideoFilename = speaker + "/" + videoFolder + "/" + videoFolder + "Compress.mp4"
        videoFilename = speaker + "/" + videoFolder + "/" + videoFolder + ".mp4"
        audioFilename = speaker + "/" + videoFolder + "/" + videoFolder + ".mp3"
        os.system(
            "/usr/local/opt/ffmpeg/bin/ffmpeg -i " + videoFilename + " -i " + audioFilename + " -c:v copy -map 0:v:0 -map 1:a:0 -y " + outputVideoFilename
        )

def getMovieNameList(speaker):
    wordOrderFile = open(os.path.join(speaker, "movieOrder"), "r")
    folderList = eval(wordOrderFile.read())
    wordOrderFile.close()
    vidfolder = []
    for f in folderList:
        folderExists = os.path.exists(os.path.join(speaker, f))
        if folderExists:
            vidfolder.append(f)
    return vidfolder

if __name__ == "__main__":
    speaker = "Elon" # capitalize
    IBM_Filename = os.path.join(speaker, "unapprovedIBMWord")
    exhausted_Filename = os.path.join(speaker, "exhaustedWord")
    human_Approve_Filename = os.path.join(speaker, "humanApproveFile")
    movie_loc = "/Users/edwardcox/Desktop/TomCruiseSing/" # directory of videos to scrape words from

    song_file = "StuckWithYou"
    instrumental_file = "songs/StuckWithUInstrumentalHi.mp3"
    # convertList = ["trump2", "trump4"] # add new videos here to combien compressed audio with video
    # replaceVideoAudioTrack(convertList) # When inserting new speaker videos
    movieNameList = getMovieNameList(speaker)
    videoTrimmer = VideoTrimmer(movie_loc, speaker)
    videoAssembler = VideoAssembler(movie_loc, instrumental_file, videoTrimmer, speaker, song_file)
    speechDetector = SpeechDetector(movie_loc, IBM_Filename, speaker)
    songVideoMatcher = SongVideoMatcher("songs/" + song_file, movie_loc, movieNameList, speaker)
    transcribeSong() # takes a long time
    # moveFiles()
