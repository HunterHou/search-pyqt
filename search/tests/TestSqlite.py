#!/usr/bin/python
# encoding=utf-8

import unittest

from search.db.sqliteDB import SqliteDB
from search.model.file import File
from search.utils.clazzUtil import get_member_name


class TestSqlite(unittest.TestCase):

    def test_create_table(self):
        table_name = 'user'
        table_columns = ['id', 'name']
        table_index = []
        db = SqliteDB()
        db.createTable(table_name, table_columns, table_index)
        db.close()

    def test_exists(self):
        table_name = 'user'
        db = SqliteDB()
        if db.isExists(table_name):
            print('存在')
        else:
            print('不存在')
        db.close()

    def test_get_table_info(self):
        table_name = 'user'
        db = SqliteDB()
        print(db.getTableInfo(table_name))
        db.close()

    def test_insert_one(self):
        table_name = 'user'
        table_columns = ['id', 'name']
        db = SqliteDB()
        db.insertOne(table_name, table_columns, ['1', "zhangsan"])
        db.close()

    def test_query(self):
        table_name = 'user'
        table_columns = ['id', 'name']
        db = SqliteDB()
        datas = db.query(table_name, table_columns, [])
        for dindex in range(len(datas)):
            print("当前数据:" + str(dindex))
            row = datas[dindex]
            for index in range(len(row)):
                print(str(index + 1) + ": " + row[index])
        db.close()

    def test_movie_exist(self):
        db = SqliteDB()
        db.isExists(File().table_name)

    def test_movie_drop_table(self):
        db = SqliteDB()
        db.dropTable(File().table_name)

    def test_movie_create_table(self):
        db = SqliteDB()
        db.createObjectTable(File())

    def test_movie_get_info(self):
        db = SqliteDB()
        print(db.getTableInfo(File().table_name))

    def test_movie_insert(self):
        file = File().build("E:\\emby\\one\\2.gif", "gif", "E:\emby\one")
        db = SqliteDB()
        db.insertObject(file)
        db.close()

    def test_movie_query(self):
        db = SqliteDB()
        file = File()
        datas = db.query(file.table_name, get_member_name(file), [])
        for dindex in range(len(datas)):
            row = datas[dindex]
            print("当前数据:" + str(dindex))
            for index in range(len(row)):
                print(str(index + 1) + ": " + row[index] if row[index] is not None else "")
        db.close()

    def test_assemble_file(self):
        db = SqliteDB()
        # params = [["name", "E:\\emby\\one\\2.gif"]]
        params = []
        orders = [['name', '']]
        files = db.assembleObjects(File(), params, orders)
        for file in files:
            print(file.name + ":::" + file.path)
