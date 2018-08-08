from django.urls import path
from . import views

app_name = 'SimilarityApp'   # app名字

urlpatterns = [
    path('', views.start, name='起始页'),
    path('login/', views.login, name='登录'),
    path('home/<role>/<user_id>/<username>/', views.home, name='主页'),
    path('project/user/<user_id>/<username>/<project_name>/', views.project_user, name='项目使用'),
    path('project/admin/<project_id>/<project_name>/', views.project_admin, name='老师项目管理'),
    path('create/<teacher_id>/<teacher_name>/', views.create_project, name='创建项目'),
    path('similarity/tea/<module_id>/<module_name>/', views.show_similarity_tea, name='文档相似度(老师)'),
    path('similarity/<module_id>/<module_name>/<username>/', views.show_similarity_stu, name='文档相似度(学生)'),
    path('similarity/quick_cal/<teacher_id>/', views.show_quick_cal_similarity, name='快速计算结果'),
    path('admin_user/<project_id>/<project_name>/', views.admin_user, name='编辑参与学生'),
    path('edit_project/<project_id>/<project_name>', views.edit_project, name='修改项目信息'),
    path('create_module/<project_id>/<project_name>/', views.create_module, name='新建模块'),
    path('module/admin/<module_id>/<module_name>/', views.admin_module, name='module管理'),
    path('module/user/<user_id>/<username>/<module_id>/<module_name>/', views.use_module, name='module使用'),
    path('delete/project/<project_id>/<project_name>/<teacher_name>/', views.delete_project, name='删除项目'),
    path('delete/project_user/<project_id>/<user_id>/<username>/', views.delete_project_user,name='删除某个项目使用者'),
    path('delete/module/<module_id>/<module_name>/', views.delete_module, name='删除子模块'),
    path('delete/extend/<user_id>/<module_id>/', views.delete_extends, name='删除所有附件'),
    path('download/single/<file_type>/<user_id>/<module_id>/<filename>/', views.download_single_file, name='下载单个文件'),
    path('download/zip/<module_id>/<user_id>/<username>/', views.download_zip_file, name='下载多个文件组成的压缩包'),
    path('download/quick_cal/<teacher_id>/<filename>/', views.download_quick_cal_doc, name='快速计算下载'),
    path('download/doc/<student_info>/<module_id>/', views.download_doc, name='下载文档文件'),
]