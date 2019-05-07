from django import template

register = template.Library()

# 自定义过滤器


@register.filter(name='cut')
def cut(L, index):
    """返回列表List的索引index对应的值"""
    try:
        print(L, type(L), len(L), index)
        return L[index]
    except:
        return None

