from django.shortcuts import render, redirect, get_object_or_404
from .models import Student, Teacher
from .encryption import encrypt, decrypt
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
            return render(request, 'SimilarityApp/student.html', {'username':username})
        else:
            return redirect('SimilarityApp:登录')
    elif role == 'tea':
        teacher = get_object_or_404(Teacher, pk=user_id)
        if username == teacher.name:
            return render(request, 'SimilarityApp/teacher.html', {'username':username})
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