from direct.showbase.ShowBase import ShowBase
from thegame import settings


class TheGameWindow(ShowBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # disables the default mouse camera control
        # self.disable_mouse()

        model_box_1 = self.loader.loadModel(str(settings.egg / "bd-cube.egg"))
        # left-rigth, far-from-camera, vertical-movement
        # x, y, z
        model_box_1.set_pos(0, 10, 0)
        model_box_1.reparent_to(self.render)
        model_box_1_node = model_box_1.node()

        model_box_2 = self.loader.loadModel(str(settings.egg / "bd-cube.egg"))
        model_box_2.set_scale(0.5, 0.5, 0.5)
        model_box_2.set_pos(0, -5, 0)
        model_box_2.reparent_to(model_box_1)


def main():
    inst = TheGameWindow()
    inst.run()


if __name__ == '__main__':
    main()
