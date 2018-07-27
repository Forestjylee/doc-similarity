import jieba as jb

'''
按照段落进行分词
@:param  artical_generator
@:param  stop_word_path
by: Junyi
'''

class WordSegmenter(object):

    def __init__(self, stop_word_path="stopWords.txt"):
        self.stop_word_path = stop_word_path
        self.stop_word_list = self.get_stop_word_list(self.stop_word_path)

    def get_stop_word_list(self, stop_word_path):
        stop_word_list = [line.strip() for line in open(self.stop_word_path, encoding='UTF-8').readlines()]
        return stop_word_list

    def separate_text(self, text):
        text_seperated = jb.lcut(text)
        return [word for word in text_seperated if word not in [' ', '\n', '\xa0']]

    def filter_stop_word(self, text):
        text_ = list(set(text) - set(self.stop_word_list))
        return text_

    def separate_artical(self, artical_generator, filter_stop_word=True):
        artical_separated = []
        for paragraph in artical_generator:
            text_separated = self.separate_text(paragraph)
            if filter_stop_word:
                text_separated= self.filter_stop_word(text_separated)
            if text_separated:
                artical_separated.append(text_separated)
        return artical_separated
