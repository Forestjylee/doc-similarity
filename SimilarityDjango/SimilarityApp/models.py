from django.db import models

# Create your models here.
# 数据库结构设计

class User(models.Model):

    name = models.CharField(max_length=20)               # 姓名
    account = models.CharField(max_length=20)            # 账户名
    password = models.CharField(max_length=20)           # 密码
    role = models.BooleanField(default=False)            # 学生为False
    unit = models.CharField(max_length=20)               # 学院,班级信息
    createtime = models.DateTimeField(auto_now_add=True) # 创建时间
    def __str__(self):
        return self.name    # 在管理界面显示的名字
    class Meta:
        db_table = 'user'        # 设置在MySQL中数据表的名称
        ordering = ['id']        # 设置栏目显示的顺序(升序)

class UserRelation(models.Model):

    stu_id = models.IntegerField()    # 学生id
    tea_id = models.IntegerField()    # 老师id
    def __str__(self):
        return '%s-*s'%(self.stu_id, self.tea_id)    # 学生id对应老师id
    class Meta:
        db_table = 'user_relation'
        ordering = ['id']


class Project(models.Model):

    name = models.CharField(max_length=50)                  # 课程名称
    tea_id = models.IntegerField()                          # 课程所属的老师
    path = models.CharField(max_length=100)                 # 课程文件所在路径
    end_date = models.DateField()                           # 课程结束日期
    createtime = models.DateTimeField(auto_now_add=True)    # 创建时间
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'project'
        ordering = ['id']


class Module(models.Model):

    name = models.CharField(max_length=50)                               # 单元名称
    description = models.CharField(max_length=200)                       # 单元描述
    path = models.CharField(max_length=100)                              # 单元所在路径
    filetype = models.CharField(max_length=20)                           # 文件类型
    end_date = models.DateField()                                        # 结束时间
    createtime = models.DateTimeField(auto_now_add=True)                 # 创建时间
    project = models.ForeignKey(Project, on_delete=models.CASCADE)     # 外键(单元所属的课程)
    def __str__(self):
        return '%s-%s'%(self.project, self.name)
    class Meta:
        db_table = 'module'
        ordering = ['id']