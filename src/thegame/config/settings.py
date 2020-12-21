import os.path as op
from pathlib import Path
from panda3d.core import loadPrcFile


class Settings(object):
    CONF_FILE = Path(op.dirname(__file__)) / "thegame.prc"

    def __init__(self):
        self.prc = loadPrcFile(self.CONF_FILE)
        self.egg = Path(op.dirname(self.CONF_FILE)) / ".." / ".." / "egg"
        self.tex = Path(op.dirname(self.CONF_FILE)) / ".." / ".." / "tex"
        self.bam = Path(op.dirname(self.CONF_FILE)) / ".." / ".." / "bam"
        self.sfx = Path(op.dirname(self.CONF_FILE)) / ".." / ".." / "sfx"


settings = Settings()
