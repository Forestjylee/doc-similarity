from django.shortcuts import render, redirect, get_object_or_404
from django.utils.encoding import escape_uri_path
from django.http import HttpResponse, Http404, FileResponse
import os
from .models import Student, Teacher, Project, ProjectUser, UserRelation, Module
from .encryption import encrypt, decrypt
from .recieve_file import *     # recieve_file是视图函数的辅助py文件

# Create your views here.


# 默认起始页直接跳转到登录界面
def start(request):
    return redirect('SimilarityApp:登录')

# 主页(role表示用户是学生还是老师)
def home(request, role, user_id, username):
    try:
        username = decrypt(username)
    except:
        return redirect('SimilarityApp:登录')
    if role == 'stu':
        student = get_object_or_404(Student, pk=user_id)
        if username == student.name:
            try:
                project_user_list = ProjectUser.objects.filter(student=student)
                project_list = [project_user.project for project_user in project_user_list]
                for project in project_list:
                    project.url = '/project/user/{}/{}/{}/'.format(student.id, encrypt(student.name), encrypt(project.name))
                return render(request, 'SimilarityApp/student.html', {'username':username, 'project_list':project_list})
            except:
                return render(request, 'SimilarityApp/student.html', {'username':username})
        else:
            return redirect('SimilarityApp:登录')
    elif role == 'tea':
        teacher = get_object_or_404(Teacher, pk=user_id)
        if username == teacher.name:
            try:
                project_list = Project.objects.filter(teacher=teacher)
                for project in project_list:
                    project.url = '/project/admin/{}/{}/'.format(project.id, encrypt(project.name))
                    project.delete_url = '/delete/project/{}/{}/{}/'.format(project.id, encrypt(project.name), encrypt(teacher.name))
            except:
                project_list = []
            if request.method == 'POST':
                if "create_project" in request.POST:
                    return redirect('SimilarityApp:创建项目', teacher_id=teacher.id, teacher_name=encrypt(teacher.name))
                if "send_zip_file" in request.FILES:
                    file_obj = request.FILES.get('send_zip_file')
                    try:
                        recieve_zip_file(file_obj, teacher)
                        return render(request, 'SimilarityApp/teacher.html', {'username':username, 'project_list':project_list, 'upload_zip_result':'压缩包上传读取成功!'})
                    except TypeError:
                        return render(request, 'SimilarityApp/teacher.html', {'username':username, 'project_list':project_list, 'upload_zip_result':'文件格式错误!不是zip压缩包'})
                    except ValueError:
                        return render(request, 'SimilarityApp/teacher.html', {'username':username, 'project_list':project_list, 'upload_zip_result':'压缩包读取失败!请稍后重新上传'})
                    except Exception:
                        return render(request, 'SimilarityApp/teacher.html', {'username':username, 'project_list':project_list, 'upload_zip_result':'压缩包上传失败!请稍后重新上传'})
                if "quick_calculate" in request.POST:
                    return redirect('SimilarityApp:快速计算结果', teacher_id=teacher.id)
            else:
                return render(request, 'SimilarityApp/teacher.html', {'username':username,'project_list':project_list})
        else:
            return redirect('SimilarityApp:登录')

# 登录界面
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            teacher = Teacher.objects.get(account=username)
            if password == teacher.password:
                return redirect('SimilarityApp:主页', role="tea", user_id=teacher.id, username=encrypt(teacher.name))
            else:
                return render(request, 'SimilarityApp/login.html', {'error':'密码错误!'})
        except:
            try:
                student = Student.objects.get(account=username)
                if password == student.password:
                    return redirect('SimilarityApp:主页', role="stu", user_id=student.id, username=encrypt(student.name))
                else:
                    return render(request, 'SimilarityApp/login.html', {'error':'密码错误!'})
            except:
                return render(request, 'SimilarityApp/login.html', {'error':'用户名不存在!'})
        return
    else:
        return render(request, 'SimilarityApp/login.html')

