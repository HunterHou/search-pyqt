def win10FilenameFilter(letter):
    winChars = ["\\", "/", ":", "*", "?", '"', '!', '！', "<", ">", "|"]
    for char in winChars:
        letter = letter.replace(char, '-')
    return letter
