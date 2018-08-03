from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from .models import Student, Teacher, Project, ProjectUser, UserRelation, Module
from .encryption import encrypt, decrypt
from .recieve_file import recieve_stu_file, recieve_tea_file
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
            except:
                return render(request, 'SimilarityApp/student.html', {'username':username})
            if request.method == 'POST':
                file_obj = request.FILES.get('send_file')      # 上传文件的文件名
                #TODO 下面的teacher应传入项目所属老师的'姓名-账号名'[根据使用场景传入参数]
                recieve_stu_file(file_obj, teacher='何老师-123456', project='default_project', module='default_project', student='{}-{}'.format(student.name, student.account))
                return HttpResponse('OK')
            else:
                return render(request, 'SimilarityApp/student.html', {'username':username, 'project_list':project_list})
        else:
            return redirect('SimilarityApp:登录')
    elif role == 'tea':
        teacher = get_object_or_404(Teacher, pk=user_id)
        if username == teacher.name:
            try:
                project_list = Project.objects.filter(teacher=teacher)
                for project in project_list:
                    project.url = '/project/admin/{}/{}/'.format(project.id, encrypt(project.name))
            except:
                project_list = []
            if request.method == 'POST':
                if "create_project" in request.POST:
                    return redirect('SimilarityApp:创建项目', teacher_id=teacher.id, teacher_name=encrypt(teacher.name))
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
                    project.name = project_new_name
                    project.end_date = project_end_date
                    try:
                        project.save()
                        return render(request, 'SimilarityApp/edit_project.html', {'edit_status':'修改成功!'})
                    except:
                        return render(request, 'SimilarityApp.edit_project.html', {'edit_status':'修改失败!'})
                if 'reset' in request.POST:
                    return render(request, 'SimilarityApp/edit_project.html')
            return render(request, 'SimilarityApp/edit_project.html')
    except:
        return Http404("页面不存在!")

# TODO 管理子模块
def admin_module(request, module_id, module_name):
    return render(request, 'SimilarityApp/admin_module.html')

# TODO 使用子模块(提交作业)
def use_module(request, user_id, username, module_id, module_name):
    module_name = decrypt(module_name)
    return render(request, 'SimilarityApp/module_user.html', {'module_name':module_name})

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

# TODO 显示计算相似度的结果(老师视角)
def show_similarity(request, module_id, module_name):
    module_name = decrypt(module_name)
    return render(request, 'SimilarityApp/similarity_tea.html')

# TODO 显示计算相似度的结果(学生视角)
def show_similarity_stu(request, module_id, module_name, username):
    return render(request, 'SimilarityApp/similarity_stu.html')