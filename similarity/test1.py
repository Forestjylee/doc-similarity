from similarity.artical_handler import ArticalHandler
from similarity.word_segmenter import WordSegmenter
import os

if __name__ == '__main__':
    artical_directory = os.path.join(os.path.abspath(".."), "test_doc")
    print(os.listdir(artical_directory))