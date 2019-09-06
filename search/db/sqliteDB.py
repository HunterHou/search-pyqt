#!/usr/bin/python
# encoding=utf-8

class SqliteDB:
    conn = sqlite3.connect('search.db')
    cursor = conn.cursor()
    columns = ['code', 'title', 'path', 'actress', 'fileType', 'dirPath', 'size', 'create_time', 'modify_time']

    def __init__(self):
        pass

    def isExists(self, name):
        self.cursor.execute('select count(*)  from sqlite_master where type=''table'' and name = ?;', name)
        if len(self.cursor.fetchall()) > 0:
            return True
        else:
            return False

    def createTable(self, tableName, columns, indexColumn):
        self.cursor.execute('create table %s(%s)', (tableName, ''.join(columns)))
        for index in indexColumn:
            self.cursor.execute('create index  idx%s_%s on  %s(%s)', (tableName, index))
        self.conn.commit()

    def db_query(self):
        self.cursor.execute(sql, param)
