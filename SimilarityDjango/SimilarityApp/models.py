from django.db import models


# Create your models here.
# 数据库结构设计


class Student(models.Model):

    name = models.CharField(max_length=20, verbose_name="学生姓名")                              # 姓名
    account = models.CharField(max_length=20, verbose_name="账户名")                             # 账户名
    password = models.CharField(max_length=20, verbose_name="密码")                              # 密码
    unit = models.CharField(max_length=20, verbose_name="学院班级信息", blank=True)               # 学院,班级信息
    createtime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")                 # 创建时间
    def __str__(self):
        return self.name    # 在管理界面显示的名字
    class Meta:
        db_table = 'student'        # 设置在MySQL中数据表的名称
        ordering = ['id']        # 设置栏目显示的顺序(升序)

class Teacher(models.Model):

    name = models.CharField(max_length=20, verbose_name="老师姓名")                              # 姓名
    account = models.CharField(max_length=20, verbose_name="账户名")                             # 账户名
    password = models.CharField(max_length=20, verbose_name="密码")                              # 密码
    unit = models.CharField(max_length=20, verbose_name="学院班级信息", blank=True)               # 学院,班级信息
    createtime = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")                 # 创建时间
    def __str__(self):
        return self.name    # 在管理界面显示的名字
    class Meta:
        db_table = 'teacher'        # 设置在MySQL中数据表的名称
        ordering = ['id']           # 设置栏目显示的顺序(升序)

class UserRelation(models.Model):

    # 使用id而不用student外键是因为防止有学生的名字一样不容易区分
    stu_id  = models.IntegerField(blank=True, verbose_name="学生id(选填)")                               # 学生id
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="老师", null=True)      # 外键(学生所属的老师)
    def __str__(self):
        return '%s-%s'%(self.teacher, self.stu_id)    # 老师对应学生id
    class Meta:
        db_table = 'user_relation'
        ordering = ['id']

class ProjectUser(models.Model):

    project_id = models.IntegerField(verbose_name="项目id")
    stu_id = models.IntegerField(verbose_name="参与学生id")
    def __str__(self):
        return '%s-%s'%(self.project_id, self.stu_id)  # 项目id对应学生id
    class Meta:
        db_table = 'project_user'
        ordering = ['project_id', 'stu_id']

class Project(models.Model):

    name = models.CharField(max_length=50, verbose_name="项目名称")                            # 课程名称
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="所属老师", null=True)    # 外键(课程所属老师|管理员)
    path = models.CharField(max_length=100)                                                   # 课程文件所在路径
    end_date = models.DateField(blank=True, verbose_name="结束日期")                           # 课程结束日期
    createtime = models.DateTimeField(auto_now_add=True)                                      # 创建时间
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'project'
        ordering = ['id']


class Module(models.Model):

    name = models.CharField(max_length=50, verbose_name="子项目名称")                             # 单元名称
    description = models.CharField(max_length=200, verbose_name="子项目描述")                     # 单元描述
    path = models.CharField(max_length=100)                                                      # 单元所在路径
    filetype = models.CharField(max_length=20, default="doc|docx")                               # 文件类型
    end_date = models.DateField(blank=True, verbose_name="截止日期")                              # 结束时间
    createtime = models.DateTimeField(auto_now_add=True)                                         # 创建时间
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="所属项目", null=True)       # 外键(单元所属的课程)
    def __str__(self):
        return '%s-%s'%(self.project, self.name)
    class Meta:
        db_table = 'module'
        ordering = ['id']