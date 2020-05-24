class Timestamp(object):
    def __init__(self, timestampString = None):
        if timestampString is not None:
            self.formatTimestamp(timestampString)

    def formatTimestamp(self, timestamp):
        self.timestamp = timestamp.replace(",", ".")
        parseTimestamp = self.timestamp.replace(".", ":")
        timeSplit = parseTimestamp.split(":") # HH:MM:SS:mm
        self.hour = int(timeSplit[0])
        self.min = int(timeSplit[1])
        self.sec = int(timeSplit[2])
        self.ms = int(float("." + timeSplit[3]) * 1000) # expressed as a fraction of a second
        self.totalms = self.calculateTotalMs(self.hour, self.min, self.sec, self.ms)

    def calculateTotalMs(self, hour, min, sec, ms):
        return hour * 3600000 + min * 60000 + sec * 1000 + ms

    def stringifyTimestamp(self, hour, min, sec, ms):
        """ after an operation, stringify the timestamp """
        strHour = str(hour).zfill(2)
        strMin = str(min).zfill(2)
        strSec = str(sec).zfill(2)
        strMs = str(ms / 1000).split(".")[1]
        stringStamp = strHour + ":" + strMin + ":" + strSec + "." + strMs
        return stringStamp

    def findDuration(self, nextTimestamp):
        """ get duration in millisconds between this timestamp and nextTimestamp """
        elapsedMs = nextTimestamp.totalms - self.totalms
        return abs(elapsedMs)
        # durationTimestamp = self.stringifyTimestamp(hour, min, sec, ms)
        # return durationTimestamp

    def convertDurationToTimestamp(self, nextTimestamp):
        msElapsed = self.findDuration(nextTimestamp)
        hour, min, sec, ms = self.convertTotalMsToTimestamp(msElapsed)
        return self.stringifyTimestamp(hour, min, sec, ms)

    def addTimestamp(self, offset, modify=False):
        """ add offset to timestamp. Dont modify this object """
        if modify:
            self.totalms += offset
            self.hour, self.min, self.sec, self.ms =  self.convertTotalMsToTimestamp(self.totalms)
            self.timestamp = self.stringifyTimestamp(self.hour, self.min, self.sec, self.ms)
            return self.timestamp
        else:
            hour, min, sec, ms = self.convertTotalMsToTimestamp(self.totalms + offset)
            timestamp = self.stringifyTimestamp(hour, min, sec, ms) # return new timestamp
            return timestamp

    def convertTotalMsToTimestamp(self, totalms):
        totalms = abs(totalms)
        hour = int(totalms / 3600000)
        totalms = totalms % 3600000
        min = int(totalms / 60000)
        totalms = totalms % 60000
        sec = int(totalms / 1000)
        ms = (totalms % 1000)
        return hour, min, sec, ms

    def convertTotalMsToString(self, totalms):
        self.hour, self.min, self.sec, self.ms = self.convertTotalMsToTimestamp(totalms)
        self.timestamp = self.stringifyTimestamp(self.hour, self.min, self.sec, self.ms)
        return self.timestamp