# 项目管理界面
def project_admin(request, project_id, project_name):
    project = get_object_or_404(Project, pk=project_id)
    try:
        project_name = decrypt(project_name)
        if project.name != project_name:
            raise ValueError
        else:
            try:
                module_list = Module.objects.filter(project=project)
            except:
                return render(request, 'SimilarityApp/admin_project.html', {'project_name': project_name})
            for module in module_list:
                module.url = '/module/admin/{}/{}/'.format(module.id, encrypt(module.name))
                module.similarity_url = '/similarity/tea/{}/{}/'.format(module.id, encrypt(module.name))
            if request.method == 'POST':
                if 'admin_user' in request.POST:
                    return redirect('SimilarityApp:编辑参与学生', project_id=project_id,
                                    project_name=encrypt(project_name))
                if 'edit_project' in request.POST:
                    return redirect('SimilarityApp:修改项目信息', project_id=project_id,
                                    project_name=encrypt(project_name))
                if 'create_module' in request.POST:
                    return redirect('SimilarityApp:新建模块', project_id=project_id, project_name=encrypt(project_name))
            else:
                return render(request, 'SimilarityApp/admin_project.html', {'project_name':project_name, 'module_list':module_list})
    except:
        return Http404

def project_user(request, user_id, username, project_name):
    try:
        project_name = decrypt(project_name)
        try:
            project = Project.objects.get(name=project_name)
            module_list = Module.objects.filter(project=project)
        except:
            return Http404
        for module in module_list:
            module.url = '/module/user/{}/{}/{}/{}/'.format(user_id, username, module.id, encrypt(module.name))
            module.similarity_url = '/similarity/{}/{}/{}/'.format(module.id, encrypt(module.name), username)
        return render(request, 'SimilarityApp/project_user.html', {'project_name':project_name, 'module_list':module_list})
    except:
        return Http404

# 编辑参与项目的学生(通过excel文件添加)
def admin_user(request, project_id, project_name):
    project = get_object_or_404(Project, pk=project_id)
    try:
        project_name = decrypt(project_name)
        if project.name != project_name:
            raise ValueError
        else:
            project_user_list = ProjectUser.objects.filter(project=project)
            student_in_project = [project_user.student for project_user in project_user_list]
            if request.method == 'POST':
                file_obj = request.FILES.get('send_file')      # 上传文件的文件名
                try:
                    recieve_tea_file(file_obj, teacher=project.teacher, project=project)
                    return render(request, 'SimilarityApp/admin_user.html', {'project_name':project_name, 'student_list':student_in_project,'upload_result':'上传并读取成功!请刷新页面查看更新后结果'})
                except TypeError:
                    return render(request, 'SimilarityApp/admin_user.html', {'project_name':project_name, 'student_list':student_in_project,'upload_result':'文件类型错误,不是Excel文件!'})
                except ValueError:
                    return render(request, 'SimilarityApp/admin_user.html', {'project_name':project_name, 'student_list':student_in_project,'upload_result':'读取失败!请检查Excel是否完整,以及是否含有(姓名,学号,班级)栏目'})
                except Exception:
                    return render(request, 'SimilarityApp/admin_user.html', {'project_name':project_name, 'student_list':student_in_project,'upload_result':'上传失败,请重试'})
            else:
                return render(request, 'SimilarityApp/admin_user.html', {'project_name':project_name, 'student_list':student_in_project})
    except:
        return Http404("您要查看的项目不存在!")

# 修改项目信息
def edit_project(request, project_id, project_name):
    project = get_object_or_404(Project, pk=project_id)
    try:
        project_name = decrypt(project_name)
        if project_name != project.name:
            raise ValueError
        else:
            if request.method == 'POST':
                project_new_name = request.POST['project_name']
                project_end_date = request.POST['project_end_date']
                if 'confirm' in request.POST:
                    teacher = project.teacher
                    update_project_name(teacher, project.name, project_new_name)    # 修改本地文件名
                    project.name = project_new_name
                    project.end_date = project_end_date
                    try:
                        project.save()
                        #return render(request, 'SimilarityApp/edit_project.html', {'edit_status':'修改成功!'})
                        return redirect('SimilarityApp:老师项目管理', project_id=project_id, project_name=encrypt(project_new_name))
                    except:
                        return render(request, 'SimilarityApp.edit_project.html', {'edit_status':'修改失败!'})
                if 'reset' in request.POST:
                    return render(request, 'SimilarityApp/edit_project.html')
            return render(request, 'SimilarityApp/edit_project.html')
    except:
        return Http404

