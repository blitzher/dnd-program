import json
import os
import shutil
import funcs as util
from random import choice

default_indent = 2

# set current directory to this files folder
dir_path = util.getcwd(__file__)
parent_path = os.path.join(*os.path.split(dir_path)[:-1])
data_path = os.path.join(parent_path, "data")
dropbox_path = "C:\\Users\\Skovborg\\Dropbox\\DnD\\data" if os.name == 'nt' else "/Users/skovborg/dropbox/dnd/data"

# load the unencrypted locks and world
with open(os.path.join(dir_path, "locks.json"), "r") as lock_file:
    current_locks = json.load(lock_file)['locks']
with open(os.path.join(dir_path, "world.json"), "r") as world_file:
    world = json.load(world_file)

# save the path before running this module
# and change cwd to this directory
pre_path = os.getcwd()
os.chdir(dir_path)


def re_align(file="world.json", indent=default_indent):
    """ re align a json file, by loading it and dumping it with an indent """
    with open(file, 'r') as _file:
        data = json.load(_file)
    with open(file, 'w') as _file:
        json.dump(data, _file, indent=indent)


def move_file(file, destination):
    file_path = os.path.join(dir_path, file)
    dest_path = os.path.join(destination, file)

    os.replace(file_path, dest_path)


def copy_file(file, destination):
    file_path = os.path.join(dir_path, file)
    dest_path = os.path.join(destination, file)

    shutil.copy(file_path, dest_path)


def generate_lock(*paths, end=True, his_level=0, loc_level=0):
    """ generates a lock for a path, and paths towards it, and saves it to locks.json"""

    # if the his_level or loc_level is greater than 0, also make lower locks
    if loc_level > 0 and his_level > 0:
        generate_lock(*paths, end=end, his_level=0, loc_level=0)
        generate_lock(*paths, end=end, his_level=his_level, loc_level=0)
        generate_lock(*paths, end=end, his_level=0, loc_level=loc_level)
        return
    if his_level > 1:
        generate_lock(*paths, end=end, his_level=his_level - 1, loc_level=0)
    if loc_level > 1:
        generate_lock(*paths, end=end, his_level=0, loc_level=loc_level - 1)

    # generate a lock that needs a similar key
    chars = "abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVXYZ0123456789"
    lock = "none"

    # generate a random lock until an unused is found
    while lock in current_locks:
        lock = "".join([choice(chars) for i in range(8)])

    # generate a list of the paths the key unlocks
    def expand(obj, pre=""):
        # Credits to Mads Bach https://github.com/madsbacha/
        output = []
        prefix = pre
        for i, c in enumerate(obj):
            try:
                output.append(prefix + c)
                prefix += c + "/"
            except TypeError:
                for oc in c:
                    new_out = expand([oc] + obj[i+1:], prefix)
                    output = output + new_out
                break
        return output

    halls = []
    for path in paths:
        for hall in expand(path):
            halls.append(hall)

    # add history and location tiers
    for hall in halls:
        hall = hall.split("/")
        if hall[-1] in ('history', 'location'):
            all_tiers = util.follow_path(world, hall)
            for tier in all_tiers:
                if (hall[-1] == 'history' and int(tier[0]) <= his_level) or (hall[-1] == 'location' and int(tier[0]) <= loc_level):
                    hall_name = "/".join(hall + [tier])
                    halls.append(hall_name)

    # remove history or locaton if his_level is 0 or loc_level is 0
    his_indx_to_remove = [c for c, hall in enumerate(halls)
                          if hall.split("/")[-1] == 'history' and his_level == 0]
    for i in sorted(his_indx_to_remove, reverse=True):
        del(halls[i])

    loc_indx_to_remove = [c for c, hall in enumerate(halls)
                          if hall.split("/")[-1] == 'location' and loc_level == 0]
    for i in sorted(loc_indx_to_remove, reverse=True):
        del(halls[i])

    # after all info is compiled, check if it is valid
    halls = sorted(util.remove_duplicates(halls))
    for hall in halls:
        try:
            util.follow_path(world, hall.split("/"))
        except KeyError:
            print("[!] Problem generating lock <%s> for the hall [%s]: Door is missing or misspelled!" % (
                str(paths)[:25], hall))
            return hall

    # if the lock already exists, dont do anything
    if halls in current_locks.values():
        print("[!] Lock  <%s:his=%s:loc=%s> already made!" %
              (str(paths)[0:65], his_level, loc_level))
        return False

    current_locks[lock] = halls
    print("[v] Succesfully created lock <%s:his=%s:loc=%s>!" %
          (str(paths)[0:65], his_level, loc_level))

    return True


