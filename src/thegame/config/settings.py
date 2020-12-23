import os.path as op
from pathlib import Path
from panda3d.core import loadPrcFile


class _Const(object):
    SHOW_COLLIDERS = False
    ALLOW_DAYLIGHT = True
    ALLOW_SHADOWS = True
    ALLOW_FILTERS = False
    ALLOW_AMBIENT = False
    TRD_PERSON_CAM = True
    CONF_FILE = Path(op.dirname(__file__)) / "thegame.prc"
    DISABLE_SFX = False

    START_GAME_DRIVER = "start-game-driver"
    QUIT_GAME_DRIVER = "quit-game-driver"

    IN_MENU_STATE = "in-menu-state"
    IN_GAME_STATE = "in-game-state"


class Settings(_Const):

    def __init__(self):
        self.prc = loadPrcFile(self.CONF_FILE)
        self.egg = Path(op.dirname(self.CONF_FILE)) / ".." / ".." / "egg"
        self.tex = Path(op.dirname(self.CONF_FILE)) / ".." / ".." / "tex"
        self.bam = Path(op.dirname(self.CONF_FILE)) / ".." / ".." / "bam"
        self.sfx = Path(op.dirname(self.CONF_FILE)) / ".." / ".." / "sfx"
        self.ass = Path(op.dirname(self.CONF_FILE)) / ".." / ".." / "assets"


settings = Settings()
