import os
import unittest

from search.model.fileInfo import writeFile


class IOTestCase(unittest.TestCase):
    filename = "test"

    def test_something(self):
        path = "E:\\"

        suffex = "xml"
        context = "<name>张三</name>"
        filepath = path + self.filename + "." + suffex
        ex = os.path.exists(filepath)
        if ex:
            self.filename = self.filename + "(1)"
            self.test_something()
        else:
            writeFile(path, self.filename, suffex, context)


if __name__ == '__main__':
    unittest.main()
