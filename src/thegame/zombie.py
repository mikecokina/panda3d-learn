from direct.showbase.ShowBase import ShowBase, SamplerState, TransparencyAttrib, TextureStage
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task.Task import Task
from panda3d.core import PointLight, AmbientLight
from direct.filter.CommonFilters import CommonFilters
from thegame import settings

KEY_MAP = {
    "up": False,
    "down": False,
    "right": False,
    "left": False,
    "space": False,
    "w": False,
    "s": False,
    "a": False,
    "d": False,
    "q": False,
    "e": False,
}


def update_key_map(key, state):
    KEY_MAP[key] = state


class TheGameWindow(ShowBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.speed = 50
        self.set_background_color(0.1, 0.1, 0.1, 1.0)
        self.cam.set_pos(0, -10, 0)

        self.plane = self.loader.loadModel(str(settings.egg / "plane2x2.egg"))
        self.texture = self.loader.loadTexture(str(settings.tex / "zombie.png"))

        self.plane.setTexture(self.texture)
        self.texture.setMagfilter(SamplerState.FT_nearest)
        self.plane.setTransparency(TransparencyAttrib.MAlpha)
        self.plane.reparentTo(self.render)

        self.tx = 0.0
        self.tx_offset = 1.0 / 6.0
        self.texture_update = 0
        self.taskMgr.add(self.update, "Update texture")

    def update(self, task: Task):
        dt = globalClock.getDt()
        self.plane.setTexOffset(TextureStage.getDefault(), self.tx, 0)

        self.texture_update += 5
        if self.texture_update % 6 * dt == 0:
            self.tx += self.tx_offset
            self.texture_update = 0
        return task.cont


def main():
    inst = TheGameWindow()
    inst.run()


if __name__ == '__main__':
    main()
