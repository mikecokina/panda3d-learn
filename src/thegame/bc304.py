from direct.showbase.ShowBase import ShowBase, NodePath
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task.Task import Task
from panda3d.core import PointLight

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
}


def update_key_map(key, state):
    KEY_MAP[key] = state


class TheGameWindow(ShowBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_background_color(0, 0, 0, 0.6)
        # disables the default mouse camera control
        # self.disable_mouse()
        self.cam.set_pos(0, -100, 0)

        self.sphere = self.loader.loadModel("models/misc/sphere")
        self.sphere.reparent_to(self.render)
        self.sphere.set_pos(10, 10, 10)
        self.sphere.set_scale(0.2)

        self.empty = NodePath("empty")
        self.empty.reparent_to(self.render)

        self.plight = PointLight("pl")
        self.plight.set_color((1, 1, 1, 1))
        self.plight.set_color((1, 1, 1, 1))
        self.plight.set_attenuation((1, 0, 0))

        self.plnp = self.render.attach_new_node(self.plight)
        self.render.set_light(self.plnp)
        self.plnp.reparent_to(self.sphere)

        self.bc304 = self.loader.loadModel(str(settings.egg / "bc304.egg"))
        # left-rigth, far-from-camera, vertical-movement
        # x, y, z
        self.bc304.set_pos(0, 0, 0)
        self.bc304.set_scale(0.1)
        self.bc304.reparent_to(self.render)
        # heading, pitch,, roll
        self.bc304.set_hpr(280, 10, 0)

        self.x, self.y, self.z = 0.0, 0.0, 0.0
        self.h, self.p = 0.0, 0.0
        self.task_mgr.add(self.update)

        # self.accept("mouse1", self.to_pegasus)
        self.accept("mouse1-up", self.to_pegasus)

        # self.accept("mouse2", self.to_pegasus)
        self.accept("mouse2-up", self.to_pegasus)

        # self.accept("mouse3", self.to_pegasus)
        self.accept("mouse3-up", self.to_pegasus)

        self.accept("arrow_left", update_key_map, ["left", True])
        self.accept("arrow_left-up", update_key_map, ["left", False])

        self.accept("arrow_right", update_key_map, ["right", True])
        self.accept("arrow_right-up", update_key_map, ["right", False])

        self.accept("arrow_up", update_key_map, ["up", True])
        self.accept("arrow_up-up", update_key_map, ["up", False])

        self.accept("arrow_down", update_key_map, ["down", True])
        self.accept("arrow_down-up", update_key_map, ["down", False])

        self.accept("space", update_key_map, ["space", True])
        self.accept("space-up", update_key_map, ["space", False])

        self.accept("w", update_key_map, ["w", True])
        self.accept("w-up", update_key_map, ["w", False])

        self.accept("s", update_key_map, ["s", True])
        self.accept("s-up", update_key_map, ["s", False])

        self.accept("a", update_key_map, ["a", True])
        self.accept("a-up", update_key_map, ["a", False])

        self.accept("d", update_key_map, ["d", True])
        self.accept("d-up", update_key_map, ["d", False])

    def to_pegasus(self):
        # mouse_pos = self.mouseWatcherNode.getMouse()
        # mouse_pos_3d = (mouse_pos[0], 0, mouse_pos[1])
        # mouse_pos_button = self.button.getRelativePoint(render, mouse_pos_3d)
        # print(mouse_pos_3d)

        # pointer = self.win.get_pointer(0)
        # self.z = -(pointer.get_y() - (720 / 2)) / 10
        # print(self.z)

        # self.bc304.set_pos(pointer.get_x(), 0, self.z)
        pass

    def update(self, task: Task):
        dt = globalClock.getDt()

        if KEY_MAP["up"]:
            self.bc304.set_pos(self.x, self.y, self.z)
            self.z += 2.0 * dt

        if KEY_MAP["down"]:
            self.bc304.set_pos(self.x, self.y, self.z)
            self.z -= 2.0 * dt

        if KEY_MAP["right"]:
            self.bc304.set_pos(self.x, self.y, self.z)
            self.x += 2.0 * dt

        if KEY_MAP["left"]:
            self.bc304.set_pos(self.x, self.y, self.z)
            self.x -= 2.0 * dt

        if KEY_MAP["w"]:
            pos = self.sphere.get_pos()
            pos.z += 3 * dt
            self.sphere.set_pos(pos)

        if KEY_MAP["s"]:
            pos = self.sphere.get_pos()
            pos.z -= 3 * dt
            self.sphere.set_pos(pos)

        if KEY_MAP["a"]:
            pos = self.sphere.get_pos()
            pos.x -= 3 * dt
            self.sphere.set_pos(pos)

        if KEY_MAP["d"]:
            pos = self.sphere.get_pos()
            pos.x += 3 * dt
            self.sphere.set_pos(pos)



        # self.z -= 0.5 * dt
        # self.bc304.set_hpr(self.h, self.p, 0)
        # self.h += 0.1
        # self.p += 0.1

        return task.cont


def main():
    inst = TheGameWindow()
    inst.run()


if __name__ == '__main__':
    main()
