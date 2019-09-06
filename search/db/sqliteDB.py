#!/usr/bin/python
# encoding=utf-8

import copy
import sqlite3

from search.utils.clazzUtil import *


class SqliteDB:
    conn = sqlite3.connect('search.db')
    cursor = conn.cursor()

    def __init__(self):
        pass

    def assembleObjects(self, clazz, params, orders):
        """查询并组装成可用对象"""
        objects = []
        tableName = clazz.table_name
        names = get_member_name(clazz)
        data = self.query(tableName, names, params, orders)
        for row in data:
            obj = copy.deepcopy(clazz)
            set_member_info(names, row, obj)
            objects.append(obj)
        return objects

    def query(self, tableName, columns, params, orders):
        """查询条件和排序组装 返回值 为list<list>"""
        sql = 'select %s from %s  ' % (','.join(columns) if len(columns) > 0 else '*', tableName)
        paramValues = []
        if len(params) > 0 and params is not None:
            sql += ' where 1=1'
            for param in params:
                if len(param) >= 2:
                    sql += ' and ' + param[0] + '=?'
                    paramValues.append(param[1])
        if len(orders) > 0 and orders is not None:
            sql += ' order by '
            for index in range(len(orders)):
                if index != 0:
                    sql += ","
                if len(orders[index]) >= 2:
                    sql += orders[index][0] + ' ' + orders[index][1]
        self.cursor.execute(sql, paramValues)
        return self.cursor.fetchall()

    def insertObject(self, obj):
        tableName = obj.table_name
        """根据可用对象的成员  insert """
        columns = get_member_name(obj)
        row = get_member_value(obj)
        sql = 'insert into %s (%s) values(%s)' % (tableName, ','.join(columns), ','.join('?' * len(row)))
        self.cursor.execute(sql, row)
        self.conn.commit()

    def createObjectTable(self, obj):
        """根据对象  创建表 """
        tableName = obj.table_name
        columns = get_member_name(obj)
        self.createTable(tableName, columns, [])

    def insertOne(self, tableName, columns, row):
        """根据插入列名 插入值  insert """
        sql = 'insert into %s (%s) values(%s)' % (tableName, ','.join(columns), ','.join('?' * len(row)))
        self.cursor.execute(sql, row)
        self.conn.commit()

    def insertMany(self, tableName, objs):
        if len(objs) == 0:
            return
        for obj in objs:
            columns = get_member_name(obj)
            row = get_member_value(obj)
            sql = 'insert into %s (%s) values(%s)' % (tableName, ','.join(columns), ','.join('?' * len(row)))
            self.cursor.execute(sql, row)
        self.conn.commit()

    def isExists(self, name):
        """是否存在"""
        self.cursor.execute("select count(*)  from sqlite_master where type='table' and name = ?", [name])
        result = false
        if len(self.cursor.fetchall()) > 0:
            result = True
        self.conn.commit()
        return result

    def getTableInfo(self, name):
        """表信息"""
        self.cursor.execute("select * from sqlite_master where type='table' and name = ?", [name])
        return self.cursor.fetchone()

    def createTable(self, tableName, columns, indexColumn):
        sql = 'create table %s(%s)' % (tableName, ','.join(columns))
        self.cursor.execute(sql)
        if indexColumn is not None and len(indexColumn) > 0:
            for index in indexColumn:
                self.cursor.execute('create index  idx?_? on  ?(?)', (tableName, index, tableName, index))
        self.conn.commit()

    def clearTable(self, tableName):
        sql = 'delete from  %s' % tableName
        self.cursor.execute(sql)
        self.conn.commit()

    def dropTable(self, tableName):
        sql = 'drop table  %s' % tableName
        self.cursor.execute(sql)
        self.conn.commit()

    def close(self):
        self.conn.close()
