import numpy as np
from direct.filter.CommonFilters import CommonFilters
from direct.showbase.ShowBase import (
    ShowBase,
    AmbientLight,
    CollisionNode,
    CollisionSphere,
    CollisionHandlerPusher,
    CollisionTraverser,
    CollisionPlane,
    Plane,
    Vec3,
    Point3, CollisionHandlerEvent, AudioSound, CollisionBox, AntialiasAttrib, DirectionalLight, BitMask32
)
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task.Task import Task
from panda3d.core import PointLight

from thegame import settings

KEY_MAP = {
    "w": False,
    "s": False,
    "a": False,
    "d": False,
    "up": False,
    "down": False,
    "right": False,
    "left": False,
    "e": False,
    "q": False,
}


def update_key_map(key, state):
    KEY_MAP[key] = state


class Controller(object):
    def __init__(self, accept):
        # key assigment
        accept("w", update_key_map, ["w", True])
        accept("w-up", update_key_map, ["w", False])

        accept("s", update_key_map, ["s", True])
        accept("s-up", update_key_map, ["s", False])

        accept("a", update_key_map, ["a", True])
        accept("a-up", update_key_map, ["a", False])

        accept("d", update_key_map, ["d", True])
        accept("d-up", update_key_map, ["d", False])

        accept("e", update_key_map, ["e", True])
        accept("e-up", update_key_map, ["e", False])

        accept("q", update_key_map, ["q", True])
        accept("q-up", update_key_map, ["q", False])

        accept("arrow_down", update_key_map, ["down", True])
        accept("arrow_down-up", update_key_map, ["down", False])

        accept("arrow_up", update_key_map, ["up", True])
        accept("arrow_up-up", update_key_map, ["up", False])

        accept("arrow_left", update_key_map, ["left", True])
        accept("arrow_left-up", update_key_map, ["left", False])

        accept("arrow_right", update_key_map, ["right", True])
        accept("arrow_right-up", update_key_map, ["right", False])


class TheGameWindow(ShowBase):
    SPEED = 35

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_background_color(0.2, 0.2, 0.2, 0.6)
        # self.render.setAntialias(AntialiasAttrib.MMultisample)
        self.controller = Controller(self.accept)
        self.cam.set_pos(0, -200, 10)

        self.player = self.loader.loadModel(str(settings.egg / "a2.egg"))
        self.player.set_pos(0, 0, 0)
        self.player.set_scale(3.0)
        self.player.set_color((0, 0, 0, 1))
        self.player.reparent_to(self.render)

        self.plane = self.loader.loadModel(str(settings.egg / "plane.egg"))
        self.plane.reparent_to(self.render)
        self.plane.set_name("plane")

        self.cube_01 = self.loader.loadModel(str(settings.egg / "bd-cube.egg"))
        self.cube_01.reparent_to(self.render)
        self.cube_01.set_name("cube")
        self.cube_01.set_scale(20)
        self.cube_01.set_pos(-100, 30, 20)

        self.cube_02 = self.loader.loadModel(str(settings.egg / "bd-cube.egg"))
        self.cube_02.reparent_to(self.render)
        self.cube_02.set_name("cube")
        self.cube_02.set_scale(10)
        self.cube_02.set_pos(-30, 100, 10)

        # ##############################################################################################################

        # player
        self.light_model = self.loader.loadModel("models/misc/sphere")
        self.light_model.set_pos(0, 0, 20)
        self.light_model.set_scale(3.0)
        self.light_model.set_color((1, 1, 1, 1))
        self.light_model.reparent_to(self.render)

        # lights
        if True:
            day_light = DirectionalLight("sun")
            day_light.set_color((1, 1, 1, 1))
            self.sun = self.render.attach_new_node(day_light)
            self.sun.set_p(-20)
            self.sun.set_h(10)

            self.cube_01.set_light(self.sun)
            self.cube_02.set_light(self.sun)
            self.player.set_light(self.sun)
            self.plane.set_light(self.sun)

        sun_spotlight = PointLight("sun_spotlight")
        sun_spotlight.set_color((1, 1, 1, 1))
        self.sun_spotlight_nodepath = self.render.attach_new_node(sun_spotlight)
        self.sun_spotlight_nodepath.reparent_to(self.light_model)

        self.cube_01.set_light(self.sun_spotlight_nodepath)
        self.cube_02.set_light(self.sun_spotlight_nodepath)
        self.player.set_light(self.sun_spotlight_nodepath)
        self.plane.set_light(self.sun_spotlight_nodepath)

        amblight = AmbientLight("ambient_light")
        amblight.set_color((0.01, 0.01, 0.01, 1))
        self.ambnp = self.render.attach_new_node(amblight)
        self.cube_01.set_light(self.ambnp)
        self.cube_02.set_light(self.ambnp)
        self.player.set_light(self.ambnp)
        self.plane.set_light(self.ambnp)

        sun_spotlight.set_shadow_caster(True, 2048, 2048)
        self.render.set_shader_auto()

        # shadows
        # self.day_light.set_shadow_caster(True, 2048, 2048)
        # self.render.set_shader_auto()

        # uppdate
        self.task_mgr.add(self.update)

    def update(self, task: Task):
        dt, ft = globalClock.getDt(), globalClock.getFrameTime()
        heading, position, pitch = self.player.get_h(), self.player.get_pos(), self.player.get_p()

        # self.sun.set_p(self.sun.get_p() - (dt * 20))
        # self.sun.set_h(self.sun.get_h() - (dt * 20))

        if KEY_MAP["up"]:
            position.z += self.SPEED * dt
            self.player.set_pos(position)

        if KEY_MAP["down"]:
            position.z -= self.SPEED * dt
            self.player.set_pos(position)

        if KEY_MAP["q"]:
            position.x -= self.SPEED * dt
            self.player.set_pos(position)

        if KEY_MAP["e"]:
            position.x += self.SPEED * dt
            self.player.set_pos(position)

        if KEY_MAP["w"]:
            dx = (self.SPEED * dt) * np.cos(np.radians(heading + 90))
            dy = (self.SPEED * dt) * np.sin(np.radians(heading + 90))
            position.y, position.x = position.y + dy, position.x + dx
            self.player.set_pos(position)

        if KEY_MAP["s"]:
            dx = - (self.SPEED * dt) * np.cos(np.radians(heading + 90))
            dy = - (self.SPEED * dt) * np.sin(np.radians(heading + 90))
            position.y, position.x = position.y + dy, position.x + dx
            self.player.set_pos(position)

        if KEY_MAP["d"] and not KEY_MAP["s"]:
            heading -= self.SPEED * dt * 2
            self.player.set_h(heading)

        if KEY_MAP["a"] and not KEY_MAP["s"]:
            heading += self.SPEED * dt * 2
            self.player.set_h(heading)

        if KEY_MAP["d"] and KEY_MAP["s"]:
            heading += self.SPEED * dt * 2
            self.player.set_h(heading)

        if KEY_MAP["a"] and KEY_MAP["s"]:
            heading -= self.SPEED * dt * 2
            self.player.set_h(heading)

        if KEY_MAP["left"]:
            pitch += self.SPEED * dt * 2
            self.player.set_p(pitch)

        if KEY_MAP["right"]:
            pitch -= self.SPEED * dt * 2
            self.player.set_p(pitch)

        return task.cont


def main():
    inst = TheGameWindow()
    inst.run()


if __name__ == '__main__':
    main()
