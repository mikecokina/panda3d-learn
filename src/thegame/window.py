from direct.showbase.ShowBase import ShowBase
from thegame import settings


class TheGameWindow(ShowBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # disables the default mouse camera control
        # self.disable_mouse()

        model_box = self.loader.loadModel("models/box")
        # left-rigth, far-from-camera, vertical-movement
        # x, y, z
        model_box.set_pos(0, 10, 0)
        model_box.reparent_to(self.render)

        model_panda = self.loader.loadModel("models/panda")
        model_panda.set_scale(0.2, 0.2, 0.2)
        model_panda.set_pos(0, 100, 0)
        model_panda.reparent_to(self.render)

        model_environemnt = self.loader.loadModel("models/environment")
        model_environemnt.set_scale(0.1, 0.1, 0.1)
        model_environemnt.reparent_to(self.render)


def main():
    inst = TheGameWindow()
    inst.run()


if __name__ == '__main__':
    main()
