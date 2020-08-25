import eel
import backend as util

eel.init('web')
world = util.load_json("utils", "world.json")
locks = util.load_json("utils", "locks.json")


@eel.expose
def get_world():
    return world


@eel.expose
def get_locks():
    return locks


eel.start('index.html', port=80)
