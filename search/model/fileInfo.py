import os


def makeInfo(act, code, title):
    pass


def writeNfo(path, filename, context):
    suffex = 'nfo'
    filepath = path + filename + "." + suffex
    ex = os.path.exists(filepath)
    if ex:
        filename = filename + "(1)"
        writeNfo(path, filename, context)
    else:
        writeFile(path, filename, context)


def writeFile(path, filename, suffex, context):
    filepath = path + filename + "." + suffex
    with open(filepath, 'w') as file:
        file.writelines(context)