# TODO 管理子模块
def admin_module(request, module_id, module_name):
    module = get_object_or_404(Module, pk=module_id)
    try:
        module_name = decrypt(module_name)
        if module_name != module.name:
            raise ValueError
        try:
            project = module.project
            teacher = project.teacher
            if request.method == 'POST':
                pass
            else:
                project_user_list = ProjectUser.objects.filter(project=project)
                student_list = [project_user.student for project_user in project_user_list]
                for student in student_list:
                    doc_directory = generate_stu_doc_directory(student, teacher, project.name, module.name)
                    student.is_upload = '已提交' if not is_empty(doc_directory) else '未提交'
                    if student.is_upload == '已提交':
                        student.download_url = '/download/zip/{}/{}/{}/'.format(module_id, student.id, encrypt(student.name))
                    else:
                        student.download_url = ''
                return render(request, 'SimilarityApp/admin_module.html', {'module_name':module_name, 'student_list':student_list})
        except:
            return render(request, 'SimilarityApp/admin_module.html')
    except:
        return Http404

# 用户文档和附件,只接受docx文件，并分词存储进入redis中
def use_module(request, user_id, username, module_id, module_name):
    module = get_object_or_404(Module, pk=module_id)
    student = get_object_or_404(Student, pk=user_id)
    delete_extends_url = '/delete/extend/{}/{}/'.format(user_id, module_id)
    try:
        module_name = decrypt(module_name)
        username = decrypt(username)
        if module_name != module.name or student.name != username:
            raise ValueError
        else:
            project = module.project
            teacher = project.teacher
            doc_directoey = generate_stu_doc_directory(student, teacher, project.name, module.name)
            extend_directory = generate_stu_extend_directory(student, teacher, project.name, module.name)
            doc_upload_status = '已提交√' if not is_empty(doc_directoey) else '未提交'
            extend_upload_status = '已提交√' if not is_empty(extend_directory) else '未提交'
            doc_file_list = get_filelist(doc_directoey, file_type='doc', user_id=user_id, module_id=module_id)
            extend_file_list = get_filelist(extend_directory, file_type='extend', user_id=user_id, module_id=module_id)
            if request.method == 'POST':
                if 'send_extend_file' in request.FILES:
                    file_obj = request.FILES.get('send_extend_file')
                    try:
                        recieve_stu_file(file_obj, teacher, project.name, module.name, student, is_doc=False)
                        return render(request, 'SimilarityApp/module_user.html',  {'module_name':module_name, 'delete_extends_url':delete_extends_url, 'doc_upload_status':doc_upload_status, 'extend_upload_status':'已提交√', 'doc_file_list':doc_file_list,'extend_file_list':extend_file_list,'extend_upload_result':'附件上传成功!请刷新页面获取最新结果'})
                    except:
                        return render(request, 'SimilarityApp/module_user.html',  {'module_name':module_name, 'delete_extends_url':delete_extends_url, 'doc_upload_status':doc_upload_status, 'extend_upload_status':extend_upload_status, 'doc_file_list':doc_file_list,'extend_file_list':extend_file_list,'extend_upload_result':'附件上传失败!请稍后重试'})
                if 'send_doc_file' in request.FILES:
                    file_obj = request.FILES.get('send_doc_file')
                    try:
                        recieve_stu_file(file_obj, teacher, project.name, module.name, student, is_doc=True)
                        return render(request, 'SimilarityApp/module_user.html', {'module_name':module_name, 'delete_extends_url':delete_extends_url, 'doc_upload_status':'已提交√', 'extend_upload_status':extend_upload_status, 'doc_file_list':doc_file_list,'extend_file_list':extend_file_list,'doc_upload_result':'文档上传并读取成功!请刷新页面获取最新结果'})
                    except TypeError:
                        return render(request, 'SimilarityApp/module_user.html', {'module_name':module_name, 'delete_extends_url':delete_extends_url, 'doc_upload_status':doc_upload_status, 'extend_upload_status':extend_upload_status, 'doc_file_list':doc_file_list,'extend_file_list':extend_file_list, 'doc_upload_result':'文件类型错误!不是docx类型的文件'})
                    except ConnectionRefusedError:
                        return render(request, 'SimilarityApp/module_user.html', {'module_name':module_name, 'delete_extends_url':delete_extends_url, 'doc_upload_status':doc_upload_status, 'extend_upload_status':extend_upload_status, 'doc_file_list':doc_file_list,'extend_file_list':extend_file_list, 'doc_upload_result':'文档分词失败!请稍后重试'})
                    except ValueError:
                        return render(request, 'SimilarityApp/module_user.html', {'module_name':module_name, 'delete_extends_url':delete_extends_url, 'doc_upload_status':doc_upload_status, 'extend_upload_status':extend_upload_status, 'doc_file_list':doc_file_list,'extend_file_list':extend_file_list, 'doc_upload_result':'文档读取失败!请检查文件是否完整'})
                    except Exception:
                        return render(request, 'SimilarityApp/module_user.html', {'module_name':module_name, 'delete_extends_url':delete_extends_url, 'doc_upload_status':doc_upload_status, 'extend_upload_status':extend_upload_status, 'doc_file_list':doc_file_list,'extend_file_list':extend_file_list, 'doc_upload_result':'文档上传失败!请稍后重试'})
            else:
                return render(request, 'SimilarityApp/module_user.html', {'module_name':module_name, 'delete_extends_url':delete_extends_url, 'doc_upload_status':doc_upload_status, 'extend_upload_status':extend_upload_status, 'doc_file_list':doc_file_list,'extend_file_list':extend_file_list})
    except:
        return Http404

