import os

class AudioFX:

    @staticmethod
    def lowerVolumeBy50(wordSnippet):
        wordSnippet.volume *= 0.5
        output_file = wordSnippet.modifyPath("quiet")
        cmd = "/usr/local/opt/ffmpeg/bin/ffmpeg -i " + wordSnippet.path + " -filter:a 'volume=0.5' -y " + output_file
        os.system(cmd)
        wordSnippet.path = output_file

    @staticmethod
    def raiseVolumeBy50(wordSnippet):
        wordSnippet.volume *= 2.0
        output_file = wordSnippet.modifyPath("loud")
        cmd = "/usr/local/opt/ffmpeg/bin/ffmpeg -i " + wordSnippet.path + " -filter:a 'volume=2.0' -y " + output_file
        os.system(cmd)
        wordSnippet.path = output_file

    @staticmethod
    def speedUpBy50(wordSnippet):
        if wordSnippet.speed * 2 <= 4.0:
            wordSnippet.speed *= 2.0
            print("make word snippet path %s faster. Speed is %s " % (wordSnippet.path, wordSnippet.speed))
            output_file = wordSnippet.modifyPath("fast")
            cmd = "/usr/local/opt/ffmpeg/bin/ffmpeg -i " + wordSnippet.path + " -filter:a 'atempo=2.0' -vn -y " + output_file
            os.system(cmd)
            wordSnippet.path = output_file
        else:
            print("ERROR can't speed video up more than 4.0")

    @staticmethod
    def slowDownBy50(wordSnippet):
        if wordSnippet.speed * 0.5 >= 0.25:
            wordSnippet.speed *= 0.5
            print("make word snippet path %s slower. Speed is %s " % (wordSnippet.path, wordSnippet.speed))
            output_file = wordSnippet.modifyPath("slow")
            cmd = "/usr/local/opt/ffmpeg/bin/ffmpeg -i " + wordSnippet.path + " -filter:a 'atempo=0.5' -vn -y " + output_file
            os.system(cmd)
            wordSnippet.path = output_file
        else:
            print("ERROR can't slow video up factor of 4.0")