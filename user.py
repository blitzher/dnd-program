import eel
import backend as util

eel.init('web')
world = util.load_json("utils", "world.json")


@eel.expose
def get_world():
    return world


eel.start('index.html')
