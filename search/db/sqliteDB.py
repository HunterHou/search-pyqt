#!/usr/bin/python
# encoding=utf-8

import sqlite3


class SqliteDB:
    conn = sqlite3.connect('search.db')
    cursor = conn.cursor()
    columns = ['code', 'title', 'path', 'actress', 'fileType', 'dirPath', 'size', 'create_time', 'modify_time']

    def __init__(self):

        pass

    def db_query(self):
        self.cursor.execute(sql, param)

    def insertOne(self):
        self.cursor.execute(sql, param)

    def insertMany(self):
        self.cursor.execute(sql, param)

    def isExists(self, name):
        self.cursor.execute("select count(*)  from sqlite_master where type='table' and name = ?", [name])
        if len(self.cursor.fetchall()) > 0:
            return True
        else:
            return False

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

    def close(self):
        self.conn.close()
