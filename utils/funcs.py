"""
utility library for dnd program
"""

import os
import shutil
import sys
import textwrap
import logging
import pprint


def clms(): return shutil.get_terminal_size()[0]
def rows(): return shutil.get_terminal_size()[1]


vers = [1, 2, 0, 1]

# sizeable constants and variables for the program
cmd_prefix = "!"
default_indent = 2


def set_prefix(new_prefix):
    # update the command prefix
    global cmd_prefix
    cmd_prefix = new_prefix


ret = "Press <enter> when you want to return"
qui = "Press <enter> when you want to quit"


def tut(): return "Type '{pfx}help' or '?' for a tutorial".format(
    pfx=cmd_prefix)


def help_msg(): return """
              This program is meant to be used in conjuction with a D&D adventure
              in which information about the world is encrypted in /data/eworld.e

              In the center of the screen, you will see the current unlocked information.
              You can navigate between these, by typing the name of an option, and pressing enter.
              The program will attempt to autocomplete what you type into the current options,
              starting from the top.
              To go backwards, simply press <enter> with nothing typed, or type '{pfx}back'. Additionally,
              you can also type '{pfx}top', to go to the very top of the information tree.

              To unlock more information, you will need to converse with you DM. After you recieve
              a key from your DM, type '{pfx}unlock <key>', where <key> is replaced by said key. A key
              is an 8 character string of random numbers and letters, such as [4BcD3FgH].

              To get more help on other commands, type '{pfx}commands'. To show this message again,
              type '{pfx}help' or '?'.
            """.format(pfx=cmd_prefix)


def cmds_msg(): return """
              [{pfx}back] / []
                go back one layer

              [{pfx}top]
                go the /Alterace/

              [{pfx}find <name>]
                attempts to find and go to a point in available data
                use as a shortcut primarily to specific cities and people

              [{pfx}]notes <optional: delete]
                creates a note in the current path, or edits currently existing note
                if a

              [{pfx}]settings
                open the settings menu

              [{pfx}unlock <key>]
                if you recieve the key for a lock, use this command to unlock it

              [{pfx}keys]
                look at all your keys
                you can also select a key, to find out what it unlocks

              [{pfx}refresh] / [{pfx}reload]
                refreshes your currently unlocked information
                automatically done when you successfully unlock information

              [{pfx}commands] / [{pfx}cmds]
                display this message

              [{pfx}help] / [?]
                display the tutorial to the program

              [{pfx}version]
                display the version number

              [{pfx}news]
                show the changes from previous versions.
                can specify from which version, using ">=", ">", "<", "<=" followed
                by version number to specify from a version
                e.g.
                "{pfx}news >1.1" to show all changes from 1.1 to now
                "{pfx}news 1.1.2" to show all changes implemented in version 1.1.2

              [{pfx}exit] / [{pfx}quit]
                exit out of the program
                """.format(pfx=cmd_prefix)


# simple method for obfuscating the content of files
encr = {
    'g': 'z', ':': 'V', 'z': '.', 'B': 'x', 'o': 'v', 'V': 'C', 'q': 'Z', 'L': '1', 'b': 'G', '\\': 'M', 'v': '7', 'N': 's', 'e': '9', "'": 'y', 'k': 'K', 'c': 'p', 'K': 'R', 'j': 'X', '/': 'N', 'n': '-', 'C': '_', 'G': 'h', '2': '"', 'U': '[', '}': ',', 's': '\\', 'H': 'T', '6': '5', 'r': '4', ' ': 'E', '"': 'a', 'R': 'u', ',': '3', 'I': 'd', '8': '{', 'W': 'S', '0': 't', 'Q': 'O', 'E': 'U', '7': ' ', 'O': 'q', 't': 'c', 'A': 'W', 'a': '8', '.': 'J', '?': ':', 'i': 'n', 'p': '2', 'X': 'o', 'S': 'H', 'P': ']', ']': '}', 'l': '0', 'x': 'D', '4': 'k', '\n': 'F', 'y': 'Q', 'w': 'g', 'f': 'i', 'h': 'e', 'F': 'B', '_': 'm', '1': "'", '-': '\n', '9': 'P', 'u': '/', 'Z': 'r', 'D': 'l', 'm': 'w', '3': 'Y', 'J': 'L', 'Y': 'j', 'T': 'b', 'M': '6', '[': '?', '5': 'I', '{': 'A', 'd': 'f'}
decr = {
    v: k for k, v in encr.items()}


def join(s, it) -> str:
    """ replace str.join(l) with join(s, l)
    simply attempts to cast each item in the iterator
    as a string before joining them
    """
    s_it = (str(_) for _ in it)
    return s.join(s_it)


def get_input(pre="> ", message="") -> str:
    """ provide a way of recieving input nicely """
    display = ("\n" + message + "\n") if message else ("")
    print(display)
    inp = input(pre)
    return inp


def dedent(message) -> str:
    """ use textwrap.dedents function, but recursively strip the
    message leading and trailing blanklines """
    split_m = message.split("\n")
    flag = False
    for i in (0, -1):
        if split_m[i] == "":
            del split_m[i]
            flag = True
    message = "\n".join(split_m)
    if flag:
        return dedent(message)
    else:
        return textwrap.dedent(message)


