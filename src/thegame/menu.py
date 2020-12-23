from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel
from direct.showbase.ShowBase import ShowBase, TextNode

from thegame import settings


class MainMenu(object):
    def __init__(self, framework: ShowBase):
        self.f = framework
        self.main_frame = DirectFrame(frameSize=(self.f.a2dLeft, self.f.a2dRight,
                                                 self.f.a2dBottom, self.f.a2dTop))
        self.main_frame.set_transparency(1)
        self.title = DirectLabel(
            scale=0.2,
            pos=(0, 0, self.f.a2dTop - 0.25),
            frameColor=(0, 0, 0, 0),
            text="Battle Tank",
            text_fg=(0, 0, 0, 1)
        )
        self.title.set_transparency(1)
        self.title.reparent_to(self.main_frame)

        self.btn_start = self.create_btn("Start", 0.12, [settings.START_GAME_DRIVER])
        self.btn_quit = self.create_btn("Quit", -0.12, [settings.QUIT_GAME_DRIVER])
        self.hide()

    def create_btn(self, label, v_position, event_args):
        maps = self.f.loader.loadModel(settings.ass / "button_map")
        geom = (maps.find("**/btn_ready"),
                maps.find("**/btn_click"),
                maps.find("**/btn_rollover"),
                maps.find("**/btn_disabled"))
        btn = DirectButton(
            text=label,
            text_fg=(0, 0, 0, 1),
            text_scale=0.05,
            text_pos=(0.02, -0.015),
            text_align=TextNode.ALeft,
            scale=2,
            pos=(self.f.a2dLeft + 0.2, 0, v_position),
            geom=geom,
            relief=0,
            frameColor=(0, 0, 0, 0),
            command=self.f.messenger.send,
            extraArgs=event_args,
            pressEffect=False,
            rolloverSound=None,
            clickSound=None)
        btn.reparent_to(self.main_frame)
        return btn

    def show(self):
        self.main_frame.show()

    def hide(self):
        self.main_frame.hide()

    def hide_start_btn(self):
        self.btn_start.hide()
