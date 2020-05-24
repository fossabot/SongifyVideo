from Timestamp import Timestamp
from Snippet import VideoSnippet
import json

class FileCourier(object):
    @staticmethod
    def readDictionaryListOfObjects(file):
        " get VideoSnippets from serialized pruned movie dictionary "
        if len(file) == 0:
            return {}
        snippetDictionary = eval(file)
        for key in snippetDictionary:
            serializedMovieEntryList = snippetDictionary[key] # get list of arguments to VideoSnippet
            snippetDictionary[key] = []
            for serializedMovieEntry in serializedMovieEntryList:
                beginTime = Timestamp(serializedMovieEntry[0])
                endTime = Timestamp(serializedMovieEntry[1])
                word = serializedMovieEntry[2]
                path = serializedMovieEntry[3]
                movieName = serializedMovieEntry[4]
                parentFilePath = serializedMovieEntry[5]
                parentBeginTime = Timestamp(serializedMovieEntry[6])
                parentEndTime = Timestamp(serializedMovieEntry[7])
                snippetDictionary[key].append(VideoSnippet(beginTime, endTime, word, path, movieName, parentFilePath, parentBeginTime, parentEndTime))
        return snippetDictionary

    @staticmethod
    def writeToSongStatList(songStat_Filename, song_file, foundWordPct):
        with open(songStat_Filename, 'a+') as f:
            f.write('\n{:20s}{:4.3f}'.format(song_file[6:], foundWordPct))
            f.close()

    @staticmethod
    def readList(file):
        """ read and evaluate list stored as string """
        with open(file, "r") as f:
            f.seek(0)
            l = f.read()
            f.close()
            return eval(l)

    @staticmethod
    def readDictionaryObjects(file):
        " get VideoSnippets from serialized pruned movie dictionary "
        if len(file) == 0:
            return {}
        snippetDictionary = eval(file)
        for key in snippetDictionary:
            serializedMovieEntry = snippetDictionary[key] # get list of arguments to VideoSnippet
            beginTime = Timestamp(serializedMovieEntry[0])
            endTime = Timestamp(serializedMovieEntry[1])
            word = serializedMovieEntry[2]
            path = serializedMovieEntry[3]
            movieName = serializedMovieEntry[4]
            parentFilePath = serializedMovieEntry[5]
            parentBeginTime = Timestamp(serializedMovieEntry[6])
            parentEndTime = Timestamp(serializedMovieEntry[7])
            snippetDictionary[key] = VideoSnippet(beginTime, endTime, word, path, movieName, parentFilePath, parentBeginTime, parentEndTime)
        return snippetDictionary

    @staticmethod
    def writeDictionaryListOfObjects(file, snippetListDictionary):
        serializableDictionary = {}
        for key in snippetListDictionary:
            videoSnippetList = snippetListDictionary[key]
            serializedVideoSnippetList = []
            for videoSnippet in videoSnippetList:
                cerealVideo = videoSnippet.serialize()
                serializedVideoSnippetList.append(cerealVideo)
            serializableDictionary[key] = serializedVideoSnippetList
        with open(file, "w") as f:
            f.write(json.dumps(serializableDictionary))
            f.close()

    @staticmethod
    def writeList(file, list):
        with open(file, "w") as f:
            f.write(str(list))
            f.close()
