from django.views import View
from django.utils.decorators import method_decorator
from .helper import *

# Create your views here.


class Login(View):
    """登录"""
    def get(self, request):
        is_login = request.session.get('is_login')
        if is_login:
            # 用户已经登录了，那么直接回到主页
            return redirect('/task/index/')
        groups = all_group()
        data = {
            "status": True,
            "groups": groups
        }
        return render(request, 'tasks/login.html', data)

    def post(self, request):
        response = login_post(request)
        return response


class Signup(View):
    """注册"""
    def get(self, request):
        groups = all_group()
        return render(request, 'tasks/signup.html', {"status": True, "groups": groups})

    def post(self, request):
        response = signup_post(request)
        return response


@method_decorator(user_auth, name='dispatch')
class Index(View):
    def get(self, request):
        # try:
        #     print("测试一：")
        #     with transaction.atomic():
        #         Students.objects.filter(id=1).update(fname="测试一")
        #     path = os.path.join(BASE_DIR, '测试1')  # 数据库先失败，验证目录是否能创建
        #     os.mkdir(path)
        # except Exception as er:
        #     print("测试一出错：", er)
        # try:
        #     print("测试二：")
        #     with transaction.atomic():
        #         Students.objects.filter(id=1).update(name="测试二")
        #     path = os.path.join(BASE_DIR, '测试2/c/aaa')  # 数据库成功，目录创建失败，验证数据库是否能回滚
        #     os.mkdir(path)
        # except Exception as er:
        #     print("测试二出错：", er)
        # try:
        #     print("测试三：")
        #     with transaction.atomic():
        #         Students.objects.filter(id=1).update(gender="测试三")
        #         path = os.path.join(BASE_DIR, '测试3/c/aaa')  # 数据库成功，目录创建失败，验证数据库是否能回滚
        #         os.mkdir(path)
        # except Exception as er:
        #     print("测试三出错：", er)
        # try:
        #     print("测试四：")
        #     with transaction.atomic():
        #         path1 = os.path.join(BASE_DIR, '测试四')
        #         os.mkdir(path1)
        #         Students.objects.filter(id=1).update(ggender="测试四")
        # except Exception as er:
        #     print("测试三出错：", er)
        response = index_get(request)
        return response

    def post(self, request):
        return render(request, 'tasks/index.html')


@method_decorator(user_auth, name='dispatch')
class Uploaded(View):
    """普通学生获取他已经上传的作业列表"""
    def get(self, request):
        response = uploaded_get(request)
        return response

    def post(self, request):
        response = uploaded_post(request)
        return response


@method_decorator(user_auth, name='dispatch')
class Upload(View):
    """作业上传"""
    def get(self, request):
        response = upload_get(request)
        return response

    def post(self, request):
        response = upload_post(request)
        return response


@method_decorator(user_auth, name='dispatch')
class GroupManage(View):
    """班级管理(修改或删除)"""
    def get(self, request):
        """获取班级列表"""
        response = group_manage_get(request)
        return response

    def post(self, request):
        """修改或删除班级或增加班级"""
        response = group_manage_post(request)
        return response


@method_decorator(user_auth, name='dispatch')
class AddGroup(View):
    """增加班级"""
    def get(self, request):
        response = add_group_get(request)
        return response

    def post(self, request):
        response = add_group_post(request)
        return response


@method_decorator(user_auth, name='dispatch')
class Modify(View):
    """修改用户资料"""
    def get(self, request):
        response = modify_get(request)
        return response

    def post(self, request):
        response = modify_post(request)
        return response


@method_decorator(user_auth, name='dispatch')
class AllUploaded(View):
    """显示班级所有已提交的作业情况"""
    def get(self, request):
        user_info = get_user_info(request)
        name = user_info.get('name')
        group = user_info.get('group')
        all_test = StuTest.objects.filter(group=group)  # 改班级已提交的所有作业
        data = {
            "name": name,
            "group": group,
            "tests": all_test,
            "permission": user_info.get('permission')  # 当前用户的权限
        }
        return render(request, 'tasks/stutests.html', data)


@method_decorator(user_auth, name='dispatch')
class StudentInfo(View):
    """学生信息列表(管理员可修改学生的基本信息，包括简单的修改和删除该学生)"""
    def get(self, request):
        response = student_info_get(request)
        return response

    def post(self, request):
        response = student_info_post(request)
        return response


@method_decorator(user_auth, name='dispatch')
class Download(View):
    """作业下载"""
    def get(self, request):
        """将文件的路径返回，提供下载的链接"""
        user_info = get_user_info(request)
        group_id = request.session.get('group_id')
        group_obj = Groups.objects.filter(id=group_id).first()
        group_name = group_obj.name  # 班级名字
        path = os.path.join(BASE_DIR, 'tests_zip', group_name)
        if not os.path.exists(path):
            os.makedirs(path)
        data = {
            "files": os.listdir(path),
            "name": user_info.get('name'),
            "group": user_info.get('group'),
            "permission": user_info.get('permission'),
            "file_root": "tests_zip/"+group_name  # 打包文件所在的根目录，这样直接在前端构造打包文件文件的链接，而不用在这儿用循环去构造，可以减少循环的次数
        }
        return render(request, 'tasks/download.html', data)

    def post(self, request):
        """下载文件"""
        test_path = request.POST.get('test_path')  # 要下载的文件相对路径，从tests_zip开始
        print("要下载的文件路径：", test_path)
        try:
            path = os.path.join(BASE_DIR, test_path)
            if os.path.exists(path):
                # 若存在，说明返回的是已经打包好的文件路径
                path = path.replace('//', '/')
                path = path.replace('\\', '/')
                file = open(path, 'rb')
                print("打开文件：", path)
                response = FileResponse(file)
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = 'attachment;filename={0}'.format(urlquote(os.path.split(path)[1]))
                """获取作业名，然后根据这个作业名，将is_download改为True"""
                zip_test_name = os.path.basename(path)  # 得到类似"医学信号处理.zip"这个字符串
                test_name = zip_test_name.replace('.zip', '')  # 得到"医学信号处理"
                Tests.objects.filter(name=test_name).update(is_download=True)
                return response
            else:
                print("要下载的文件不存在")
                return HttpResponse('文件不存在,下载失败')
        except Exception as er:
            print("下载作业出错：", er)
            return HttpResponse('文件下载失败,原因是：{}'.format(er))


@method_decorator(user_auth, name='dispatch')
class TestManage(View):
    """作业打包或者删除"""
    def get(self, request):
        response = pack_get(request)
        return response

    def post(self, request):
        try:
            tid = request.POST.get("test_id")  # 要处理的作业id
            print(tid, type(tid))
            tid = int(tid)
        except:
            data = {
                "status": False,
                "error": "编号出错"
            }
            return HttpResponse(json.dumps(data))
        command = request.POST.get('command')
        test_obj = Tests.objects.filter(id=tid).first()  # 获取作业对象
        group_id = request.session.get('group_id')  # 获取班级id
        group_obj = Groups.objects.filter(id=group_id).first()  # 获取班级的对象
        if command == "Delete":
            response = delete_test(tid, test_obj, group_obj)
        else:
            response = pack_test(request, tid, test_obj)
        return response


@method_decorator(user_auth, name='dispatch')
class AddTest(View):
    """添加作业"""
    def get(self, request):
        response = add_test_get(request)
        return response

    def post(self, request):
        response = add_test_post(request)
        return response


class Logout(View):
    def get(self, request):
        response = redirect('/task/login/')  # 重定向
        request.session.flush()  # 删除所有的session
        print("用户注销")
        return response
