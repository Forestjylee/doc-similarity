'''
相似度计算模块
使用算法:TF-IDF(启用) || LSI模型(暂不使用)
@:param artical_directory[文章分词列表文件夹路径](dev|prod快速计算时)
@:param redis_daatabase[文章分词列表redis](prod)√
by: Junyi
'''
import os
from .artical_handler import ArticalHandler
from .word_segmenter import WordSegmenter
from gensim import corpora, models, similarities


#  接收 word_segmenter.py 分词得到的词语列表，运用gensim建立所有文档的公共词库
#  运用 SimilarityCalculator.get_docs_TFIDF_similarities()即可得到每一个文档与其他文档之间的相似度的迭代器


class SimilarityCalculator(object):

    def __init__(self, artical_directory, project_name=None, module_name=None, is_quick=False):
        self.artical_directory = artical_directory
        self.docs_words = []
        self.is_quick = is_quick
        self.word_segmenter = WordSegmenter()
        self.artical_handler = ArticalHandler(artical_directory)
        if not is_quick:     # 非快速计算时
            self.project_name = project_name
            self.module_name = module_name
            self.redis_key_list = self.get_redis_key_list()
            self.set_docs_words()
        else:
            self.artical_name_list = self.get_artical_name_list()
            self.set_docs_words_quick()

    def get_redis_key_list(self):
        try:
            redis_key_list = []
            student_list = os.listdir(self.artical_directory)
            for student_info in student_list:
                doc_directory = os.path.join(os.path.join(self.artical_directory, student_info),'docs')
                if not self.is_empty(doc_directory):
                    redis_key = '{}-{}-{}'.format(student_info, self.project_name, self.module_name)
                    redis_key_list.append(redis_key)
            return redis_key_list
        except:
            raise FileNotFoundError

    # 从文件夹路径中获取文件名
    def get_artical_name_list(self):
        try:
            artical_name_list = os.listdir(self.artical_directory)
            return artical_name_list
        except:
            raise FileNotFoundError

    # 读取所有文档的分词词组列表(从redis数据库读出)[提交式项目]
    def set_docs_words(self):
        self.docs_words = []
        for redis_key in self.redis_key_list:
            artical_separated = self.word_segmenter.read_from_redis_for_calculate(redis_key=redis_key)           # prod
            self.docs_words.append(artical_separated)

    # 从本地硬盘读取文章然后分词, 用于快速计算模块[快速计算]
    def set_docs_words_quick(self):
        self.docs_words = []
        for artical in self.artical_handler.get_artical_generators():
            artical_separated = self.word_segmenter.separate_artical_for_calculate(artical)
            self.docs_words.append(artical_separated)

    # 建立语料特征索引字典
    def get_docs_corpus(self):
        dictionary = corpora.Dictionary(self.docs_words)
        for doc_words in self.docs_words:
            yield dictionary.doc2bow(doc_words)

    # 生成所有文档的TFIDF模型
    def get_docs_TFIDF_model(self):
        TFIDF_model = models.TfidfModel(self.get_docs_corpus())
        return TFIDF_model

    # 得到每篇doc对应和其他doc的TF-IDF相似度
    def get_docs_TFIDF_similarities(self):
        docs_corpus = self.get_docs_corpus
        TFIDF_model = self.get_docs_TFIDF_model()
        # 初始化一个相似度计算的对象[可用save()序列化保存到本地]
        TFIDF_similarity_calculator = similarities.MatrixSimilarity(corpus=list(TFIDF_model[docs_corpus()]))
        for doc_vectors in docs_corpus():
            doc_similarities = list(enumerate(TFIDF_similarity_calculator[TFIDF_model[doc_vectors]]))
            yield doc_similarities

    # 生成所有文档的LSI模型(未启用)
    def get_docs_LSI_model(self):
        LSI_model = models.LsiModel(corpus=self.get_docs_corpus(),
                                    id2word=corpora.Dictionary(self.docs_words),
                                    num_topics=2)
        return LSI_model

    # 得到每篇doc对应和其他doc的LSI相似度(未启用)
    def get_docs_LSI_similarities(self):
        pass

    # 美化输出格式
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

    # 获取相似度前200的文档信息(快速计算/提交式项目)[通过self.is_quick来区分两者]
    def get_top_200(self):
        similarity_list = []
        if not self.is_quick:
            name_list = self.redis_key_list
        else:
            name_list = self.artical_name_list
        list_len = len(name_list)
        for index, doc in enumerate(self.get_docs_TFIDF_similarities()):
            for i in range(index+1, list_len):
                if not self.is_quick:
                    doc_A_info = name_list[index]
                    doc_B_info = name_list[doc[i][0]]
                    item = {
                        'doc_A':doc_A_info,
                        'doc_A_directory':('-').join(doc_A_info.split('-')[:2]),
                        'doc_B':name_list[doc[i][0]],
                        'doc_B_directory':('-').join(doc_B_info.split('-')[:2]),
                        'similarity':round(doc[i][1]*100, 3),    # 保留三位小数
                    }
                else:   # TODO 学生信息
                    item = {
                        'doc_A':name_list[index],
                        'doc_B':name_list[doc[i][0]],
                        'similarity':round(doc[i][1]*100, 3)    # 保留三位小数
                    }
                similarity_list.append(item)
        # 只取前200
        try:
            top_200 = sorted(similarity_list, key=lambda x:x['similarity'], reverse=True)[:201]
        except:
            top_200 = sorted(similarity_list, key=lambda x:x['similarity'], reverse=True)
        return top_200

    # 判断目录是否为空
    @staticmethod
    def is_empty(directory_path):
        try:
            if not os.listdir(directory_path):
                return True
            else:
                return False
        except:
            return True
