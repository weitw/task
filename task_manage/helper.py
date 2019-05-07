from django.shortcuts import render
from django.db import transaction  # 事务处理的方法
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import redirect, HttpResponse
from django.utils.http import urlquote
from django.http import FileResponse
from .models import *
import os
import json
import shutil
import time


BASE_DIR = os.getcwd()  # 项目根目录


def user_auth(func):
    """用来装饰，在每一个类之上，用于验证用户是否已经登录过，并且还判断用户类型"""

    def inner(request, *args, **kwargs):
        try:
            is_login = request.session.get('is_login')  # 查看登录状态
            if is_login:
                return func(request, *args, **kwargs)
            return redirect('/task/login/')
        except Exception as er:
            print("用户尚未登录: ", er)
            return redirect('/task/login/')
    return inner


def set_user_info(request, username, group):
    """
    设置登录或者注册用户的信息,username: 用户名,group: 所在班级
    """
    response = redirect('/task/index/')
    try:
        group_obj = Groups.objects.filter(name=group).first()  # 当前用户的班级对象
        with transaction.atomic():
            obj = Students.objects.filter(username=username, group_id=group_obj.id).first()  # 当前登录的用户对象
            request.session["group_id"] = group_obj.id  # 将班级的id存入django_session表
            request.session["user_id"] = obj.id  # 将当前登录的用户的id存入django_session表
        request.session["is_login"] = True  # 用户的登录状态
        return response
    except Exception as er:
        print("set_user_info出错：", er)
        return render(request, 'tasks/login.html', {"status": False, "login_error": "服务异常"})


def get_user_info(request):
    """获取用户的真实姓名,班级名和权限"""
    try:
        user_id = request.session.get('user_id')  # 用户id
        user_obj = Students.objects.filter(id=user_id).first()  # 用户对象
        name = user_obj.name  # 用户名
        # group_id = request.session.get('group_id')  # 用户所在班级的id
        group_id = user_obj.group_id  # 用户所在班级的id
        group_obj = Groups.objects.filter(id=group_id).first()  # 用户班级的对象
        return {"name": name, "group": group_obj.name, "permission": user_obj.permission}
    except Exception as er:
        print("获取用户真实姓名出错：", er)
        return {"name": "路人", "group": "路人", "permission": 0}


def all_username():
    """获取学生表中所有的学号"""
    try:
        username_obj = Students.objects.all()  # 所有学生的对象列表
        username = []
        print("所有学生的对象列表是：", username_obj)
        if username_obj:
            for user_obj in username_obj:
                username.append(user_obj.username)
            return username
        return None
    except Exception as er:
        print("获取所有账号出错：", er)
        return None


def all_group():
    """获取所有班级名"""
    try:
        group_list = Groups.objects.all()
        if group_list:
            groups = []  # 所有班级的列表
            for group in group_list:
                groups.append(group.name)
            return groups
        else:
            print("尚未有任何班级，返回None")
            return None
    except Exception as er:
        print("获取所有班级出错：", er)
        return None


def signup_post(request):
    """注册"""
    username = request.POST.get('username')  # 用户名（学号）
    password = request.POST.get('password')  # 密码
    password = make_password(password)  # 密码加密
    name = request.POST.get('name')  # 用户真实姓名
    group = request.POST.get('group')  # 班级
    try:
        usernames = all_username()

        group_obj = Groups.objects.filter(name=group).first()
        print("这儿")
        if usernames:
            if username in usernames:
                print("用户名已经存在，不允许重新注册")
                data = {
                    "status": False,
                    "signup_error": "用户名已经存在"
                }
                return render(request, 'tasks/signup.html', data)
        info = {
            "username": username,
            "password": password,
            "name": name,
            "group_id": group_obj.id
        }
        print(info)
        Students.objects.create(**info)  # 添加
        response = set_user_info(request, username, group)
        return response
    except Exception as er:
        print("注册过程出错：", er)
        data = {
            "status": False,
            "signup_error": "信息填写有误，请仔细检查"
        }
        return render(request, 'tasks/signup.html', data)


def login_post(request):
    """登录"""
    username = request.POST.get('username')  # 学号
    password = request.POST.get('password')  # 密码
    group = request.POST.get('group')  # 班级
    print("登录用户的信息：", username, make_password(password), group)
    try:
        group_obj = Groups.objects.filter(name=group).first()
        group_id = group_obj.id  # 班级的id
        obj = Students.objects.filter(username=username, group_id=group_id).first()
        if obj and check_password(password, obj.password):
            print("用户信息正确，可以登陆")
            response = set_user_info(request, username, group)
            return response
        else:
            print("用户名或密码错误")
            data = {
                "status": False,
                "login_error": "用户名或密码错误",
                "groups": all_group()
            }
            return render(request, 'tasks/login.html', data)
    except Exception as er:
        print("登录时获取学生表出错：", er)
        data = {
            "status": False,
            "login_error": "服务异常,请稍后再试",
            "groups": all_group()
        }
        return render(request, 'tasks/login.html', data)


def index_get(request):
    user_info = get_user_info(request)
    group_id = request.session.get('group_id')
    tests = Tests.objects.filter(group_id=group_id)
    data = {
        "status": True,
        "name": user_info.get("name"),  # 真实姓名
        "group": user_info.get("group"),  # 班级
        "tests": tests,
        "permission": user_info.get('permission')  # 用户权限
    }
    # print(data)
    return render(request, 'tasks/index.html', data)


def uploaded_get(request):
    """用户请求个人已经提交过的所有作业页面"""
    user_info = get_user_info(request)
    data = {
        "name": user_info.get('name'),
        "group": user_info.get('group'),
        "permission": user_info.get('permission')  # 用户权限
    }
    user_id = request.session.get('user_id')  # 当前登录的用户的id
    tasks = StuTest.objects.filter(stu_id=user_id)  # 当前登录的用户提交的所有作业
    data["status"] = True
    data["tasks"] = tasks
    return render(request, 'tasks/uploaded.html', data)


def uploaded_post(request):
    """用户要删除已提交的某个作业，只能删除数据库和media路径下的，不能删除tests_zip下的文件"""
    command = request.POST.get('command')
    if command:
        print("用户是要删除作业")
        try:
            test_id = int(request.POST.get('id'))  # 作业id
            test_obj = StuTest.objects.filter(id=test_id)  # 作业对象，现在还是一个列表
            test = test_obj.first()  # 该作业的对象，不是一个列表
            test_path = test.path  # 要删除的该作业保存的路径
            print("删除的作业目录是：", test_path, "id是：", test_id)
            if os.path.isfile(test_path):
                os.remove(test_path)  # 删除作业
                test.delete()  # 删除数据库中的内容
            data = {
                "status": True,
                "success": "删除作业成功"
            }
            return HttpResponse(json.dumps(data))
        except Exception as er:
            data = {
                "status": False,
                "error": "删除作业失败, 因为".format(er)
            }
            return HttpResponse(json.dumps(data))
    else:
        # 用户是要查看某个作业，也就是要下载。
        # 这个地方前端最好传过来的是path，这样就可以不用在后端构造文件的路径了，不过那样的话，文件路径就会暴露在前端，不安全。所以暂时就用构造这种方法
        test_path = request.POST.get('test')
        test_name = os.path.basename(test_path)  # 获取到文件名，包括扩展名
        try:
            file = open(test_path, 'rb')
            print("打开文件：", test_path)
            response = FileResponse(file)
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = 'attachment;filename={0}'.format(urlquote(test_name))
            return response
        except Exception as er:
            print("下载作业出错：", er)
            return HttpResponse('文件下载失败,原因是：{}'.format(er))


def upload_get(request):
    user_info = get_user_info(request)
    data = {
        "status": True,
        "name": user_info.get('name'),
        "group": user_info.get('group'),
        "permission": user_info.get('permission')  # 用户权限
    }
    return render(request, 'tasks/upload.html', data)


def upload_post(request):
    """上传作业"""
    print("*******上传作业********")
    file_obj = request.FILES.get("avatar")
    user_id = request.session.get('user_id')  # 用户id
    user = Students.objects.filter(id=user_id).first()
    user_info = get_user_info(request)  # 用户信息，包括姓名和班级
    group = user_info.get('group', "")
    print(file_obj.name)
    group_path = os.path.join(BASE_DIR, 'media/' + group)  # 用户的班级的目录
    tests = os.listdir(group_path)  # 得到该班级下的所有作业，type->list,也就是用户要提交作业要存放的目录
    student_obj = Students.objects.filter(id=user_id).first()  # 该登录用户的对象
    try:
        stu_num = student_obj.username  # 登录用户的学号，用户只能提交自己的作业，以免有人讲文件名修改为别人的，会覆盖别人的作业，所以作业名中一定要包含自己的学号
    except Exception as er:
        print("学生对象获取失败：", er)
        stu_num = None
    for test in tests:
        if test in file_obj.name and stu_num in file_obj.name:
            """作业名和当前用户的学号在文件名中，允许提交"""
            try:
                test_obj = Tests.objects.filter(name=test).first()  # 当前提交的作业的对象
                test_id = test_obj.id  # 作业id
                print("目录'{}'包含在作业'{}'中".format(test, file_obj.name))
                # filename = str(hash(group+file_obj.name+str(time.time)))  # 存储在目录中的文件名用hash表示，以免文件名重复
                upload_to = os.path.join(group_path, test, file_obj.name)  # 作业保存目录是作业所在的目录+文件名
                print("作业保存目录是:", upload_to)
                old_test = StuTest.objects.filter(stu_id=user_id, test_id=test_id)  # 该学生提交的该作业对象
                count = 1  # 作业提交的次数，默认为1，如果用户是第一次提交该作业，那么次数就从1开始，如果不是，那么就先获取之前提交的count数，再加1
                if old_test:
                    print("用户已经提交过该作业了，现在先删除旧的作业，再更新新的作业")
                    count = old_test.first().count+1  # 作业提交的次数
                    old_test.delete()  # 删除数据库中旧的记录
                info = {
                    "test_id": test_id,
                    "stu_id": user_id,
                    "filename": file_obj.name,  # 这儿存储的是文件的真实名字，而不是hash得到的文件名
                    "path": upload_to,
                    "count": count
                }
                with transaction.atomic():
                    # StuTest.objects.filter(stu_id=user_id, test_id=test_id).update(count=the_test_count)
                    all_count = user.count + 1  # 作业提交的总次数（是所有的作业的累加次数）
                    Students.objects.filter(id=user_id).update(count=all_count)  # 更新数据中用户提交的作业次数
                    StuTest.objects.create(**info)  # 向学生作业表中添加数据
                    with open(upload_to, 'wb') as f:
                        # print("数据库库操作没问题，可以保存用户的作业至本地")
                        for item in file_obj.chunks():
                            f.write(item)
                data = {
                    "status": True,
                    "success": "作业提交成功!"
                }
            except Exception as er:
                print("上传作业出错：", er)
                data = {
                    "status": False,
                    "error": "上传作业失败，原因:{}".format(er)
                }
            return HttpResponse(json.dumps(data))
    data = {
        "status": False,
        "error": "上传作业失败，请检查你的作业名是否规范"
    }
    return HttpResponse(json.dumps(data))


def group_manage_get(request):
    """View all groups in Group table"""
    user_info = get_user_info(request)
    groups = Groups.objects.all()
    data = {
        "status": True,
        "groups": groups,
        "name": user_info.get('name'),
        "group": user_info.get('group'),
        "permission": user_info.get('permission')  # current user's permission(权限)
    }
    # print(data)
    return render(request, 'tasks/group_list.html', data)


def group_manage_post(request):
    """
    User will edit group's information or delete group
    :return: json
    """
    command = request.POST.get('command')
    if command == "Modify":
        try:
            print("Edit group's information, include group's name and number of the group")
            name = request.POST.get('name')
            amount = request.POST.get('amount')  # the number of students in the group
            group_id = request.POST.get('group_id')  # the group's id in Group table
            groups = all_group()  # all group's object, type:list
            old_group = Groups.objects.filter(id=group_id).first().name  # 用户要修改的班级原来的名字
            # groups.remove(old_group)  # 除去该班级名
            if name == old_group:
                # 班级的名字和之前的一样，没有修改，所以只修改班级人数
                Groups.objects.filter(id=group_id).update(amount=amount)  # 修改班级人数
                data = {
                    "status": True,
                    "modify_success": "修改成功"
                }
                print("修改班级人数成功")
                return HttpResponse(json.dumps(data))
            # 班级名也跟着改了，所以要验证一下要修改的班级名是否已经存在
            if name not in groups:
                # 要修改的班级名未被占用，允许修改
                # print("允许修改")
                try:
                    media_path = os.path.join(BASE_DIR, 'media/' + old_group)  # 旧的班级名称
                    if not os.path.isdir(media_path):
                        os.makedirs(media_path)  # 如果该路径丢失，则先创建
                    new_media_path = os.path.join(BASE_DIR, 'media/' + name)  # 新的班级名称
                    zip_path = os.path.join(BASE_DIR, 'tests_zip', old_group)  # 旧的班级打包文件存放的路径
                    if not os.path.isdir(zip_path):
                        os.makedirs(zip_path)  # 如果该路径丢失，则先创建
                    new_zip_path = os.path.join(BASE_DIR, 'tests_zip', name)  # 新的班级打包文件存放的路径
                    with transaction.atomic():
                        # 启动事务
                        Groups.objects.filter(id=group_id).update(name=name, amount=amount)
                        os.rename(media_path, new_media_path)  # 修改文件名
                        os.rename(zip_path, new_zip_path)  # 修改文件名
                    data = {
                        "status": True,
                        "modify_success": "修改成功"
                    }
                    print("修改班级和人数成功，服务器中各班级对应的目录页修改了")
                    return HttpResponse(json.dumps(data))
                except Exception as er:
                    print("修改班级名过程出错: ", er)
                    data = {
                        "status": False,
                        "modify_error": "修改失败"
                    }
                    return HttpResponse(json.dumps(data))
            else:
                print("班级'{}'已经存在,修改失败".format(name))
                data = {
                    "status": False,
                    "modify_error": "班级'{}'已经存在".format(name)
                }
                return HttpResponse(json.dumps(data))
        except Exception as er:
            print("修改班级出错：", er)
            data = {
                "status": False,
                "modify_error": er
            }
            return HttpResponse(json.dumps(data))
    if command == "Delete":
        print("用户要删除")
        group_id = request.POST.get('group_id')  # 用户选择要删除的班级id
        try:
            group = Groups.objects.filter(id=group_id).first().name  # 班级名字
            media_path = os.path.join(BASE_DIR, 'media/' + group)  # 该班级上传作业的路径
            zip_path = os.path.join(BASE_DIR, 'tests_zip', group)  # 该班级打包文件的路径
        except Exception as er:
            print("查找要删除的班级失败：", er)
            return HttpResponse(json.dumps({"status": False, "del_error": "服务器响应出错，请稍后再试"}))
        try:
            Groups.objects.filter(id=group_id).delete()
            if os.path.exists(media_path):
                shutil.rmtree(media_path)  # 班级删除了，那么该班级的目录以及子目录都应删除
            if os.path.exists(zip_path):
                shutil.rmtree(zip_path)  # 该班级的打包文件的路径也要删除
            data = {
                "status": True,
                "del_success": "删除班级成功"
            }
            return HttpResponse(json.dumps(data))
        except Exception as er:
            print("删除班级失败：", er)
            data = {
                "status": False,
                "del_error": er
            }
            return HttpResponse(json.dumps(data))


def add_group_get(request):
    """admin want to get add_group page"""
    user_info = get_user_info(request)
    data = {
        "status": True,
        "name": user_info.get('name'),
        "group": user_info.get('group'),
        "permission": user_info.get('permission')  # 用户权限
    }
    return render(request, 'tasks/add_group.html', data)


def add_group_post(request):
    """增加班级的post处理"""
    group = request.POST.get('group')
    amount = request.POST.get('amount')
    # print(group)
    user_info = get_user_info(request)
    data = {
        "name": user_info.get('name'),
        "group": user_info.get('group'),
        "permission": user_info.get('permission')  # 用户权限
    }
    groups = all_group()
    if not groups or (groups and group not in groups):
        try:
            media_path = os.path.join(BASE_DIR, 'media/' + group)  # 班级作业上传的路径
            zip_path = os.path.join(BASE_DIR, 'tests_zip', group)  # 打包文件所存放的路径
            Groups.objects.create(name=group, amount=amount)  # 创建班级
            os.makedirs(media_path)
            os.makedirs(zip_path)
            data["status"] = True
            data["add_success"] = "添加成功"
            print("添加班级成功，给用户返回>>", data)
            return render(request, 'tasks/add_group.html', data)
        except Exception as er:
            print("添加班级失败>>", er)
            data["status"] = True
            data["add_error"] = "服务器异常,添加失败"
            return render(request, 'tasks/add_group.html', data)
    else:
        print("班级已经存在，不允许再增加")
        data["status"] = False
        data["add_error"] = "班级已经存在，添加失败"
        return render(request, 'tasks/add_group.html', data)


def modify_get(request):
    """修改资料的get请求"""
    user_info = get_user_info(request)
    data = {
        "name": user_info.get('name'),
        "group": user_info.get('group'),
        "permission": user_info.get('permission')  # 用户权限
    }
    user_id = request.session.get('user_id')
    user_obj = Students.objects.filter(id=user_id).first()
    data["student"] = user_obj  # 该学生的对象
    return render(request, 'tasks/modify.html', data)


def modify_post(request):
    """处理修改资料的请求"""
    name = request.POST.get('name')  # 学生姓名
    password = request.POST.get('password')  # 密码
    username = request.POST.get('username')  # 学号
    age = request.POST.get('age')  # 年龄
    gender = request.POST.get('gender')  # 性别
    user_id = request.session.get('user_id')
    current_user = Students.objects.filter(id=user_id).first()
    current_username = current_user.username
    info = {
        "name": name,
        "age": age,
        "gender": gender
    }
    stu = Students.objects.filter(username=username)
    if username == current_username or (username != current_username and not stu):
        """
        这儿的意思是：如果表单中的username与数据库中该用户的username一致，说明用户没有要修改用户名。或者，表单中的username不等于数据中的
        username，但是他要修改的这个学号目前未被占用，所以这两种情况都允许修改
        """
        print("允许修改")
        if not check_password(password, current_user.password):
            print("表单中密码和数据库中的密码不一样，表示用户要修改密码")
            info["password"] = make_password(password)
        Students.objects.filter(id=user_id).update(**info)
        data = {
            "status": True,
            "result": "修改成功",
            "name": name  # 返回name，如果为修改过，那么name不变；如果修改过，那么该name就是用户新的名字
        }
        return HttpResponse(json.dumps(data))
    else:
        print("修改失败")
        data = {
            "status": False,
            "result": "用户名已经存在，不允许修改"
        }
        return HttpResponse(json.dumps(data))


def student_info_get(request):
    """展示该用户所在班级中的所有学生的基本信息，根据当前用户的权限，前端会显示不同的信息，修改信息的范围也会不一样"""
    user_info = get_user_info(request)
    data = {
        "name": user_info.get('name'),
        "group": user_info.get('group'),
        "permission": user_info.get('permission')  # 用户权限
    }
    group_id = request.session.get('group_id')  # 当前管理员所在的班级
    students = Students.objects.filter(group_id=group_id)  # 所在班级的所有学生
    data["students"] = students
    return render(request, 'tasks/students.html', data)


def student_info_post(request):
    """修改学生信息（权限不同，可修改的内容也不同）或者删除学生"""
    command = request.POST.get('command')
    try:
        stu_id = int(request.POST.get('id'))  # 要修改的学生的id
        permission = int(request.POST.get('permission'))  # 要修改的学生的权限
    except Exception as er:
        print("获取学生id失败: ", er)
        return HttpResponse(json.dumps({"status": False}))
    if command == "Modify":
        """管理员修改学生信息"""
        stu_obj = Students.objects.filter(id=stu_id).first()
        name = request.POST.get('name')
        username = request.POST.get('username')
        info = {
            "name": name,
            "username": username,
            "permission": permission
        }
        stu = Students.objects.filter(username=username)
        if username == stu_obj.username or (username != stu_obj.username and not stu):
            """
            这儿的意思是：如果表单中的username与数据库中该用户的username一致，说明用户没有要修改用户名。或者，表单中的username不等于数据中的
            username，但是他要修改的这个学号目前未被占用，所以这两种情况都允许修改
            """
            print("允许修改")
            Students.objects.filter(id=stu_id).update(**info)
            data = {
                "status": True,
                "modify_success": "修改成功",
            }
            return HttpResponse(json.dumps(data))
        else:
            print("修改失败")
            data = {
                "status": False,
                "modify_error": "用户名已经存在，不允许修改"
            }
            return HttpResponse(json.dumps(data))

        # if username in usernames:
        #     print("学号已经存在，不可修改")
        #     data = {
        #         "status": False,
        #         "modify_error": "学号已经存在，修改失败"
        #     }
        # else:
        #     try:
        #         print(name, username, id)
        #         Students.objects.filter(id=stu_id).update(name=name, username=username, permission=permission)
        #         data = {
        #             "status": True,
        #             "modify_success": "修改成功"
        #         }
        #     except Exception as err:
        #         print("修改学生信息失败：", err)
        #         data = {
        #             "status": False,
        #             "modify_error": err
        #         }
        # return HttpResponse(json.dumps(data))
    if command == "Delete":
        print("管理员要删除学生")
        try:
            Students.objects.filter(id=stu_id).delete()
            data = {
                "status": True,
                "del_success": "删除学生成功"
            }
        except Exception as er:
            print("删除学生失败:", er)
            data = {
                "status": False,
                "del_error": "删除学生失败，原因是：".format(er)
            }
        # print(data)
        return HttpResponse(json.dumps(data))


def pack_get(request):
    """作业管理的get 请求页面"""
    user_info = get_user_info(request)  # 获取用户名和班级名
    media_path = os.path.join(BASE_DIR, 'media', user_info.get('group'))  # 班级所在的目录，例如B160905
    group_id = request.session.get('group_id')  # 班级的id
    tests = Tests.objects.filter(group_id=group_id)  # 获取到该班级的作业对象的一个列表
    stu_files = []
    for test in tests:
        stu_files.append(os.listdir(os.path.join(media_path, test.name)))  # 每个作业下学生提交的作业的列表
    # stu_files：[['B16090532魏廷万医学信号处理.docx', '医学信号处理.html', '魏廷万B16090501医学信号处理.txt'], ['B16090532魏廷万脑机接口.docx']]
    data = {
        "name": user_info.get('name'),
        "group": user_info.get('group'),
        "tests": tests,
        "stu_files": stu_files,
        "permission": user_info.get('permission')  # 用户权限
    }
    # print(data)
    return render(request, 'tasks/test_manage.html', data)


def pack_test(request, tid, test_obj):
    """处理post请求，打包作业。每次打包完都要将is_download改为0，这样表示刚刚打包的文件未下载"""
    print("用户要打包的作业id是：", tid)
    test_name = test_obj.name  # 作业名字
    user_info = get_user_info(request)
    group = user_info.get('group')  # 管理员所在班级的名字，根据这个找到班级的目录
    media_path = os.path.join(BASE_DIR, 'media', group)  # 该学生所在班级作业上传的目录
    if not os.path.exists(media_path):
        os.makedirs(media_path)  # 若不存在，则创建
    test_path = os.path.join(media_path, test_name)  # 要打包的作业的目录
    zip_path = os.path.join(BASE_DIR, 'tests_zip', group)  # 打包文件所存放的路径
    if not os.path.exists(zip_path):
        os.makedirs(zip_path)  # 如不存在，则创建
    pack_save_path = os.path.join(zip_path, test_name)  # 作业打包之后存在该目录下，每个班都有相应的该目录
    try:
        zip_path = shutil.make_archive(pack_save_path, 'zip', test_path)  # 作业打包后的完整路径， zip文件就在该作业下
        print("文件打包的结果：", zip_path)
        data = {
            "status": True,
            "success": "打包成功"
        }
        Tests.objects.filter(name=test_name).update(is_download=False)
        return HttpResponse(json.dumps(data))
    except Exception as er:
        print("打包文件时出错：", er)
        data = {
            "status": False,
            "error": "文件打包失败",
        }
        return render(request, 'tasks/500.html', data)


def delete_test(tid, test_obj, group_obj):
    """
    管理员要删除作业
    如果作业目录下尚未有提交的作业，那么可以直接删除。
    但是如果有作业，那么就分情况：1. 有作业，但是已经下载过，则允许删除。2. 有作业，但是未下载过，则不允许删除
    return: json data
    """
    print("用户要删除作业")
    group = group_obj.name  # 获取班级名
    is_download = test_obj.is_download  # 作业下载情况
    path = os.path.join(BASE_DIR, 'media', group, test_obj.name)  # 该作业的目录
    zip_path = os.path.join(BASE_DIR, 'tests_zip', group, test_obj.name + '.zip')  # 该作业打包文件所存放的路径
    if is_download or not os.listdir(path):
        # 已经下载或者目录下没有作业，允许直接删除
        try:
            with transaction.atomic():
                Tests.objects.filter(id=tid).delete()  # 数据库中删除该作业
                shutil.rmtree(path)  # 递归的删除该作业
            if os.path.exists(zip_path):
                os.remove(zip_path)  # 删除打包文件
            data = {
                "status": True,
                "success": "删除成功"
            }
        except Exception as er:
            print("作业删除失败：", er)
            data = {
                "status": False,
                "error": "删除作业失败,原因是{}".format(er)
            }
        return HttpResponse(json.dumps(data))
    else:
        print("作业不为空，并且也没有下载过作业,不允许删除")
        data = {
            "status": False,
            "error": "检测到该作业未下载,请先下载,再尝试删除"
        }
        return HttpResponse(json.dumps(data))


def add_test_get(request):
    """作业管理的get请求页面，也就是作业的列表"""
    user_info = get_user_info(request)
    data = {
        "name": user_info.get("name"),
        "group": user_info.get("group"),
        "permission": user_info.get('permission')  # 用户权限
    }
    return render(request, 'tasks/add_test.html', data)


def add_test_post(request):
    """作业管理的post请求,增加作业"""
    user_info = get_user_info(request)
    test_name = request.POST.get('name')  # 作业名
    deadline = request.POST.get('deadline')  # 截止时间
    details = request.POST.get("details")  # 作业补充说明
    group_id = request.session.get("group_id")  # 获取当前的班级
    tests_obj = Tests.objects.filter(group_id=group_id)
    group = user_info.get('group')  # 班级名
    data = {
        "name": user_info.get('name'),
        "group": group,
        "permission": user_info.get('permission')  # 用户权限
    }
    tests = []  # 该班级已经布置过的作业列表
    for test in tests_obj:
        tests.append(test.name)
    if test_name in tests:
        print("作业已经存在，不能添加")
        data["status"] = False
        data["add_error"] = "作业已经存在"
        return render(request, 'tasks/add_test.html', data)
    else:
        info = {
            "name": test_name,
            "deadline": deadline,
            "group_id": group_id
        }
        if details:
            info["details"] = details
        try:
            path = os.path.join(BASE_DIR, 'media', group, test_name)
            with transaction.atomic():
                # 使用事务
                Tests.objects.create(**info)  # 创建新作业
                os.makedirs(path)  # 创建新作业的目录
            data["status"] = True
            data["add_success"] = "添加成功"
            return render(request, 'tasks/add_test.html', data)
        except OSError as er:
            print("用户在添加作业时，创建作业目录时出错：", er)
            data["status"] = False
            data["add_error"] = "作业已经存在"
            return render(request, 'tasks/add_test.html', data)
        except Exception as er:
            print("添加作业失败：", er)
            data["status"] = False
            data["add_error"] = er
            return render(request, 'tasks/add_test.html', data)



