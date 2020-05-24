class VideoSnippet:
    def __init__(self, beginTime, endTime, word, path, movieName, parentPath=None, parentStart=None, parentEnd=None):
        self.beginTime = beginTime
        self.endTime = endTime
        self.word = word
        self.path = path
        self.originalPath = path # for reverting changes made during human approval
        self.movieName = movieName
        self.parentPath = parentPath
        self.parentBeginTime = parentStart
        self.parentEndTime = parentEnd
        self.id = self.getId() # for comparing word snippets
        self.volume = 1.0 # normal volume
        self.speed = 1.0

    def modifyPath(self, word):
        for i in range(len(self.path)-1, 0, -1):
            if self.path[i]=="/":
                path = self.path[:i+1] + word + self.path[i+1:]
                print(path)
                return path

    def getId(self):
        if self.parentBeginTime is not None:
            return self.movieName + " " + self.parentBeginTime.timestamp + " " + self.parentEndTime.timestamp
        else: # for subtitle snippets (no parent attribute)
           return self.movieName + " " + self.beginTime.timestamp + " " + self.endTime.timestamp

    """ serialize the Word Snippets """
    def serialize(self):
        return [self.beginTime.timestamp, self.endTime.timestamp, self.word, self.path, self.movieName, self.parentPath, self.parentBeginTime.timestamp, self.parentEndTime.timestamp]

    def isIdentical(self, videoSnippetList):
        """ check if the same snippet has been saved to IBM dictionary """
        for videoSnippet in videoSnippetList:
            if self.id == videoSnippet.id:
                # print("identical videoSnippet found, dont add to IBM dictionary")
                return True
        return False

class SongSnippet:
    def __init__(self, beginTime, endTime, subtitle):
        self.beginTime = beginTime
        self.endTime = endTime
        self.subtitle = subtitle