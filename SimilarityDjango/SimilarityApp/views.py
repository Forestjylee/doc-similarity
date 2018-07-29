from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from .models import Student, Teacher
# Create your views here.


# 默认起始页直接跳转到登录界面
def start(request):
    return redirect('SimilarityApp:登录')

# 主页
def home(request):
    user_id = request.GET['user_id']
    username = request.GET['username']
    return render(request, 'SimilarityApp/橙色鲸鱼.html')

# 登录界面
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            teacher = Teacher.objects.get(account=username)
            if password == teacher.password:
                user = {'user_id': teacher.id, 'username': teacher.name}
                return redirect('SimilarityApp:主页')
            else:
                return render(request, 'SimilarityApp/login.html', {'error':'密码错误!'})
        except:
            try:
                student = Student.objects.get(account=username)
                if password == student.password:
                    user = { 'user_id':student.id, 'username':student.name}
                    return redirect('SimilarityApp:主页')
                else:
                    return render(request, 'SimilarityApp/login.html', {'error':'密码错误!'})
            except:
                return render(request, 'SimilarityApp/login.html', {'error':'用户名不存在!'})
        return
    else:
        return render(request, 'SimilarityApp/login.html')