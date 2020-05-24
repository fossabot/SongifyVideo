Have you ever wondered what it would be like if Elon Musk sang Justin Bieber and Ariana Grande's hit song "Stuck With You"? 

Well now you can songify your favorite personality with this Python program. Take a look here: https://www.youtube.com/watch?v=twu7Yj8IRxw

Note: This program will need modifications to work on Windows/Ubuntu (the command line commands will differ). It was developed on macOS Mojave and written with Python 3.7

This program uses IBM's AI speech to text service to parse videos for words that match lyrics. However, it also requires a human-in-the-loop to 
for quality control. The good news is unique words only need to be parsed once. 

1) Create an IBM account: https://cloud.ibm.com/login
2) Create an API key for IBM Watson's Speech To Text service (you get 500 minutes for free): https://cloud.ibm.com/catalog/services/speech-to-text
3) In the file SpeechDetector.py, replace 'YOUR_API_KEY' with the API key you generated

The other setup required is gathering videos to parse. This involves getting YouTube video subtitles and mp4 files of your speaker.
My process is like this: 

1) In YouTube search for speeches by your speaker. 
2) For every video, get its subtitle file (https://savesubs.com/) and download its mp4 and mp3 file (https://ytmp3.cc/en13/)
3) Save all 3 files in a directory of the speaker's name (illustrated with 'elon' in my directory tree at bottom)
4) Continue doing this for about 30 videos (so you have plenty of words to choose from)

You will also need to download a silent clip (preferably entertaining) to fill in the awkward pause(s) at the beginning of a music video or in between lyrics. 
Put this file in the silence folder and call it speaker + "swag" eg "elonswag".

Additionally, download the mp3 file for the music video and also the srt of the same music video and put this in the songs folder. 

Make sure you have the following libraries installed: ffmpeg, subprocess, copy, os
If you don't have ffmpeg on a Mac, install using via terminal with "brew install ffmpeg"

Now you can run the program. The program will first trim all subtitles containing the word of interest from the mp4 file you downloaded. This process may take several minutes depending on the song length.
When it is done, you will be prompted via voice to confirm whether IBM transcribed the word correctly. You can make adjustments to the video snippet until you feel it is acceptable or you can skip it. 

After all word matches have been confirmed or skipped, the program will create a mishmash video of your speaker. If you got this far I am very impressed and congragulate you. 

├── AudioFX.py 
├── Cleanser.py
├── Elon
│   ├── elon1
│   │   ├── elon1.mp3
│   │   ├── elon1.mp4
│   │   └── elon1.srt
        ...
│   ├── elon40
│   │   ├── elon40.mp3
│   │   ├── elon40.mp4
│   │   ├── elon40.srt
│   │   └── elon40tore
│   ├── exhaustedWord
│   ├── humanApproveFile
│   ├── movieOrder
│   ├── subtitleAudio
│   │   ├── a0.mp3
        ...
│   │   └── youre9.mp3
│   ├── subtitledVideos
│   ├── unapprovedIBMWord
│   ├── wordAudio
        ...
│   │   └── you69.mp3
│   └── wordVideo
        ...
│       └── yourself.mp4
├── FileCourier.py
├── SingMeCruise.py
├── Snippet.py
├── SongVideoMatcher.py
├── SongifyVideo.py
├── SpeechDetector.py
├── Timestamp.py
├── VideoAssembler.py
├── VideoSelector.py
├── VideoTrimmer.py
├── WaveGenerator.py
├── WordFilter.py
├── __pycache__
│   ├── AudioFX.cpython-37.pyc
│   ├── Cleanser.cpython-37.pyc
│   ├── FileCourier.cpython-37.pyc
│   ├── Snippet.cpython-37.pyc
│   ├── SongVideoMatcher.cpython-37.pyc
│   ├── SpeechDetector.cpython-37.pyc
│   ├── Timestamp.cpython-37.pyc
│   ├── VideoAssembler.cpython-37.pyc
│   ├── VideoTrimmer.cpython-37.pyc
│   └── WaveGenerator.cpython-37.pyc
├── combineClip
        ...
│   ├── combineClip74.mp4
│   └── videoClipLocation.txt
├── finalVideo
│   └── Elon_StuckWithYou.mp4
├── instrumentalClip
        ...
│   └── outputInstrumentalPath73.mp4
├── normalizedClip
│   ├── normalized
        ...
│   └── normalizedyourself.mp4
├── silence
│   ├── elonswag.mp4
│   └── trumpswag.mp4
├── songs
│   ├── StuckWithYou.srt
│   ├── StuckWithYouInstrumental.mp3
│   └── songStatsList
├── stretchedCombineClip
        ...
│   └── stretchedCombineSilenceClip73.mp4
├── testing
        ...
│   └── testing74.mp4
├── thumbnail
│   └── wallemoji.png
└── utility.py
