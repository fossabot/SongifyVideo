import os

def deleteMp3Files(movieNameList, speaker):
    for videoFolder in movieNameList:
        wordAudioFilename = speaker + "/" + videoFolder + "/wordAudio"
        # subtitleAudioFilename = speaker + "/" + videoFolder + "/subtitleAudio" # SUBTITLES REUSED IN IBM_DICTIONARY
        # subtitleAudioFileList = [f for f in os.listdir(subtitleAudioFilename)]
        wordAudioFileList = [f for f in os.listdir(wordAudioFilename)]
        for f in wordAudioFileList:
            os.remove(os.path.join(wordAudioFilename, f))
        # for f in subtitleAudioFileList:
        #     os.remove(os.path.join(subtitleAudioFilename, f))


def moveFiles():
    baseDir = "/Users/edwardcox/Desktop/TomCruiseSing/Trump"
    trumpdir = os.listdir("/Users/edwardcox/Desktop/TomCruiseSing/Trump")
    for trump in trumpdir:
        if trump[:5] == "trump":
            subPath = os.path.join(baseDir, trump, "subtitleAudio")
            wordPath = os.path.join(baseDir, trump, "wordAudio")
            subContent = os.listdir(subPath)
            wordContent = os.listdir(wordPath)
            for sub in subContent:
                fullSubPath = os.path.join(baseDir, subPath, sub)
                newSubPath = os.path.join(baseDir, "subtitleAudio", sub)
                os.rename(fullSubPath, newSubPath)
            for word in wordContent:
                fullWordPath = os.path.join(baseDir, wordPath, word)
                newWordPath = os.path.join(baseDir, "wordAudio", word)
                os.rename(fullWordPath, newWordPath)