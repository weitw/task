from django.db import models
# Create your models here.


class Students(models.Model):
    """学生表"""
    username = models.CharField(max_length=30, null=False)  # 学号
    password = models.CharField(max_length=100)  # 密码
    name = models.CharField(max_length=50, null=False)  # 姓名
    age = models.CharField(max_length=10, default="18")  # 年龄
    gender = models.CharField(max_length=10, default="男")  # 性别
    # group = models.CharField(max_length=50)  # 班级
    group_id = models.IntegerField()  # 班级id
    count = models.IntegerField(default=0)  # 学生的作业数目
    details = models.TextField(default="")  # 介绍
    permission = models.IntegerField(default=4)  # 学生的权限
    # """
    # '0'：尚未被认证的用户
    # '1': 普通用户
    # '4'：普通管理员（能管理学生和作业）
    # '6': 待定
    # '7'：超级管理员"""

    class Meta:
        db_table = "student"


class Permission(models.Model):
    """暂时用不到"""
    number = models.CharField(max_length=50)  # 权限的编号
    name = models.CharField(max_length=100)  # 权限的名字

    class Meta:
        db_table = "permission"


class Tests(models.Model):
    """作业表"""
    group_id = models.IntegerField(default=0)  # 指明是哪个班的作业
    name = models.CharField(max_length=100)  # 作业名
    release_time = models.DateTimeField(auto_now_add=True)  # 作业发布时间，自动创建
    deadline = models.CharField(max_length=100, default="无")  # 截止日期
    is_download = models.BooleanField(default=False)  # 作业是否已经被管理员下载，默认是没有被下载
    result_to = models.CharField(max_length=100, default="")  # 打包文件之后，打包的文件存储的目录
    details = models.TextField(default="")  # 作业描述，比如注意事项之类的

    class Meta:
        db_table = "Test"


class StuTest(models.Model):
    """学生提交的作业信息"""
    test_id = models.IntegerField()  # 作业对应的id
    stu_id = models.IntegerField()  # 学生的id
    group = models.CharField(max_length=50, default="B160905")  # 作业所属班级
    path = models.CharField(max_length=200, null=True)  # 作业保存路径
    filename = models.CharField(max_length=150, null=True)  # 文件名
    count = models.IntegerField(default=1)  # 上传的次数
    time = models.DateTimeField(auto_now_add=True)  # 作业上传的时间

    class Meta:
        db_table = "stu_test"


class Groups(models.Model):
    """学生所在的组，也就是班级"""
    name = models.CharField(max_length=50)  # 班级名字
    amount = models.IntegerField(default=0)  # 班级人数

    class Meta:
        db_table = "group"

