from direct.fsm.FSM import FSM
from direct.showbase.ShowBase import (
    ShowBase,
    AntialiasAttrib,
    CollisionTraverser,
    CollisionHandlerPusher, CollisionHandlerEvent
)
from direct.gui.DirectGui import DGG
from thegame import settings
from thegame.battletank import BattleTank
from thegame.hud import Hud
from thegame.menu import MainMenu


class MainGame(ShowBase):
    def __init__(self):
        self.game = None
        ShowBase.__init__(self)
        # FSM.__init__(self, "battle-tank-fsm")

        if settings.DISABLE_SFX:
            self.disableAllAudio()

        # Enhance font readability
        DGG.getDefaultFont().setPixelsPerUnit(100)
        # get the displays width and height for later usage
        self.dispWidth = self.pipe.getDisplayWidth()
        self.dispHeight = self.pipe.getDisplayHeight()

        self.musicManager.setConcurrentSoundLimit(3)
        self.render.setAntialias(AntialiasAttrib.MMultisample)

        self.menu = MainMenu(self)
        self.hud = Hud(self)
        self.accept("escape", self.__escape)

        self.state = settings.IN_MENU_STATE
        self.menu.show()

        # accept msg inputs
        self.accept(settings.QUIT_GAME_DRIVER, self.exit_game)
        self.accept(settings.START_GAME_DRIVER, self.start_game)

        # collision
        self.cTrav = CollisionTraverser()
        self.cTrav.setRespectPrevTransform(True)
        self.pusher = CollisionHandlerPusher()
        self.cHandler = CollisionHandlerEvent()
        # self.request("Menu")

    def enter_menu(self):
        if self.state != settings.IN_MENU_STATE:
            self.menu.show()

    def exit_menu(self):
        self.menu.hide()
        self.game.stop()

    def start_game(self):
        def update_hp(uid, hp):
            self.messenger.send("hud_set_hp", [uid, hp])

        if self.game is None:
            self.menu.hide()
            self.menu.hide_start_btn()
            self.state = settings.IN_GAME_STATE
            self.game = BattleTank(self)
            self.hud.show()
        self.accept("update-hp", update_hp)

    def exit_game(self):
        if self.game is not None:
            self.game.stop()
        self.userExit()

    def __escape(self):
        if self.state == settings.IN_GAME_STATE:
            self.state = settings.IN_MENU_STATE
            self.menu.show()
            self.hud.hide()
            self.disableAllAudio()

        elif self.state == settings.IN_MENU_STATE and self.game is not None:
            self.state = settings.IN_GAME_STATE
            self.menu.hide()
            self.hud.show()
            if not settings.DISABLE_SFX:
                self.enableAllAudio()


def main():
    g = MainGame()
    g.run()


if __name__ == '__main__':
    main()
