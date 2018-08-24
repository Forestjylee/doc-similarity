# 文档查重系统

## 一.环境配置

### 1.开发环境: 

### 	编译环境:   Python 3.6.4

### 	web框架:   Django 2.0.5

### 	包管理工具:   Pipenv

### 集成环境:   PyCharm

### 	操作系统:   Windows 10 (64bit)

### 2.工作服务器配置

### 	操作系统:   Ubuntu 16.04

### 	数据库:   MySql 5.7, redis

## 二.项目架构

### 1.文件目录结构:

**doc-similarity(根目录)**

│  
├─SimilarityDjango
    ├─similarity
    │  └─test_doc
    │  
    ├─SimilarityApp
    │  ├─migrations
    │  └─templates
    │         └─SimilarityApp
    │  
    ├─SimilarityDjango
     │  
    └─static
     │ ├─css
     │ ├─images
     │ └─js
     ├─upload_data

### SimilarityDjango

#### 	SimilarityDjango文件夹中包含整个项目的所有代码，其中:

#### 		1.<u>similarity</u>包含相似度计算算法的核心代码(与网页完美分离,可直接取出放到别处		   运行);

#### 		2.<u>SimilarityApp</u>包含Django app的主要代码(数据库模板,后台管理,url转发,视图,templates);

#### 		<u>3.SimilarityDjango</u>是Django框架默认生成的文件夹,其中包含了Django的配置文件settings.py等;

#### 		<u>4.static</u>包含项目的静态文件(image文件,css文件,js文件)。注意:html文件放在.Similarity/templates目录下,Django约定俗成。

#### 	5.<u>upload_data</u>用来存储用户上传的文件,部署时可有可无,在运行时会自动创建。

### 2.主要部分功能

#### (1)SimilarityApp:其中__init__.py,admin.py,apps.py,models.py,tests.py,views.py为Django自动生成的文件。根据数据库的结构,修改了models.py中的代码，其中定义了数据库的所有模型。admin.py轻度定制后台管理界面。views.py中定义全部视图函数。||

#### 后来创建的文件是urls.py,encryption.py,recieve_file.py。

#### urls.py中定义App的视图转发,为Django约定俗成的写法。

#### encryption.py中定义了基于base64的加密函数和解密函数，用于字符串加密和解密。recieve_file.py中定义了本文件定义接收用户上传文件的方法和处理方法(与MySql,redis数据库交互)。

#### recieve_file.py:

```python
"""
 定义接收用户上传文件的方法和处理方法(与MySql,redis数据库交互)
 学生上传的源码(压缩包)文件保存在[根目录\upload_data\老师姓名\项目名称\模块名称\学生名称(姓名-账号名)\extends\]路径下
 学生上传的doc文件保存在[根目录\upload_data\老师姓名\项目名称\模块名称\学生名称\docs]路径下
 老师上传的文件保存在[根目录(和Django项目同级)\upload_data\老师姓名\students_info\]路径下(老师上传的是学生名单文件(Excel格式))
 @:param  file_object  是request.FILES.get(<input>的name标签)得到的对象,用于获取文件名字和文件数据流
 @:param  project  是文件所属项目的名称,用于创建项目文件夹
 @:param  module   是文件所属的项目的某一个模块的名称,用于创建模块文件夹
 @:param  teacher  是文件所属老师的models模型对象,方便对数据库进行操作,同时用于创建老师的文件夹
 @:param  student  是文件所属学生的(姓名-账号名),用于创建学生文件夹
 @:param  is_doc  (Boolean type)判断是否是doc类型的文件
 接收用户doc文件后分词,然后保存到redis数据库
"""
```

#### (2)similarity[相似度计算模块]

####          >TF-IDF(Term Frequency-Inverse Document Frequency词频-逆文档频率)算法<

#### 1.TF(词频)：一篇文章中各种词语出现的次数

#### 	e.g:中国的大学生有很多。

#### 	将上述的句子分词处理并统计词频后可得:[中国1,的1,大学生1,有1,很多1]

![img](http://www.ruanyifeng.com/blogimg/asset/201303/bg2013031505.png) 

#### 2.IDF(逆文档频率)：在词频的基础上，要对每个词分配一个"重要性"权重 

#### 	比如在一个主题为快速排序的实验中，使用所有用户的实验报告构建语料库，“快速排序”，“算法”等词可能每篇文章都会出现，它们并不能很好的反映每篇文章的特性，所以它们在计算相似性时所占的权重要适当的降低。

#### ![img](http://www.ruanyifeng.com/blogimg/asset/201303/bg2013031506.png) 

#### 3.TF-IDF

#### 	得到了TF和IDF的值之后,将两者相乘即可求得TF-IDF的值。

#### 4.余弦相似度:

##### 假定a向量是[x1, y1]，b向量是[x2, y2]，那么可以将余弦定理改写成下面的形式：

![img](http://www.ruanyifeng.com/blogimg/asset/201303/bg2013032006.png)

##### 在坐标系中表示如下:

![img](http://www.ruanyifeng.com/blogimg/asset/201303/bg2013032005.png)

#### 5.计算文档相似度

#### 	计算文档相似度的流程如下:

            **（1）使用TF-IDF算法，找出两篇文章的关键词 **

　　        **（2）每篇文章各取出若干个关键词（比如20个），合并成一个集合，计算每篇文章对于这个集合中的词                      的词频（为了避免文章长度的差异，可以使用相对词频）**

　　        **（3）生成两篇文章各自的词频向量**

　　        **（4）计算两个向量的余弦相似度，值越大就表示越相似。**

## 三.主要外部库和工具

### 1.jieba(分词核心库)

### 2.python-docx(docx文档解析库)[√目前只支持docx文档]

### 3.antiword(doc文档解析工具)[×不启用]

### 4.gensim(相似度计算包)

### 5.redis, pymysql(数据库交互库)

### 6.pandas(处理Excel数据)

## 四.数据库设计

### 1.MySQL数据库设计

#### 数据表:student, teacher, user_relation, project, module, project_user

### 2.redis数据库设计

#### 使用db=5数据库

## 五.部署流程

### 1.从github上clone项目到本地(推荐直接从PyCharm中clone)

#### 项目地址:https://github.com/Forest75/doc-similarity

### 2.在项目的根目录下打开cmd,输入>pipenv install(回车),等待虚拟环境安装完成。

####      [请确保电脑上已经配置好python环境(3.6或以上)并安装了pipenv库(直接pip install pipenv)]
