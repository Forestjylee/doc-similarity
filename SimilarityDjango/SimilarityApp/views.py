from django.shortcuts import render, redirect

# Create your views here.


# 默认起始页直接跳转到登录界面
def start(request):
    return redirect('SimilarityApp:登录')

def home(request):
    return render(request, 'SimilarityApp/橙色鲸鱼.html')

def login(request):
    if request.method == 'POST':
        return redirect('SimilarityApp:主页')  # 登陆成功跳转到主页
    else:
        return render(request, 'SimilarityApp/login.html')