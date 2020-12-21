import numpy as np
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
    "up": False,
    "down": False,
    "e": False,
    "q": False,
}


def update_key_map(key, state):
    KEY_MAP[key] = state


class TheGameWindow(ShowBase):
    BULLET_SPEED = 200
    SPEED = 50
    BULLETS = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_background_color(0.2, 0.2, 0.2, 0.6)
        # disables the default mouse camera control
        # self.disable_mouse()
        self.cam.set_pos(0, -250, 100)
        self.cam.set_p(-20)

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

        # player
        self.tank = self.loader.loadModel(str(settings.egg / "a2.egg"))

        self.tank.set_pos(0, 0, 20)
        self.tank.set_name("tank")
        self.tank.set_scale(3.0)
        self.tank.set_color((1, 1, 1, 1))
        self.tank.reparent_to(self.render)

        # self.camera.reparentTo(self.sphere)
        # self.camera.setPos(0, 30, 10)
        # self.camera.lookAt(self.sphere)
        # self.camera.setP(self.camera.getP() + 15)

        self.gun = self.loader.loadModel("models/misc/sphere")
        self.gun.set_pos(0.0, 0.0, 1.0)
        self.gun.set_name("gun")
        self.gun.set_scale(0.1)
        self.gun.set_color((1, 1, 1, 1))
        self.gun.reparent_to(self.tank)

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

        self.accept("arrow_down", update_key_map, ["down", True])
        self.accept("arrow_down-up", update_key_map, ["down", False])

        self.accept("arrow_up", update_key_map, ["up", True])
        self.accept("arrow_up-up", update_key_map, ["up", False])

        self.accept("space", self.fire_bullet)

        # collision
        self.cTrav = CollisionTraverser()
        self.col_pusher = CollisionHandlerPusher()

        tank_collider = self.tank.attachNewNode(CollisionNode('tank-collider'))
        tank_collider.node().addSolid(CollisionSphere(0, 0, 0, 1))
        tank_collider.show()

        self.col_pusher.addCollider(tank_collider, self.tank)
        self.cTrav.showCollisions(self.render)
        self.cTrav.addCollider(tank_collider, self.col_pusher)

        # uppdate
        self.task_mgr.add(self.update)
        self.task_mgr.add(self.update_bullets)

    def update_bullets(self, task: Task):
        dt = globalClock.getDt()
        rmi = []
        for idx, entry in enumerate(self.BULLETS):
            bullet, heading = entry
            bullet_pos = bullet.get_pos()
            if bullet_pos.y > 100:
                bullet.removeNode()
                rmi.append(idx)
                continue

            dx = (self.BULLET_SPEED * dt) * np.cos(np.radians(heading))
            dy = (self.BULLET_SPEED * dt) * np.sin(np.radians(heading))

            bullet_pos.y += dy
            bullet_pos.x += dx
            bullet.set_pos(bullet_pos)

        self.BULLETS = [b for i, b in enumerate(self.BULLETS) if i not in rmi]
        return task.cont

    def fire_bullet(self):
        position = self.gun.get_pos(self.render)
        heading = self.tank.get_h() + 90

        bullet = self.loader.loadModel("models/misc/sphere")
        bullet.set_pos(position)
        bullet.set_scale(0.5)
        bullet.set_color((1, 1, 1, 1))
        bullet.reparent_to(self.render)
        self.BULLETS.append([bullet, heading])
        print(f"fire bullet 1/{len(self.BULLETS)} from {position} to direction {heading}")

    def handle_collision(self, entry):
        print(self.floor.get_name())
        for k in KEY_MAP:
            KEY_MAP[k] = False
        print(entry)

    def update(self, task: Task):
        dt = globalClock.getDt()

        if KEY_MAP["up"]:
            pos = self.tank.get_pos()
            pos.z += self.SPEED * dt
            self.tank.set_pos(pos)

        if KEY_MAP["down"]:
            pos = self.tank.get_pos()
            pos.z -= self.SPEED * dt
            self.tank.set_pos(pos)

        if KEY_MAP["a"]:
            pos = self.tank.get_pos()
            pos.x -= self.SPEED * dt
            self.tank.set_pos(pos)

        if KEY_MAP["d"]:
            pos = self.tank.get_pos()
            pos.x += self.SPEED * dt
            self.tank.set_pos(pos)

        if KEY_MAP["w"]:
            pos = self.tank.get_pos()
            pos.y += self.SPEED * dt
            self.tank.set_pos(pos)

        if KEY_MAP["s"]:
            pos = self.tank.get_pos()
            pos.y -= self.SPEED * dt
            self.tank.set_pos(pos)

        if KEY_MAP["e"]:
            h = self.tank.get_h()
            h -= self.SPEED * dt * 2
            self.tank.set_h(h)

        if KEY_MAP["q"]:
            h = self.tank.get_h()
            h += self.SPEED * dt * 2
            self.tank.set_h(h)

        return task.cont


def main():
    inst = TheGameWindow()
    inst.run()


if __name__ == '__main__':
    main()
