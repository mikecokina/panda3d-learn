from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DirectWaitBar, DGG
from panda3d.core import TextNode


class Hud(DirectObject):
    def __init__(self, framework):
        super(Hud, self).__init__()
        self.f = framework

        self.player = DirectWaitBar(
            text="Player",
            text_fg=(1, 1, 1, 1),
            text_pos=(-1.2, -0.15, 0),
            text_align=TextNode.ALeft,
            text_scale=0.075,
            value=100,
            barColor=(0, 1, 0.25, 1),
            barRelief=DGG.FLAT,
            barBorderWidth=(0.03, 0.03),
            borderWidth=(0.01, 0.01),
            relief=DGG.FLAT,
            frameColor=(0.8, 0.05, 0.10, 1),
            frameSize=(-1.2, 0, 0, -0.05),
            pos=(-0.2, 0, self.f.a2dTop - 0.10))
        self.player.set_transparency(1)

        self.bot = DirectWaitBar(
            text="Enemy",
            text_fg=(1, 1, 1, 1),
            text_pos=(1.2, -0.15, 0),
            text_align=TextNode.ARight,
            text_scale=0.075,
            value=100,
            barColor=(0, 1, 0.25, 1),
            barRelief=DGG.FLAT,
            barBorderWidth=(0.03, 0.03),
            borderWidth=(0.01, 0.01),
            relief=DGG.FLAT,
            frameColor=(0.8, 0.05, 0.10, 1),
            frameSize=(0, 1.2, 0, -0.05),
            pos=(0.2, 0, self.f.a2dTop - 0.10))
        self.bot.set_transparency(1)

        self.accept("hud_set_hp", self.set_hp)
        self.hide()

    def show(self):
        self.bot.show()
        self.player.show()

    def hide(self):
        self.bot.hide()
        self.player.hide()

    def set_hp(self, uid, value):
        if uid == "bot":
            self.bot["value"] = value
        elif uid == "player":
            self.player["value"] = value