def decrypt(file):
    with open(file, 'r') as f:
        raw_data = f.read().strip()

    decrypt_data = ""
    for ch in raw_data:
        if ch in util.decr:
            decrypt_data += util.decr[ch]
        else:
            decrypt_data += ch

    decrypt_data = json.loads(decrypt_data)

    with open(file + '.json', 'w') as f:
        json.dump(decrypt_data, f, indent=default_indent)


def encrypt(file="world.json"):
    with open(os.path.join(dir_path, file), 'r') as f:
        raw_data = json.dumps((json.load(f)))

    encrypt_data = ""
    for ch in raw_data:
        if ch in util.encr:
            encrypt_data += util.encr[ch]
        else:
            print("[?] Couldn't interpret '%s' when encrypting" % ch)
            encrypt_data += ch

    with open(os.path.join(dir_path, "e" + file[:-5] + ".e"), 'w') as f:
        f.write(encrypt_data)


def main():
    re_align()
    # region CITY & CITY PERSON

    # % CITY TEMPLATE %
    # generate_lock(["provinces", "Kingshaven", "cities", "Galanodel", [
    #              "history", "location"]], his_level = 1, loc_level = 1)
    # generate_lock(["provinces", "Desolate Plateau", "cities", "Crestiel", ["history", "location"]], his_level=1, loc_level=1)
    # generate_lock(["provinces", "Ebon Reach", "cities", "Torriton", [
    #              "history", "location"]], his_level=3, loc_level=3)

    # % PERSON TEMPLATE %
    # generate_lock(["provinces", "Storms Peak", "cities", "Storms Eye", "people", "Tycho Aurelius", ['occupation', 'characteristics','history', 'location']], his_level=2, loc_level=1)

    # endregion

    # region ORGANISATION TEMPLATES

    # % ORGANISATION TEMPLATE %
    # generate_lock(["organisations", "Marvins Miraculous Caravan", ["signatures", "history", "people"]])

    # % ORGANISATION PERSON %
    # generate_lock(["organisations", "Marvins Miraculous Caravan", "people", "Nemeia Florara", ["occupation", "history", "location", "characteristics"]], his_level=1, loc_level=1)

    # endregion

    # region RELIGION, UNIQUE PERSON & JOURNAL

    # % RELIGION TEMPLATE %
    # generate_lock(['religions', 'Seven Faced Vaii', ['major gods', 'minor gods', 'description', 'belief', 'sigil']],
    #    ['religions', 'Seven Faced Vaii', 'major gods', 'Vaii', ['domain', 'title', 'representation', 'symbolize', 'sigil']],
    #    ['religions', 'Seven Faced Vaii', 'minor gods', ['Academia', 'Anger', 'Nurture', 'Heavens', 'Naturalia', 'Decera', 'Terrifia'], ['domain', 'title', 'representation', 'sigil']])

    # % UNIQUE PERSON TEMPLATE
    # generate_lock(['people', 'Magnus Heck', ["occupation", "history", "location", "characteristics"]], his_level=1, loc_level=1)

    # % JOURNAL TEMPLATE %
    # generate_lock(["journals", "Journal of Isak", "11th-page"])

    generate_lock(["journals", "Infernal Instruments",
                   "1st-piece", ["1st-page", "instrument"]])

    # endregion

    # write updated locks to json
    with open("locks.json", "w") as lock_file:
        data = {'locks': current_locks}
        json.dump(data, lock_file, indent=default_indent)

    encrypt("locks.json")
    encrypt("world.json")

    move_dir = dropbox_path

    for file in ['elocks.e', 'eworld.e']:
        try:
            move_file(file, move_dir)
        except Exception as e:
            print("Couldn't move files to %s" % move_dir)
            print(e)

    copy_file('changelog.json', move_dir)


if __name__ == '__main__':
    if main() is None:
        print("[v] Succesful termination")

# change back to working directory
os.chdir(pre_path)
