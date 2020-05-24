import re

class Cleanser(object):

    @staticmethod
    def clean_sentence(dirty_sentence):
        """ clean up song subtitle. dirtysentence is an array of words """
        clean_sentence = []
        for word in dirty_sentence:
            clean_sentence.append(Cleanser.cleaning_word(word))
        return clean_sentence

    @staticmethod
    def cleaning_word(dirty_word):
        clean_wd = "".join(c for c in dirty_word if c.isalpha()).lower() #  only keeps letters
        return clean_wd

    @staticmethod
    def hasLetters(word_array):
        for word in word_array:
            wordHasLetters = bool(re.search('[a-zA-Z]', word))
            if wordHasLetters:
                return True
        return False

    @staticmethod
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext