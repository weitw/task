import re
from django import forms
from django.core.exceptions import ValidationError

# Create your models here.


def mobile_validate(value):
    mobile_re = re.compile(r'^(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$')
    if not mobile_re.match(value):
        raise ValidationError('手机号码格式错误')


# 定义验证规则
class MyForm(forms.Form):
    user = forms.CharField(required=True, error_messages={'required': '用户名不能为空.'})
    pwd = forms.CharField(required=True,
                          min_length=6,  # 最少长度
                          max_length=10,  # 最大长度
                          error_messages={'required': '密码不能为空.', 'min_length': "至少6位"},  # 不合法提示信息
                          widget=forms.PasswordInput)  # 输入类型

    num = forms.IntegerField(error_messages={'required': '数字不能空.', 'invalid': '必须输入数字'})
    email = forms.EmailField(required=True, error_messages={'required': '邮箱不能空.', 'invalid': '邮箱格式错误'})
    # 应用自定义验证规则
    phone = forms.CharField(required=True, validators=[mobile_validate, ], error_messages={'required': '请填写手机号'})
