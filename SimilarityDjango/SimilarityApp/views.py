from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from .models import Student, Teacher, Project
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
            if request.method == 'POST':
                file_obj = request.FILES.get('send_file')      # 上传文件的文件名
                #TODO 下面的teacher应传入项目所属老师的'姓名-账号名'[根据使用场景传入参数]
                recieve_stu_file(file_obj, teacher='何老师-123456', project='default_project', module='default_project', student='{}-{}'.format(student.name, student.account))
                return HttpResponse('OK')
            else:
                return render(request, 'SimilarityApp/student.html', {'username':username})
        else:
            return redirect('SimilarityApp:登录')
    elif role == 'tea':
        teacher = get_object_or_404(Teacher, pk=user_id)
        if username == teacher.name:
            try:
                project_list = Project.objects.filter(teacher=teacher)
                for project in project_list:
                    project.url = '/project/tea/{}/{}/'.format(project.id, encrypt(project.name))
            except:
                project_list = []
            if request.method == 'POST':
                file_obj = request.FILES.get('send_file')      # 上传文件的文件名
                try:
                    recieve_tea_file(file_obj, teacher=teacher)
                    return render(request, 'SimilarityApp/teacher.html', {'username':username,'project_list':project_list,'upload_result':'上传并读取成功!'})
                except TypeError:
                    return render(request, 'SimilarityApp/teacher.html', {'username':username,'project_list':project_list,'upload_result':'文件类型错误,不是Excel文件!'})
                except ValueError:
                    return render(request, 'SimilarityApp/teacher.html', {'username':username,'project_list':project_list,'upload_result':'读取失败!请检查Excel是否完整,以及是否含有(姓名,学号,班级)栏目'})
                except Exception:
                    return render(request, 'SimilarityApp/teacher.html', {'username':username,'project_list':project_list,'upload_result':'上传失败,请重试'})
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
            return render(request, 'SimilarityApp/admin_project.html')
    except:
        return Http404("您要查看的项目不存在!")

# 创建项目界面
def create_project(request, teacher_id, teacher_name):
    pass