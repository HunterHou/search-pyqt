import os
import unittest


def write(path, filename, suffex, context):
    filepath = path + filename + "." + suffex
    with open(filepath, 'w') as file:
        file.writelines(context)


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
            write(path, self.filename, suffex, context)


if __name__ == '__main__':
    unittest.main()
