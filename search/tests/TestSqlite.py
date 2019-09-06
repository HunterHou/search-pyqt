#!/usr/bin/python
# encoding=utf-8

import sqlite3
import unittest


class TestSqlite(unittest.TestCase):

    def test_create_table(self):
        conn = sqlite3.connect('search.db')
        cursor = conn.cursor()
        cursor.execute(
            'create table movie(code varchar(20) ,title varchar(800),path varchar(800),actress varchar(800),fileType varchar(800),dirPath varchar(800),size varchar(800),create_time varchar(800),modify_time varchar(800))')
        print(cursor.rowcount)
        conn.commit()
        conn.close()

    def test_insert_One(self):
        conn = sqlite3.connect('search.db')
        cursor = conn.cursor()
        cursor.execute(
            'insert into movie (code,title,path,actress,fileType,dirPath,size,create_time,modify_time) values (?,?,?,?,?,?,?,?,?)',
            ('111', '', '', '', '', '', '', '', ''))
        print(cursor.rowcount)
        conn.commit()
        conn.close()

    def test_query(self):
        conn = sqlite3.connect('search.db')
        cursor = conn.cursor()
        cursor.execute(
            'select * from movie')

        rows = cursor.fetchall()
        for row in rows:
            print(row)

        print(cursor.rowcount)
        conn.commit()
        conn.close()
