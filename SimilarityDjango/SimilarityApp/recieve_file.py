'''
本文件定义接受用户上传文件的方法
学生上传的源码(压缩包)文件保存在[根目录\upload_data\老师姓名\项目名称\模块名称\学生名称(姓名-账号名)\]路径下
TODO 学生上传的doc|docx文件保存在[根目录\upload_data\老师姓名\项目名称\模块名称\学生名称\docx]路径下
老师上传的文件保存在[根目录\upload_data\老师姓名\students_info\]路径下(老师上传的是学生名单文件(Excel格式))
@:param  file_object  是request.FILES.get(<input>的name标签)得到的对象,用于获取文件名字和文件数据流
@:param  project_directory  是文件所属项目的名称,用于创建项目文件夹
@:param  module_directory  是文件所属的项目的某一个模块的名称,用于创建模块文件夹
@:param  teacher_name_directory  是文件所属老师的名称,用于创建老师的文件夹
'''

import os


def recieve_stu_file(file_object, teacher, project, module, student, is_doc=False):
    file_directory = os.path.join(os.path.join(os.path.join(os.path.join(os.path.join(os.path.abspath('.'), 'upload_data'), teacher),project), module),student)
    if is_doc:     # 如果文件是doc|docx文件
        file_directory = os.path.join(file_directory, 'docx')
    os.mkdir(file_directory)
    file_path = os.path.join(file_directory, file_object.name)
    with open(file_path, 'wb') as f:
        for chunk in file_object.chunks():
            f.write(chunk)

def recieve_stu_doc_file(file_object, teacher, project, module, student):
    file_directory = os.path.join(os.path.join(os.path.join(os.path.join(os.path.join(os.path.abspath('.'), 'upload_data'), teacher),project), module),student)
    file_directory = os.path.join(file_directory, 'docx')
    os.mkdir(file_directory)
    file_path = os.path.join(file_directory, file_object.name)
    with open(file_path, 'wb') as f:
        for chunk in file_object.chunks():
            f.write(chunk)


def recieve_tea_file(file_object, teacher):
    file_directory = os.path.join(os.path.join(os.path.join(os.path.abspath('.'), 'upload_data'), teacher), 'students_info')
    os.mkdir(file_directory)
    file_path = os.path.join(file_directory, file_object.name)
    with open(file_path, 'wb') as f:
        for chunk in file_object.chunks():
            f.write(chunk)