import Cleanser
import os
import re

class VideoTrimmer:
    def __init__(self, movieLocation, speaker):
        self.movieLocation = movieLocation
        self.speaker = speaker

    def extractWord(self, snippetName):
        ''' extract word portion of id '''
        endIdx = len(snippetName)
        for i in range(len(snippetName)):
            character = snippetName[i]
            if character.isdigit():
                endIdx = i
                break
        return snippetName[:endIdx]

    def trimVideoSnippetList(self, videoSnippetList, exhaustedWordSet, previouslyApprovedList):
        """ write trimmed video and audio to disk for IBM transcription
            input: a list of Snippets
        """
        doopList = set() # dont repeat trim same word
        for videoSnippet in videoSnippetList:
            if videoSnippet.word not in exhaustedWordSet and videoSnippet.word not in previouslyApprovedList:
                audio_origin = os.path.join(self.movieLocation, self.speaker, videoSnippet.movieName, videoSnippet.movieName + ".mp3")
                self.trimVideoSnippet(videoSnippet, audio_origin, videoSnippet.path)

    def adjustSnippetTimestamp(self, videoSnippet, leftAdjust, rightAdjust):
        videoSnippet.beginTime.addTimestamp(leftAdjust, modify=True)
        videoSnippet.endTime.addTimestamp(rightAdjust, modify=True)

    def trimAudioSnippet(self, videoSnippet, audio_origin, audio_destination):
        start_timestamp = videoSnippet.beginTime.timestamp  # Snippet object
        end_timestamp = videoSnippet.endTime.timestamp
        trimcmd = "/usr/local/opt/ffmpeg/bin/ffmpeg -i " + audio_origin + " -ss " + start_timestamp + " -to " + end_timestamp + " -y -c copy " + audio_destination
        os.system(trimcmd)  # removed -c copy to re-encode
        if not os.path.exists(audio_destination):
            print("path does not exist")
            print("start timestamp %s end timestamp %s audio origin %s audio destination %s" % (start_timestamp, end_timestamp, audio_origin, audio_destination))

    def trimVideoSnippet(self, videoSnippet, audio_origin, audio_destination):
        # Requires re-encoding for audio-video sync
        start_timestamp = videoSnippet.beginTime.timestamp  # Snippet object
        end_timestamp = videoSnippet.endTime.timestamp
        trimcmd = "/usr/local/opt/ffmpeg/bin/ffmpeg -i " + audio_origin + " -ss " + start_timestamp + " -to " + end_timestamp + " -y " + audio_destination
        os.system(trimcmd)  # removed -c copy to re-encode
        print(trimcmd)

        if not os.path.exists(audio_destination):
            print("path does not exist")
            print("start timestamp %s end timestamp %s audio origin %s audio destination %s" % (start_timestamp, end_timestamp, audio_origin, audio_destination))