# 创建项目界面
def create_project(request, teacher_id, teacher_name):
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    try:
        teacher_name = decrypt(teacher_name)
        if teacher_name != teacher.name:
            raise ValueError
        else:
            if request.method == 'POST':
                project_name = request.POST['project_name']
                project_end_date = request.POST['project_end_date']
                if 'confirm' in request.POST:
                    try:
                        project = Project()
                        project.name = project_name
                        project.teacher = teacher
                        if project_end_date:
                            project.end_date = project_end_date
                        project.save()
                        return render(request, 'SimilarityApp/create_project.html', {'create_status':'创建成功!'})
                    except:
                        return render(request, 'SimilarityApp/create_project.html', {'create_status':'创建失败!请重试'})
                if 'reset' in request.POST:
                    return render(request, 'SimilarityApp/create_project.html')
            return render(request, 'SimilarityApp/create_project.html')
    except:
        Http404("页面不存在!")

# 创建子模块界面
def create_module(request, project_id, project_name):
    project = get_object_or_404(Project, pk=project_id)
    try:
        project_name = decrypt(project_name)
        if project_name != project.name:
            raise ValueError
        else:
            if request.method == 'POST':
                module_name = request.POST['module_name']
                module_description = request.POST['module_description']
                module_end_date = request.POST['module_end_date']
                if 'confirm' in request.POST:
                    try:
                        module = Module()
                        module.name = module_name
                        module.project = project
                        if module_end_date:
                            module.end_date = module_end_date
                        if module_description:
                            module.description = module_description
                        module.save()
                        return render(request, 'SimilarityApp/create_module.html', {'create_status': '创建成功!'})
                    except:
                        return render(request, 'SimilarityApp/create_module.html', {'create_status': '创建失败!请重试'})
                if 'reset' in request.POST:
                    return render(request, 'SimilarityApp/create_module.html')
            return render(request, 'SimilarityApp/create_module.html')
    except:
        Http404("页面不存在!")

# 显示计算相似度的结果(老师视角)
def show_similarity(request, module_id, module_name):
    module = get_object_or_404(Module, pk=module_id)
    project = module.project
    teacher = project.teacher
    module_name = decrypt(module_name)
    similarity_list = get_similarity_list(teacher, project_name=project.name, module=module)
    return render(request, 'SimilarityApp/similarity_tea.html', {'module_name':module_name, 'similarity_list':similarity_list})

