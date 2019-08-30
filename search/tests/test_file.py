#!/usr/bin/python
# encoding=utf-8


import unittest

from search.model.file import replaceSuffix


class TestFile(unittest.TestCase):

    def test_replace_suffix(self):

        """ test replaceSuffix"""
        filepath = "a.b.c.jpg"
        new_filepath = replaceSuffix(filepath, 'png')
        print(new_filepath)
        filepath = "ajpg"
        new_filepath = replaceSuffix(filepath, 'png')
        print(new_filepath)

    def test_list_in_list(self):
        parent = ["text", "jpg", 'png', 'xls', 'mp4', 'wmv', 'gif']
        child = ['jpg', 'pngg']
        if set(child) < set(parent):
            print("HasIt")
        else:
            print('HasNot')
