#-*- coding:utf-8 -*-

# """
# 本文件定义接收用户上传文件的方法和处理方法(与MySql,redis数据库交互)
# 学生上传的源码(压缩包)文件保存在[根目录(和Django项目同级)\upload_data\老师姓名\项目名称\模块名称\学生名称(姓名-账号名)\extends\]路径下
# 学生上传的docx文件保存在[根目录(和Django项目同级)\upload_data\老师姓名\项目名称\模块名称\学生名称\docs]路径下
# 老师上传的文件保存在[根目录(和Django项目同级)\upload_data\老师姓名\students_info\]路径下(老师上传的是学生名单文件(Excel格式))
# @:param  file_object  是request.FILES.get(<input>的name标签)得到的对象,用于获取文件名字和文件数据流
# @:param  project  是文件所属项目的*名称*,用于创建项目文件夹
# @:param  module  是文件所属的项目的某一个模块的*名称*,用于创建模块文件夹
# @:param  teacher  是文件所属老师的models模型对象,方便对数据库进行操作,同时用于创建老师的文件夹
# @:param  student  是文件所属学生的models模型对象,用于创建学生文件夹
# @:param  is_doc  (Boolean type)判断是否是doc类型的文件
# """

# 不适用antiword进行读取,限制用户只能上传docx类型文件

import pandas as pd
import os
import shutil
import zipfile
from pathlib import Path
from .models import UserRelation, Student, ProjectUser
from .encryption import encrypt
from .artical_handler import ArticalHandler
from .word_segmenter import WordSegmenter

# 收到一个doc就分词并存储进redis数据库中|收到附件就保存起来
def recieve_stu_file(file_object, teacher, project, module, student, is_doc=False):
    file_type = os.path.splitext(file_object.name)[-1]
    student_info = '{}-{}'.format(student.name, student.account)
    teacher_info = '{}-{}'.format(teacher.name, teacher.account)
    file_directory = os.path.join(os.path.join(os.path.join(os.path.join(os.path.join(os.path.abspath('..'), 'upload_data'),teacher_info),project),module),student_info)
    if is_doc is True:     # 如果文件是doc|docx文件
        if file_type != '.docx':
            raise TypeError
        file_directory = os.path.join(file_directory, 'docs')
        shutil.rmtree(file_directory, ignore_errors=True)
    else:
        file_directory = os.path.join(file_directory, 'extends')
    os.makedirs(file_directory, exist_ok=True)
    file_path = os.path.join(file_directory, file_object.name)
    with open(file_path, 'wb') as f:
        for chunk in file_object.chunks():
            f.write(chunk)
    if is_doc is True:        # 如果是文档则进行分词后存储到redis数据库中
        try:
            student_key = '{}-{}-{}'.format(student_info, project, module)
            word_segmenter = WordSegmenter()
            separated_artical = word_segmenter.separate_artical_for_calculate(artical_generator=ArticalHandler.get_words_from_docx(docx_path=file_path, include_table=True))
            if not word_segmenter.save_to_redis(student_key, separated_artical):
                raise ConnectionRefusedError
        except ConnectionRefusedError:
            raise ConnectionRefusedError
        except:
            raise ValueError

def recieve_tea_file(file_object, teacher, project):
    file_type = os.path.splitext(file_object.name)[-1]
    if file_type != '.xlsx' and file_type != '.xls':
        raise TypeError
    teacher_info = '{}-{}'.format(teacher.name,teacher.account)
    file_directory = os.path.join(os.path.join(os.path.join(os.path.abspath('..'), 'upload_data'), teacher_info), 'students_info')
    os.makedirs(file_directory, exist_ok=True)
    file_path = os.path.join(file_directory, file_object.name)
    with open(file_path, 'wb') as f:
        for chunk in file_object.chunks():
            f.write(chunk)
    try:
        update_student_info(file_path=file_path, teacher=teacher, project=project)
    except:
        raise ValueError

# 老师文件夹的temp_zip目录用来保存临时接收的zip文件(解压到quick_cal文件夹,然后开始计算)
def recieve_zip_file(file_object, teacher):
    file_type = os.path.splitext(file_object.name)[-1]
    if file_type != '.zip':
        raise TypeError
    teacher_info = '{}-{}'.format(teacher.name, teacher.account)
    zip_directory = os.path.join(os.path.join(os.path.join(os.path.abspath('..'), 'upload_data'),teacher_info),'temp_zip')
    target_directory = os.path.join(os.path.join(os.path.join(os.path.abspath('..'), 'upload_data'),teacher_info),'quick_cal')
    shutil.rmtree(zip_directory, ignore_errors=True)
    os.makedirs(zip_directory)
    zip_path = os.path.join(zip_directory, file_object.name)
    with open(zip_path, 'wb') as f:
        for chunk in file_object.chunks():
            f.write(chunk)
    try:
        decompress(zip_path=zip_path, target_directory=target_directory)
    except:
        raise ValueError

