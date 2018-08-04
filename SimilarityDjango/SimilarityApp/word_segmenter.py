'''
按照段落进行分词
@:param  artical_generator
@:param  stop_word_path
by: Junyi
'''
import jieba as jb
import redis

# save_to_redis(部署时)将分词的结果保存至redis数据库

class WordSegmenter(object):

    def __init__(self, stop_word_path="stopWords.txt"):
        self.redis_handler = redis.Redis(host='localhost', port=6379, db=5)
        self.stop_word_path = stop_word_path
        self.stop_word_list = self.get_stop_word_list(self.stop_word_path)
        self.extend_word_list = [' ', '\xa0', '\n', '\t']    # 一些无法列在stopWords.txt中的停用词

    def get_stop_word_list(self, stop_word_path):
        stop_word_list = [line.strip() for line in open(self.stop_word_path, encoding='UTF-8').readlines()]
        return stop_word_list

    def separate_text(self, text):
        text_seperated = jb.lcut(text)
        return [word for word in text_seperated if word not in self.extend_word_list]

    def filter_stop_word(self, text):
        text_ = [word for word in text if word not in self.stop_word_list]
        return text_

    def separate_artical_for_calculate(self, artical_generator, filter_stop_word=True):
        artical_separated = []
        for paragraph in artical_generator:
            text_separated = self.separate_text(paragraph)
            if filter_stop_word:
                text_separated= self.filter_stop_word(text_separated)
            if text_separated:
                artical_separated.extend(text_separated)
        return artical_separated

    # 将分词后的列表保存至redis数据库
    def save_to_redis(self, artical_name, artical_separated):
        try:
            self.redis_handler.set(name=artical_name, value=str(artical_separated))
            return True
        except Exception as e:
            return False

    # 从Redis数据库中取出文章对应的分词列表
    def read_from_redis_for_calculate(self, artical_name):
        artical_separated = self.redis_handler.get(name=artical_name)
        return eval(artical_separated)

    # 判断一个元素是否存在redis表中
    def is_in_redis(self, artical_name):
        return self.redis_handler.exists(name=artical_name)