def autocomplete(message, options, case_sens=False, default=None):
    """ attempt to autocomplete message amongs options """
    if not message:
        return default
    if not case_sens:
        message = message.lower()
    for option in options:
        if not case_sens:
            if option.lower().startswith(message):
                return option
        else:
            if option.startswith(message):
                return option
    return default


def seperator(width=None, symbol="=") -> None:
    """ draw a line seperator using symbol """
    width = width if width else clms()
    print((width * symbol).center(clms()))


def center(text, symbol=" ") -> None:
    """ center some piece of text within on the screen,
    adding linebreaks wherever necessary """
    linewidth = clms() - 10
    text = str(text)

    # if linebreaks, split text and print chunks
    if ("\n" in text):
        for chunk in text.split("\n"):
            center(chunk, symbol=symbol)
        return

    # if exceeding linewidth, search for space or dash
    # and split line
    if len(text) > linewidth:
        for c, ch in enumerate(text[0:linewidth][::-1]):
            c = linewidth - c
            if ch in [" ", "-"]:
                center(text[0:c], symbol=symbol)
                center(text[c:], symbol=symbol)
                break
    else:
        print(text.center(clms(), symbol))


def center_around(symbol, *strings):
    """ 
    center some strings around some symbol in each of the strings
    """
    for string in strings:
        left, right = string.split(symbol)
        target_width = max(len(left), len(right))
        if len(left) < target_width:
            left = " " * (target_width - len(left)) + left
        if len(right) < target_width:
            right = right + " " * (target_width - len(right))

        center(" ".join([left, symbol, right]))


def highlight(text, width=None, symbol="=") -> None:
    """ place some text centered in between 2 seperators """
    width = width if width else clms()

    seperator(width=width, symbol=symbol)
    center(text)
    seperator(width=width, symbol=symbol)


def follow_path(obj: dict, path: list):
    """ follow the path in an dict-like object """
    def shorten(s, _len=10):
        if _len:
            return str(s)[:_len]
        else:
            return str(s)
    try:
        for item in path:
            obj = obj[item]
    except:
        logging.warning("Following path: <%s> in: <%s> was not possible" % (
            shorten(path, False), shorten(obj, 25)))
    return obj


def remove_duplicates(obj) -> list:
    """ remove duplicates from a list """
    return list(dict.fromkeys(obj))


def clear() -> None:
    """ clear the terminal """
    os.system('cls' if os.name == 'nt' else 'clear')


def getcwd(file) -> str:
    """ get the current working directory for executing script"""
    # Credit to anon at https://itqna.net/questions/75644/problem-pyinstaller-osgetcwd-mac-os
    if getattr(sys, 'frozen', False) and os.name != 'nt':
        # if program is mac-frozen, do workaround
        cwd = "/" + \
            os.path.join(*os.path.abspath(sys.executable).split("/")[:-1])
    else:  # otherwise, follow normal procedure
        cwd = os.path.dirname(os.path.realpath(file))
    return cwd


def sumlist(lists) -> list:
    """ joins lists of lists into one single list 

    sumlist( [ [a,b],[c,d] ] ) -> [a,b,c,d]
    """
    ret = []
    for each in lists:
        for obj in each:
            ret.append(obj)
    return ret


# handle & setup logging
log_file_name = 'user.log'
logging.basicConfig(filename=log_file_name, level=logging.DEBUG)


def clear_log():
    with open(log_file_name, 'w'):
        pass


def log_version():
    logging.info("running version: %s" % version(*vers))


def log_user_data(usr):
    logging.info("current path: '%s'", "/".join(usr.current_path))
    logging.info("recent action: '%s'", usr.recent_input)
    logging.info("keys: %s", usr.keys)
    logging.info("settings: \n%s", usr.settings)


class version:
    def __init__(self, *version):
        if len(version) < 2:
            raise ValueError(
                "Cannot make version with no major and minor version number")
        self.major = version[0]
        self.minor = version[1]
        self.subversion = version[2:]
        self.total = version

    def __str__(self):
        str_version = [str(self.major), str(self.minor)]
        str_version += [str(_) for _ in self.subversion]
        return ".".join(str_version)

    @staticmethod
    def from_str(arg):
        return version(*arg.split("."))

    def __add__(self, other):
        return str(self) + other

    def __radd__(self, other):
        return other + str(self)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.total == other.total

    def __gt__(self, other):
        shortest = min([self, other], key=lambda x: len(x.total))

        for c, _ in enumerate(shortest.total):
            if self.total[c] > other.total[c]:
                return True
            elif self.total[c] < other.total[c]:
                return False

        return False

    def __lt__(self, other):
        if self.__eq__(other):
            return False

        return not self.__gt__(other)

    def __ge__(self, other):
        if self.__eq__(other):
            return True

        return self.__gt__(other)

    def __le__(self, other):
        if self.__eq__(other):
            return True

        return self.__lt__(other)
