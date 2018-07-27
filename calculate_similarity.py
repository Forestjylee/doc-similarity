'''
相似度计算模块
@:param artical_separated[文章分词列表]
by: Junyi
'''

#TODO  接收 word_segmenter.py 分词得到的词语列表，运用算法进行两篇文章的相似度计算


class SimilarityCalculator(object):

    def __init__(self, artical_one, artical_two):
        self.artical_one = artical_one
        self.artical_two = artical_two
