"""
object oriented d&d players information sheet
"""
import json
import os.path
import utils.funcs as util

CURRENT_WORKING_DIR = util.getcwd(__file__)
VERSION = "1.1.2"

encr = {
    '\n': 'i', ' ': '4', '"': '9', "'": '}', ',': "'", '-': 'R', '.': ' ', '0': 'h', '1': '{', '2': 'x', '3': '\\', '4': 'b', '5': 'L', '6': 'Q', '7': 'G', '8': '1', '9': 'H', ':': 'F', 'A': 'm', 'B': '6', 'C': '5', 'D': 'K', 'E': 'D', 'F': 'U', 'G': 'c', 'H': '"', 'I': 'z', 'J': 'M', 'K': 'I', 'L': 'f', 'M': 'B', 'N': 't', 'O': '.', 'P': ',', 'Q': 'u', 'R': 'W', 'S': 'V', 'T': 'g', 'U': 'v', 'V': '\n', 'W': '0', '\\': 'N', 'a': 'k', 'b': '8', 'c': 'O', 'd': 'a', 'e': 'e', 'f': 'T', 'g': 'S', 'h': 'd', 'i': 'r', 'j': 'y', 'k': '-', 'l': '2', 'm': 'P', 'n': 'p', 'o': 'J', 'p': 'C', 'q': 'w', 'r': 'o', 's': 'l', 't': ':', 'u': 's', 'v': 'q', 'w': '7', 'x': '3', 'y': 'A', 'z': 'j', '{': 'n', '}': 'E'}
decr = {
    v: k for k, v in encr.items()}


def decrypt(file):
    with open(file, 'r') as f:
        raw_data = f.read()

    decrypt_data = ""
    for ch in raw_data:
        if ch in decr:
            decrypt_data += decr[ch]
        else:
            decrypt_data += ch
    return decrypt_data


def load_json(*j_file):
    """
    loads the data from a json file, encrypted or not
    can take the path to a json file as argument.
    """

    j_file = os.path.join(CURRENT_WORKING_DIR, *j_file)
    _, extention = os.path.splitext(j_file)

    if extention == '.json' and os.path.exists(j_file):
        with open(j_file, 'r+') as file:
            data = json.load(file)
    elif os.path.exists(j_file):
        data = json.loads(decrypt(j_file))
    else:
        if any(necessary in j_file for necessary in ['world', 'lock']):
            raise Exception("Program does not function without %s" % j_file)

        data = {'keys': []}
        with open(j_file, 'w+') as file:
            json.dump(data, file, indent=util.default_indent)
    return data


class user:
    def __init__(self, game_master=False):
        self.running = True
        self.load_info()
        self.current_path = []
        self.game_master = game_master
        self.iterations = 0

    def load_info(self):
        self.keys = load_json('keys.json')['keys']
        self.locks = load_json('data', 'elocks.e')['locks']
        self.world = load_json('data', 'eworld.e')

    def add_key(self, key):
        # add to current class instance
        if key not in self.locks or key in self.keys:
            return False
        self.keys.append(key)
        self.save_keys()
        util.clear()
        util.highlight("Succes <%s>! New information unlocked" %
                       key, symbol='=')
        for door in self.locks[key]:
            util.center("%s" % door)
        util.get_input()
        return True

    def find_endpoint(self, name):
        doors = util.sumlist(self.locks[key] for key in self.keys)
        handles = list(filter(lambda door: door.split(
            "/")[-1].lower().startswith(name.lower()), doors))

        # If it only found one match
        if len(handles) == 1:
            return handles[0]
        else:
            return False

    def handle_command(self, command):
        " pass the unparsed input "
        # remove leading and trailing whitespace
        cmd = command.strip().split(" ")[0]

        # commands without the prefix
        if util.autocomplete(cmd, ['__empty__']):
            self.current_path = self.current_path[:-1]
            return True

        if util.autocomplete(cmd, ['?']):
            util.clear()
            util.highlight("Tutorial")
            util.center(util.dedent(util.cmds_msg()))
            util.get_input(util.ret)
            return True

        # unlock all information DELETE AT SOME POINT
        if cmd == "alohomora":
            self.game_master = True
            return True

        # filter away the prefix and commands without the prefix
        if cmd.startswith(util.cmd_prefix):
            cmd = cmd[len(util.cmd_prefix):]
        else:
            return False

        # commands with the prefix
        if util.autocomplete(cmd, ['clms']):
            print(util.clms())
            util.get_input()
            return True
        if util.autocomplete(cmd, ['back']):
            self.current_path = self.current_path[:-1]
            return True
        if util.autocomplete(cmd, ['top']):
            self.current_path = []
            return True
        if util.autocomplete(cmd, ['unlock']):
            attempt_key = command.split(" ")[-1]
            if not self.add_key(attempt_key):
                util.get_input(
                    "<%s> is not a valid key, or is already unlocked!" % attempt_key)
            return True
        if util.autocomplete(cmd, ['exit', 'quit']):
            self.running = False
            return True
        if util.autocomplete(cmd, ['refresh']):
            self.load_info()
            return True
        if util.autocomplete(cmd, ['keys']):
            return True
        if util.autocomplete(cmd, ['commands', 'cmds']):
            util.clear()
            util.highlight("Commands")
            util.center(util.dedent(util.cmds_msg()))
            util.get_input(util.ret)
            return True
        if util.autocomplete(cmd, ['help']):
            util.clear()
            util.highlight("Tutorial")
            util.center(util.dedent(util.help_msg()))
            util.get_input(util.ret)
            return True
        if util.autocomplete(cmd, ['find']):
            target = self.find_endpoint(command.split(" ")[-1])
            if target:
                self.current_path = target.split("/")
        if util.autocomplete(cmd, ['version']):
            util.center("user-"+VERSION)
            util.get_input()
            return True
        return False

    def handle_path(self, action):
        if not action:
            return
        try:
            target = util.follow_path(self.world, self.current_path + [action])
        except:
            return

        if type(target) != dict:
            util.center(target)
            util.get_input(util.ret)
            util.clear()
        else:
            self.current_path.append(action)

    def is_unlocked(self, option):
        if self.game_master:
            return True
        door = "/".join(self.current_path + [option])
        keys = util.sumlist(self.locks[key_] for key_ in self.keys)
        return door in keys

    def save_keys(self):
        keys_file = os.path.join(CURRENT_WORKING_DIR, "keys.json")
        with open(keys_file, 'w') as keys_json:
            data = {'keys': self.keys}
            json.dump(data, keys_json, indent=util.default_indent)

    def end(self):
        util.clear()


def main():
    pass


if __name__ == '__main__':
    main()
