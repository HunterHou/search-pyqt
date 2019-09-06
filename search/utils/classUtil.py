#!/usr/bin/python
# encoding=utf-8


def set_member_info(names, values, obj):
    for index in range(len(names)):
        name = names[index]
        if hasattr(obj, name):
            setattr(obj, name, values[index])
    return obj


def get_member_Info(obj):
    """获取对象的变量信息 key-value"""
    members = []
    for name, value in vars(obj).items():
        member = [name, value]
        members.append(member)
    return members


def get_member_name(obj):
    """获取对象的变量名 key"""
    members = []
    for name, value in vars(obj).items():
        members.append(name)
    return members


def get_member_value(obj):
    """获取对象的变量值 value"""
    members = []
    for name, value in vars(obj).items():
        members.append(value)
    return members
