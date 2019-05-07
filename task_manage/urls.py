from task_manage import views
from django.urls import path
# from task import settions

urlpatterns = [
    path('', views.Index.as_view(), name='index'),  # 主页
    path('login/', views.Login.as_view(), name='login'),  # 登录
    path('signup/', views.Signup.as_view(), name='signup'),  # 注册
    path('upload/', views.Upload.as_view(), name='upload'),  # 上传作业
    path('uploaded/', views.Uploaded.as_view(), name='uploaded'),  # 个人所上传的作业
    path('modify/', views.Modify.as_view(), name='modify'),  # 修改用户资料
    path('all_uploaded/', views.AllUploaded.as_view(), name='all_uploaded'),  #
    path('students/', views.StudentInfo.as_view(), name='students'),  # 学生信息列表
    path('add_task/', views.AddTest.as_view(), name='add_task'),  # 增加作业
    path('manage/', views.TestManage.as_view(), name='test_manage'),  # 作业打包或者删除
    path('download/', views.Download.as_view(), name='download'),  # 作业打包或者删除
    path('recycle/', views.Index.as_view(), name='recycle'),
    path('groups_manage/', views.GroupManage.as_view(), name="groups_manage"),  # 班级管理
    path('add_group/', views.AddGroup.as_view(), name="add_group"),  # 添加班级
    path('logout/', views.Logout.as_view(), name='logout'),  # 注销
] # + static(settions.STATIC_URL, document_root=settings.STATIC_ROOT)