# TODO 显示计算相似度的结果(学生视角)
def show_similarity_stu(request, module_id, module_name, username):
    return render(request, 'SimilarityApp/similarity_stu.html')

# 显示计算相似度的结果(快速计算)
def show_quick_cal_similarity(request, teacher_id):
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    try:
        similarity_list = get_quick_similarity_list(teacher)
        return render(request, 'SimilarityApp/similarity_tea.html', {'module_name':'*快速计算*', 'similarity_list':similarity_list})
    except:
        return HttpResponse('计算出现错误,请检查压缩包内容后重新上传计算.')

def delete_project(request, project_id, project_name, teacher_name):
    project = get_object_or_404(Project, pk=project_id)
    try:
        project_name = decrypt(project_name)
        teacher_name = decrypt(teacher_name)
        teacher = project.teacher
        if project.name != project_name or teacher_name != teacher.name:
            raise ValueError
        else:
            project_user_list = ProjectUser.objects.filter(project=project)
            for project_user in project_user_list:
                project_user.delete()
            delete_project_directory(teacher, project_name)
            project.delete()
    finally:
        return redirect('SimilarityApp:主页', role='tea', user_id=teacher.id, username=encrypt(teacher.name))

def download_single_file(request, file_type, user_id, module_id, filename):
    module = get_object_or_404(Module, pk=module_id)
    student = get_object_or_404(Student, pk=user_id)
    try:
        project = module.project
        teacher = project.teacher
        filename = decrypt(filename)
        if file_type == 'doc':
            directory = generate_stu_doc_directory(student, teacher, project.name, module.name)
        elif file_type == 'extend':
            directory = generate_stu_extend_directory(student, teacher, project.name, module.name)
        else:
            raise TypeError
        file_path = os.path.join(directory, filename)
        f = open(file_path, 'rb')
        response = FileResponse(f)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename={}'.format(escape_uri_path(filename))
        return response
    except:
        return Http404

# 将单个学生提交的文件全部打包下载到本地
def download_zip_file(request, module_id, user_id, username):
    module = get_object_or_404(Module, pk=module_id)
    student = get_object_or_404(Student, pk=user_id)
    try:
        project = module.project
        teacher = project.teacher
        username = decrypt(username)
        if username == student.name:
            filename = '{}-{}.zip'.format(student.name, student.account)
            zip_file_path = generate_zip_file(student, teacher, project.name, module.name)
            f = open(zip_file_path, 'rb')
            response = FileResponse(f)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename={}'.format(escape_uri_path(filename))
            return response
        else:
            return Http404
    except:
        return Http404

# [老师查看查重界面]下载指定文档
def download_doc(request, student_info, module_id):
    module = get_object_or_404(Module, pk=module_id)
    project = module.project
    teacher = project.teacher
    teacher_info = '{}-{}'.format(teacher.name, teacher.account)
    file_directory = os.path.join(os.path.join(os.path.join(os.path.join(os.path.join(os.path.join(os.path.abspath('..'),'upload_data'),teacher_info),project.name),module.name),student_info),'docs')
    try:
        filename = os.listdir(file_directory)[0]
        file_path = os.path.join(file_directory, filename)
        f = open(file_path, 'rb')
        response = FileResponse(f)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename={}'.format(escape_uri_path(filename))
        return response
    except:
        return Http404


# 将快速下载界面的某个指定文档下载到本地
def download_quick_cal_doc(request, teacher_id, filename):
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    file_path = genetate_quick_cal_path(teacher, filename)
    try:
        f = open(file_path, 'rb')
        response = FileResponse(f)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename={}'.format(escape_uri_path(filename))
        return response
    except:
        return Http404


# 学生清空一个子模块的所有附件
def delete_extends(request, user_id, module_id):
    student = get_object_or_404(Student, pk=user_id)
    module = get_object_or_404(Module, pk=module_id)
    project = module.project
    teacher = project.teacher
    delete_extends_directory(teacher, student, project.name, module.name)
    return redirect('SimilarityApp:module使用', user_id=user_id, username=encrypt(student.name), module_id=module_id, module_name=encrypt(module.name))