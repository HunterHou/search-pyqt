import re


def win10FilenameFilter(letter):
    # winChars = ["\\", "/", ":", "*", "?", '"', '!', '！', "<", ">", "|"]
    # for char in winChars:
    #     letter = letter.replace(char, '-')
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    letter = re.sub(rstr, "_", letter)  # 替换为下划线
    letter = letter.strip()
    return letter
