'''
相似度计算模块
使用算法:TF-IDF(启用) || LSI模型(暂不使用)
@:param artical_directory[文章分词列表文件夹路径](dev)
@:param redis_daatabase[文章分词列表redis](prod)
by: Junyi
'''
import os
from artical_handler import ArticalHandler
from word_segmenter import WordSegmenter
from gensim import corpora, models, similarities


#  接收 word_segmenter.py 分词得到的词语列表，运用gensim建立所有文档的公共词库
#  运用 SimilarityCalculator.get_docs_TFIDF_similarities()即可得到每一个文档与其他文档之间的相似度的迭代器


class SimilarityCalculator(object):

    def __init__(self, artical_directory):
        self.docs_words = []
        self.artical_directory = artical_directory
        self.artical_handler = ArticalHandler(artical_directory=self.artical_directory)
        self.word_segmenter = WordSegmenter()
        self.get_docs_words()

    # 读取所有文档的分词词组列表(从本地硬盘读出(开发时),从redis数据库读出(部署时))
    def get_docs_words(self):
        self.docs_words = []
        for artical in self.artical_handler.get_artical_generators():
            artical_separated = self.word_segmenter.separate_artical_for_calculate(artical)     # dev
            # artical_separated = self.word_segmenter.read_from_redis_for_calculate()           # prod
            self.docs_words.append(artical_separated)
        return self.docs_words

    # 建立语料特征索引字典
    def get_docs_corpus(self):
        dictionary = corpora.Dictionary(self.docs_words)
        for doc_words in self.docs_words:
            yield dictionary.doc2bow(doc_words)

    # 生成所有文档的TFIDF模型
    def get_docs_TFIDF_model(self):
        TFIDF_model = models.TfidfModel(self.get_docs_corpus())
        return TFIDF_model

    # 生成所有文档的LSI模型(未启用)
    def get_docs_LSI_model(self):
        LSI_model = models.LsiModel(corpus=self.get_docs_corpus(),
                                    id2word=corpora.Dictionary(self.docs_words),
                                    num_topics=2)
        return LSI_model

    # 得到每篇doc对应和其他doc的TF-IDF相似度
    def get_docs_TFIDF_similarities(self):
        docs_corpus = self.get_docs_corpus
        TFIDF_model = self.get_docs_TFIDF_model()
        # 初始化一个相似度计算的对象[可用save()序列化保存到本地]
        TFIDF_similarity_calculator = similarities.MatrixSimilarity(corpus=list(TFIDF_model[docs_corpus()]))
        for doc_vectors in docs_corpus():
            doc_similarities = list(enumerate(TFIDF_similarity_calculator[TFIDF_model[doc_vectors]]))
            yield self.prettify(doc_similarities)

    # 得到每篇doc对应和其他doc的LSI相似度
    def get_docs_LSI_similarities(self):
        pass

    @staticmethod
    def prettify(doc_similarities):
        pretty_doc_similarities = []
        for each_similarity in doc_similarities:
            data = {
                'index':each_similarity[0],
                'similarity':'%.2f'%(each_similarity[1]*100)
            }
            pretty_doc_similarities.append(data)
        return pretty_doc_similarities



if __name__ == '__main__':
    sc = SimilarityCalculator(artical_directory=os.path.join(os.path.abspath("."), "test_doc"))
    sc.get_docs_words()
    for doc in sc.get_docs_TFIDF_similarities():
        for i in doc:
            print(i)
        print('----------------------------------')