# 读取上传的Excel文件,将文件中的信息同步到数据库中(student表,user_relation表,project_user表)[经过测试,可以正常运行]
def update_student_info(file_path, teacher, project):
    student_info = pd.read_excel(file_path)      # student_info type->DataFrame
    student_name, student_account, student_unit = list(student_info['姓名']), list(student_info['学号']), list(student_info['班级'])
    for name, account, unit in zip(student_name, student_account, student_unit):
        try:
            student = Student.objects.get(account=account)    # 报出DonotExist错误才创建用户
        except:
            student = Student()
            student.name = name
            student.account = str(account)
            student.password = student.account[-6:]           # init password is account[-6:]
            student.unit = unit
            student.save()
        try:
            relation = UserRelation.objects.get(student=student, teacher=teacher)
        except:
            relation = UserRelation()
            relation.student = student
            relation.teacher = teacher
            relation.save()
        try:
            project_user = ProjectUser.objects.get(project=project, student=student)
        except:
            project_user = ProjectUser()
            project_user.project = project
            project_user.student = student
            project_user.save()

# 本版本不使用antiword
# def get_content_from_antiword(antiword_path, doc_file_path):
#     content = subprocess.check_output([antiword_path, doc_file_path])
#     # antiword返回的content的格式有待确认

def generate_stu_directory(student, teacher, project, module):
    student_info = '{}-{}'.format(student.name, student.account)
    teacher_info = '{}-{}'.format(teacher.name, teacher.account)
    file_directory = os.path.join(os.path.join(os.path.join(os.path.join(os.path.join(os.path.abspath('..'), 'upload_data'),teacher_info),project),module),student_info)
    return file_directory

# 生成一个文件夹路径，方便接下来判断目录是否为空，从而判断用户是否提交了文件
def generate_stu_doc_directory(student, teacher, project, module):
    student_info = '{}-{}'.format(student.name, student.account)
    teacher_info = '{}-{}'.format(teacher.name, teacher.account)
    file_directory = os.path.join(os.path.join(os.path.join(os.path.join(os.path.join(os.path.join(os.path.abspath('..'), 'upload_data'),teacher_info),project),module),student_info),'docs')
    return file_directory

# 生成一个文件夹路径，方便接下来判断目录是否为空，从而判断用户是否提交了附件
def generate_stu_extend_directory(student, teacher, project, module):
    student_info = '{}-{}'.format(student.name, student.account)
    teacher_info = '{}-{}'.format(teacher.name, teacher.account)
    file_directory = os.path.join(os.path.join(os.path.join(os.path.join(os.path.join(os.path.join(os.path.abspath('..'), 'upload_data'),teacher_info),project),module),student_info),'extends')
    return file_directory

# 在所给文件夹的上一级目录下新建一个【文件夹名_zip】目录，将该文件夹压缩后放到此目录中(放回target_path)
def generate_zip_file(student, teacher, project, module):
    directory = generate_stu_directory(student, teacher, project, module)
    path_splited = os.path.split(directory)
    zip_name = path_splited[-1] + '.zip'
    target_directory = os.path.join(path_splited[0], path_splited[-1]+'_zip')
    target_zip_path = os.path.join(target_directory, zip_name)
    shutil.rmtree(target_directory, ignore_errors=True)
    os.makedirs(target_directory, exist_ok=True)
    z = zipfile.ZipFile(target_zip_path, 'w', zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(directory):
        fpath = dirpath.replace(directory,'')
        fpath = fpath and fpath + os.sep or ''
        for filename in filenames:
            z.write(os.path.join(dirpath, filename), fpath+filename)
    z.close()
    return target_zip_path

# 判断目录是否为空
def is_empty(directory_path):
    try:
        if not os.listdir(directory_path):
            return True
        else:
            return False
    except:
        return True

def update_project_name(teacher, project_old_name, project_new_name):
    teacher_info = '{}-{}'.format(teacher.name, teacher.account)
    old_directory = os.path.join(os.path.join(os.path.join(os.path.abspath('..'), 'upload_data'),teacher_info),project_old_name)
    new_directory = os.path.join(os.path.join(os.path.join(os.path.abspath('..'), 'upload_data'),teacher_info),project_new_name)
    os.rename(old_directory, new_directory)

def delete_project_directory(teacher, project_name):
    teacher_info = '{}-{}'.format(teacher.name, teacher.account)
    directory = os.path.join(os.path.join(os.path.join(os.path.abspath('..'),'upload_data'),teacher_info),project_name)
    shutil.rmtree(directory, ignore_errors=True)

def delete_extends_directory(teacher, student, project_name, module_name):
    file_directory = generate_stu_extend_directory(student,teacher, project_name, module_name)
    shutil.rmtree(file_directory, ignore_errors=True)

def get_filename(file_path):
    if os.path.exists(file_path):
        filename = os.path.split(file_path)[-1]
        return filename
    else:
        return None

# 学生上传文件界面,获取文件path的函数
def get_filelist(directory_path, file_type, user_id, module_id):
    try:
        file_list = []
        file_path_list = os.listdir(directory_path)
        for file_path in file_path_list:
            file_path = os.path.join(directory_path, file_path)
            filename = get_filename(file_path=file_path)
            file = {
                'filename' : filename,
                'download_url' : '/download/single/{}/{}/{}/{}/'.format(file_type, user_id, module_id, encrypt(filename))
            }
            file_list.append(file)
        return file_list
    except:
        return []

# 解压缩
def decompress(zip_path, target_directory):
    f = zipfile.ZipFile(zip_path)
    shutil.rmtree(target_directory, ignore_errors=True)
    os.makedirs(target_directory, exist_ok=True)
    for name in f.namelist():
        f.extract(name, target_directory)
        old_path = os.path.join(target_directory, name)
        new_name = os.path.join(target_directory, name.encode('cp437').decode('gbk'))  # 解决中文乱码问题
        os.rename(old_path, new_name)

##########################################################################################
