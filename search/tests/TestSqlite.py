#!/usr/bin/python
# encoding=utf-8

import unittest

from search.db.sqliteDB import SqliteDB


class TestSqlite(unittest.TestCase):
    table_name = 'user'
    table_columns = ['id', 'name']
    table_index = []

    def test_create_table(self):
        db = SqliteDB()
        db.createTable(self.table_name, self.table_columns, self.table_index)
        db.close()

    def test_exists(self):
        db = SqliteDB()
        if db.isExists(self.table_name):
            print('存在')
        else:
            print('不存在')

        db.close()

    def test_get_table_info(self):
        db = SqliteDB()
        print(db.getTableInfo(self.table_name))
        db.close()
