from similarity.artical_handler import ArticalHandler
from similarity.word_segmenter import WordSegmenter
import os

if __name__ == '__main__':
    list1 = ["你好", "我好"]
    str_list = str(list1)
    list2 = eval(str_list)
    print(type(list2))