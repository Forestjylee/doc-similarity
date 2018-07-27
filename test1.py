from artical_handler import ArticalHandler
from word_segmenter import WordSegmenter

if __name__ == '__main__':
    aritical_ = ArticalHandler(artical_path="test.docx")
    segmenter_ = WordSegmenter()
    print(segmenter_.separate_artical(artical_generator=aritical_.get_words(), filter_stop_word=True))