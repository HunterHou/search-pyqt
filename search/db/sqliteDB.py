#!/usr/bin/python
# encoding=utf-8

import sqlite3

from search.model.file import File
from search.utils.classUtil import *


class SqliteDB:
    conn = sqlite3.connect('search.db')
    cursor = conn.cursor()
    columns = ['code', 'title', 'path', 'actress', 'fileType', 'dirPath', 'size', 'create_time', 'modify_time']

    def __init__(self):
        pass

    def assembleMovies(self, sample, params, orders):
        moives = []
        names = get_member_name(sample)
        data = self.query('movie', names, params, orders)
        for row in data:
            file = File()
            set_member_info(names, row, file)
            moives.append(file)
        return moives

    def query(self, tableName, columns, params, orders):

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

    def insertOne(self, tableName, columns, row):
        sql = 'insert into %s (%s) values(%s)' % (tableName, ','.join(columns), ','.join('?' * len(row)))
        self.cursor.execute(sql, row)
        self.conn.commit()

    def insertMany(self, tableName, columns, rows):
        if len(rows) == 0:
            return
        for row in rows:
            sql = 'insert into %s(%s) values(%)' % (tableName, ','.join(columns), ','.join(row))
            self.cursor.execute(sql)
        self.conn.close()

    def isExists(self, name):
        self.cursor.execute("select count(*)  from sqlite_master where type='table' and name = ?", [name])
        result = false
        if len(self.cursor.fetchall()) > 0:
            result = True
        self.conn.commit()
        return result;

    def getTableInfo(self, name):
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
        sql = 'delete from  %s' % (tableName)
        self.cursor.execute(sql)
        self.conn.commit()

    def dropTable(self, tableName):
        sql = 'drop table  %s' % (tableName)
        self.cursor.execute(sql)
        self.conn.commit()

    def close(self):
        self.conn.close()
