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
    Point3, CollisionHandlerEvent, AudioSound, CollisionBox
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

SHOW_COLLIDERS = False


def update_key_map(key, state):
    KEY_MAP[key] = state


class SFXContainer(object):
    __slots__ = ["tank_fire", "tank_moving"]

    def loader(self, loader):
        setattr(self, "tank_fire", loader.loadSfx(settings.sfx / "tank-fire.wav"))
        setattr(self, "tank_moving", loader.loadSfx(settings.sfx / "tank-moving.wav"))
        return self


class TheGameWindow(ShowBase):
    BULLET_SPEED = 200
    SPEED = 35
    BULLETS = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sfx = SFXContainer().loader(self.loader)
        self.set_background_color(0.2, 0.2, 0.2, 0.6)
        # disables the default mouse camera control
        # self.disable_mouse()
        # self.cam.set_pos(0, -250, 100)
        # self.cam.set_p(-20)
        self.musicManager.setConcurrentSoundLimit(3)

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
        self.plight.set_shadow_caster(True, 1024, 1024)
        self.render.set_shader_auto()

        # floor
        self.floor = self.loader.loadModel(str(settings.egg / "floor.egg"))
        self.floor.reparent_to(self.render)
        self.floor.set_name("floor")

        # houses
        self.house_01 = self.loader.loadModel(str(settings.egg / "house_01.egg"))
        self.house_01.reparent_to(self.render)
        self.house_01.set_name("house01")
        self.house_01.set_scale(1.5)
        self.house_01.set_pos(20, 50, 0)

        self.house_02 = self.loader.loadModel(str(settings.egg / "house_02.egg"))
        self.house_02.reparent_to(self.render)
        self.house_02.set_name("house02")
        self.house_02.set_scale(1.5)
        self.house_02.set_pos(-50, 10, 0)

        # player
        self.tank = self.loader.loadModel(str(settings.egg / "tank.egg"))

        self.tank.set_pos(0, 0, 5)
        self.tank.set_name("tank")
        self.tank.set_scale(3.0)
        self.tank.set_color((1, 1, 1, 1))
        self.tank.reparent_to(self.render)

        # 3rd person camera lock
        self.camera.reparent_to(self.tank)
        self.cam.set_pos(0, -25, 10)
        self.cam.lookAt(self.tank)
        self.cam.setP(self.camera.getP() - 20)

        self.gun = self.loader.loadModel("models/misc/sphere")
        self.gun.set_pos(0.0, 4.5, 1.8)
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
        self.pusher = CollisionHandlerPusher()
        # self.pusher.setHorizontal(True)

        tank_collider = self.tank.attachNewNode(CollisionNode('tank-collider'))
        tank_collider.node().addSolid(CollisionBox(Point3(-2, -3, 0), Point3(2, 3, 2.25)))

        house_collider = self.house_01.attachNewNode(CollisionNode('house-collider'))
        house_collider.node().addSolid(CollisionBox(Point3(0, 0, 0), Point3(16, 16, 17)))

        floor_collider = self.floor.attachNewNode(CollisionNode('ground-zero-collider'))
        floor_collider.node().addSolid(CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, 0))))

        self.pusher.addCollider(tank_collider, self.tank)
        self.cTrav.addCollider(tank_collider, self.pusher)

        # show.hide all colliders
        if SHOW_COLLIDERS:
            floor_collider.show()
            tank_collider.show()
            house_collider.show()
            self.cTrav.showCollisions(self.render)

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
        self.sfx.tank_fire.stop()
        self.sfx.tank_fire.play()
        position = self.gun.get_pos(self.render)
        heading = self.tank.get_h() + 90

        bullet = self.loader.loadModel("models/misc/sphere")
        bullet.set_pos(position)
        bullet.set_scale(0.3)
        bullet.set_color((1, 1, 1, 1))
        bullet.reparent_to(self.render)
        self.BULLETS.append([bullet, heading])
        # print(f"fire bullet 1/{len(self.BULLETS)} from {position} to direction {heading}")

    def handle_collision(self, entry):
        print(self.floor.get_name())
        for k in KEY_MAP:
            KEY_MAP[k] = False
        print(entry)

    def update(self, task: Task):
        dt, ft = globalClock.getDt(), globalClock.getFrameTime()
        tank_heading, tank_position = self.tank.get_h(), self.tank.get_pos()
        is_moving = KEY_MAP["w"] or KEY_MAP["s"] or KEY_MAP["a"] or KEY_MAP["d"]

        if is_moving and self.sfx.tank_moving.status() != AudioSound.PLAYING:
            self.sfx.tank_moving.play()

        if not is_moving and self.sfx.tank_moving.status() == AudioSound.PLAYING:
            self.sfx.tank_moving.stop()

        if KEY_MAP["up"]:
            tank_position.z += self.SPEED * dt
            self.tank.set_pos(tank_position)

        if KEY_MAP["down"]:
            tank_position.z -= self.SPEED * dt
            self.tank.set_pos(tank_position)

        if KEY_MAP["q"]:
            tank_position.x -= self.SPEED * dt
            self.tank.set_pos(tank_position)

        if KEY_MAP["e"]:
            tank_position.x += self.SPEED * dt
            self.tank.set_pos(tank_position)

        if KEY_MAP["w"]:
            dx = (self.SPEED * dt) * np.cos(np.radians(tank_heading + 90))
            dy = (self.SPEED * dt) * np.sin(np.radians(tank_heading + 90))
            tank_position.y, tank_position.x = tank_position.y + dy, tank_position.x + dx
            self.tank.set_pos(tank_position)

        if KEY_MAP["s"]:
            dx = - (self.SPEED * dt) * np.cos(np.radians(tank_heading + 90))
            dy = - (self.SPEED * dt) * np.sin(np.radians(tank_heading + 90))
            tank_position.y, tank_position.x = tank_position.y + dy, tank_position.x + dx
            self.tank.set_pos(tank_position)

        if KEY_MAP["d"] and not KEY_MAP["s"]:
            h = self.tank.get_h()
            h -= self.SPEED * dt * 2
            self.tank.set_h(h)

        if KEY_MAP["a"] and not KEY_MAP["s"]:
            h = self.tank.get_h()
            h += self.SPEED * dt * 2
            self.tank.set_h(h)

        if KEY_MAP["d"] and KEY_MAP["s"]:
            h = self.tank.get_h()
            h += self.SPEED * dt * 2
            self.tank.set_h(h)

        if KEY_MAP["a"] and KEY_MAP["s"]:
            h = self.tank.get_h()
            h -= self.SPEED * dt * 2
            self.tank.set_h(h)

        return task.cont


def main():
    inst = TheGameWindow()
    inst.run()


if __name__ == '__main__':
    main()
