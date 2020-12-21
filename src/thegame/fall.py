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
    Point3, CollisionHandlerEvent
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
    "q": False,
    "e": False,
}


def update_key_map(key, state):
    KEY_MAP[key] = state


class TheGameWindow(ShowBase):
    SPEED = 50

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_background_color(0.2, 0.2, 0.2, 0.6)
        # disables the default mouse camera control
        # self.disable_mouse()
        self.cam.set_pos(0, -100, 0)

        # lights
        self.plight = PointLight("pl")
        self.plight.set_color((1, 1, 1, 1))
        self.plight.set_color((1, 1, 1, 1))
        self.plight.set_attenuation((1, 0, 0))
        self.plnp = self.render.attach_new_node(self.plight)
        self.plnp.set_pos(0, 0, 100)
        self.render.set_light(self.plnp)

        self.amblight = AmbientLight("ambl")
        self.amblight.set_color((0.1, 0.1, 0.1, 1))
        self.ambnp = self.render.attach_new_node(self.amblight)
        self.render.set_light(self.ambnp)

        # shadows
        self.plight.set_shadow_caster(True, 2048, 2048)
        self.render.set_shader_auto()

        # floor
        self.floor = self.loader.loadModel(str(settings.egg / "floor.egg"))
        self.floor.reparent_to(self.render)
        self.floor.set_name("floor")

        self.sphere = self.loader.loadModel("models/misc/sphere")
        self.sphere.set_pos(0, 0, 20)
        self.sphere.set_name("sphere")
        self.sphere.set_scale(3.0)
        self.sphere.set_color((1, 1, 1, 1))
        self.sphere.reparent_to(self.render)

        # key assigment
        self.accept("w", update_key_map, ["w", True])
        self.accept("w-up", update_key_map, ["w", False])

        self.accept("s", update_key_map, ["s", True])
        self.accept("s-up", update_key_map, ["s", False])

        self.accept("a", update_key_map, ["a", True])
        self.accept("a-up", update_key_map, ["a", False])

        self.accept("d", update_key_map, ["d", True])
        self.accept("d-up", update_key_map, ["d", False])

        self.accept("e", update_key_map, ["e", True])
        self.accept("e-up", update_key_map, ["e", False])

        self.accept("q", update_key_map, ["q", True])
        self.accept("q-up", update_key_map, ["q", False])

        # collision
        self.cTrav = CollisionTraverser()
        self.col_pusher = CollisionHandlerPusher()

        # self.handler = CollisionHandlerEvent()
        # self.handler.addInPattern('%fn-into-%in')
        # self.accept('player-into-Floor', self.handle_collision)

        sphere_collider = self.sphere.attachNewNode(CollisionNode('player'))
        sphere_collider.node().addSolid(CollisionSphere(0, 0, 0, 1))
        sphere_collider.show()

        # floor_collider = self.floor.attachNewNode(CollisionNode('ground_zero'))
        # floor_collider.node().addSolid(CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, 0))))
        # floor_collider.show()

        self.col_pusher.addCollider(sphere_collider, self.sphere)
        self.cTrav.showCollisions(self.render)
        # self.cTrav.addCollider(sphere_collider, self.handler)
        self.cTrav.addCollider(sphere_collider, self.col_pusher)

        # uppdate
        self.task_mgr.add(self.update)

    def handle_collision(self, entry):
        print(self.floor.get_name())
        for k in KEY_MAP:
            KEY_MAP[k] = False
        print(entry)

    def update(self, task: Task):
        dt = globalClock.getDt()

        if KEY_MAP["e"]:
            pos = self.sphere.get_pos()
            pos.z += self.SPEED * dt
            self.sphere.set_pos(pos)

        if KEY_MAP["q"]:
            pos = self.sphere.get_pos()
            pos.z -= self.SPEED * dt
            self.sphere.set_pos(pos)

        if KEY_MAP["a"]:
            pos = self.sphere.get_pos()
            pos.x -= self.SPEED * dt
            self.sphere.set_pos(pos)

        if KEY_MAP["d"]:
            pos = self.sphere.get_pos()
            pos.x += self.SPEED * dt
            self.sphere.set_pos(pos)

        if KEY_MAP["w"]:
            pos = self.sphere.get_pos()
            pos.y += self.SPEED * dt
            self.sphere.set_pos(pos)

        if KEY_MAP["s"]:
            pos = self.sphere.get_pos()
            pos.y -= self.SPEED * dt
            self.sphere.set_pos(pos)

        return task.cont


def main():
    inst = TheGameWindow()
    inst.run()


if __name__ == '__main__':
    main()
