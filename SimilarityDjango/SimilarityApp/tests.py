from SimilarityApp.divide_word import WordSegmenter
from SimilarityApp.get_artical import ArticalHandler
# Create your tests here.
if __name__ == '__main__':
    word_s = WordSegmenter()
    sepa = word_s.separate_artical_for_calculate(ArticalHandler.get_words_from_docx('E:\\doc-similarity\\upload_data\\何老师-123456\\测试项目\\测试module\\李俊仪-201630609971\\docs\\第一题.docx'))
    print(sepa)