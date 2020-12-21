from direct.showbase.ShowBase import ShowBase, SamplerState, TransparencyAttrib, TextureStage, OrthographicLens
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task.Task import Task
from panda3d.core import PointLight, AmbientLight
from direct.filter.CommonFilters import CommonFilters
from thegame import settings


class TheGameWindow(ShowBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.speed = 50
        self.set_background_color(0.1, 0.1, 0.1, 1.0)
        self.cam.set_pos(0, -10, 0)

        self.cube1 = self.loader.loadModel("models/box")
        self.cube1.setPos(-5, 0, 0)
        self.cube1.setScale(50)
        self.cube1.reparentTo(self.render)

        self.cube2 = self.loader.loadModel("models/box")
        self.cube2.setPos(5, 70, 0)
        self.cube2.setScale(50)
        self.cube2.reparentTo(self.render)

        lens = OrthographicLens()
        lens.setFilmSize(16 * 15, 9 * 15)
        lens.setNearFar(-150, 150)
        self.cam.node().setLens(lens)


def main():
    inst = TheGameWindow()
    inst.run()


if __name__ == '__main__':
    main()
