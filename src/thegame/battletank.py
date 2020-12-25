import numpy as np
from direct.filter.CommonFilters import CommonFilters
from direct.showbase.ShowBase import (
    AmbientLight,
    CollisionNode,
    CollisionPlane,
    Plane,
    Vec3,
    Point3,
    AudioSound,
    CollisionBox,
    DirectionalLight,
    NodePath
)
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task.Task import Task
from panda3d.core import PointLight
from thegame import settings
from thegame.config.logger import getLogger

logger = getLogger("battle-tank")

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


class Tank(object):
    __slots__ = ["tank", "gun", "hp", "tank_moving_sound", "tank_fire_sound", "tank_idle_sound",
                 "engine_running", "f"]

    SFX_KEYS = ["tank_moving_sound", "tank_fire_sound", "tank_idle_sound"]

    def __init__(self, tank, gun, framework):
        self.tank = tank
        self.gun = gun
        self.hp = 100
        self.engine_running = False
        self.f = framework

        setattr(self, "tank_fire_sound", self.f.loader.loadSfx(settings.sfx / "tank-fire.wav"))
        setattr(self, "tank_moving_sound", self.f.loader.loadSfx(settings.sfx / "tank-moving.wav"))
        setattr(self, "tank_idle_sound", self.f.loader.loadSfx(settings.sfx / "tank-idle.wav"))

    def handle_sfx(self):
        is_moving = KEY_MAP["w"] or KEY_MAP["s"] or KEY_MAP["a"] or KEY_MAP["d"]

        # start engine
        if is_moving and not self.engine_running:
            self.engine_running = True

        # stop sounds
        if not is_moving and self.tank_moving_sound.status() == AudioSound.PLAYING:
            self.tank_moving_sound.stop()

        if is_moving and self.tank_idle_sound.status() == AudioSound.PLAYING:
            self.tank_idle_sound.stop()

        # play sounds
        if is_moving and self.tank_moving_sound.status() != AudioSound.PLAYING:
            self.tank_moving_sound.play()

        if not is_moving and self.tank_idle_sound.status() != AudioSound.PLAYING and self.engine_running:
            self.tank_idle_sound.play()

    def hit(self):
        self.hp -= 0.01
        self.f.messenger.send("update-hp", ["player", self.hp])


class BattleTank(object):
    BULLET_SPEED = 500
    SPEED = 40
    TURN_SPEED = 25

    def __init__(self, framework, *args, **kwargs):
        self.bullets = []
        self.environment = {}
        self.colliders = {}
        self.task_manager = []

        super().__init__(*args, **kwargs)
        self.f = framework
        self.controller = Controller(self.f.accept, self)
        self.f.set_background_color(0.2, 0.2, 0.2, 0.6)

        if settings.ALLOW_FILTERS:
            self.filter = CommonFilters(self.f.win, self.f.cam)
            self.filter.set_bloom(mintrigger=0.99, size="small")
            # self.filter.set_blur_sharpen(amount=0.99)

        self.base_node = NodePath("base")
        self.base_node.reparent_to(self.f.render)

        # floor
        self.plane = self.create_model(settings.egg / "plane", self.base_node, "ground-zero", color=(1, 1, 1, 1))
        self.create_model(settings.egg / "house_01", self.base_node, "house-01", position=(20, 50, 0), scale=1.5)
        self.create_model(settings.egg / "house_02", self.base_node, "house-02", position=(-50, 10, 0), scale=1.5)

        self.sun_light_model = self.create_model("models/misc/sphere", self.base_node, "sun", position=(0, -150, 250),
                                                 scale=5.0, color=(1, 1, 1, 1), _store=False)

        tank = self.create_model(settings.egg / "tank", self.base_node, "player", scale=3.0, position=(0.0, 0.0, 1e-3))
        gun = self.create_model("models/misc/sphere", tank, "player-gun",
                                position=(0.0, 4.5, 1.755), scale=0.1, _store=False)
        self.tank = Tank(tank, gun, framework=self.f)
        self._tank = self.tank.tank

        # point light for shadows
        sun_light = PointLight("sun-light")
        sun_light.set_color((0.4, 0.4, 0.4, 1))
        self.sun_light_node = self.base_node.attach_new_node(sun_light)
        self.sun_light_node.reparent_to(self.sun_light_model)
        self.redistribute_light(self.sun_light_node)
        self.plane.set_light(self.sun_light_node)

        # daylight
        if settings.ALLOW_DAYLIGHT:
            day_light = DirectionalLight("day-light")
            day_light.set_color((1, 1, 1, 1))
            self.daylight_node = self.f.render.attach_new_node(day_light)
            self.daylight_node.set_p(-20)
            self.daylight_node.set_h(10)
            self.daylight_node.reparent_to(self.sun_light_model)
            self.redistribute_light(self.daylight_node)

        # shadows
        if settings.ALLOW_SHADOWS:
            sun_light.set_shadow_caster(True, 2048, 2048)
            self.f.render.set_shader_auto()

        # 3rd person camera lock
        if settings.TRD_PERSON_CAM:
            self.f.camera.reparent_to(self.tank.tank)
            self.f.cam.set_pos(0, -25, 10)
            self.f.cam.lookAt(self.tank.tank)
            self.f.cam.setP(self.f.camera.getP() - 20)

        if settings.ALLOW_AMBIENT:
            amblight = AmbientLight("ambient-light")
            amblight.set_color((0.2, 0.2, 0.2, 1))
            self.amblight_node = self.f.render.attach_new_node(amblight)
            self.redistribute_light(self.amblight_node)

        # colliders
        tank_collider = self.environment["player"].attachNewNode(CollisionNode('player-collider'))
        tank_collider.node().addSolid(CollisionBox(Point3(-2, -3, 0), Point3(2, 3, 2.25)))
        self.colliders['player-collider'] = tank_collider

        house_01_collider = self.environment["house-01"].attachNewNode(CollisionNode('house-01-collider'))
        house_01_collider.node().addSolid(CollisionBox(Point3(0, 2, 0), Point3(14, 16, 17)))
        self.colliders['house-01'] = house_01_collider

        house_02_collider = self.environment["house-02"].attachNewNode(CollisionNode('house-02-collider'))
        house_02_collider.node().addSolid(CollisionBox(Point3(0, 0, 0), Point3(21, 27, 37)))
        self.colliders['house-02'] = house_02_collider

        floor_collider = self.environment["ground-zero"].attachNewNode(CollisionNode('ground-zero-collider'))
        floor_collider.node().addSolid(CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, 0))))
        self.colliders['ground-zero-collider'] = floor_collider

        self.f.pusher.addCollider(tank_collider, self.environment["player"])
        self.f.cTrav.addCollider(tank_collider, self.f.pusher)

        # show.hide all colliders
        if settings.SHOW_COLLIDERS:
            for key, value in self.colliders.items():
                logger.info(f"collider for {key} is visible")
                value.show()
                self.f.cTrav.showCollisions(self.f.render)

        # uppdate
        self.task_manager.append(self.f.task_mgr.add(self.update))
        self.task_manager.append(self.f.task_mgr.add(self.update_bullets))

    def create_model(self, from_path, reparent_to, uid, name=None,
                     position=None, scale=None, color=None, _store=True):
        if uid in self.environment and _store:
            raise KeyError(f"Value {uid} of uid already exists.")
        position = position or (0, 0, 0)
        obj = self.f.loader.loadModel(from_path)
        obj.reparent_to(reparent_to)
        name = name or uid
        obj.set_name(name)
        if scale:
            obj.set_scale(scale)
        if color:
            obj.set_color(color)
        obj.set_pos(*position)
        if _store:
            self.environment[uid] = obj
        return obj

    def redistribute_light(self, light_node):
        for key, value in self.environment.items():
            logger.info(f"seting light {light_node} for model {key}")
            value.set_light(light_node)

    def update_bullets(self, task: Task):
        dt = globalClock.getDt()
        rmi = []
        for idx, entry in enumerate(self.bullets):
            bullet, heading = entry
            bullet_pos = bullet.get_pos()

            if abs(np.sqrt(bullet_pos.y ** 2 + bullet_pos.x ** 2)) > 300:
                bullet.removeNode()
                rmi.append(idx)
                continue

            dx = (self.BULLET_SPEED * dt) * np.cos(np.radians(heading))
            dy = (self.BULLET_SPEED * dt) * np.sin(np.radians(heading))

            bullet_pos.y += dy
            bullet_pos.x += dx
            bullet.set_pos(bullet_pos)

        self.bullets = [b for i, b in enumerate(self.bullets) if i not in rmi]
        return task.cont

    # def handle_collision(self, entry):
    #     print(self.floor.get_name())
    #     for k in KEY_MAP:
    #         KEY_MAP[k] = False
    #     print(entry)
    #
    def update(self, task: Task):
        if self.f.state == settings.IN_MENU_STATE:
            return task.cont

        dt, ft = globalClock.getDt(), globalClock.getFrameTime()
        tank_heading, tank_position = self.tank.tank.get_h(), self.tank.tank.get_pos()

    #     # self.sun.set_p(self.sun.get_p() - (dt * 40))
    #     # self.sun.set_h(self.sun.get_h() - (dt * 20))

        self.tank.hit()
        self.tank.tank.set_pos(tank_position.x, tank_position.y, tank_position.z)
        self.tank.handle_sfx()

        if KEY_MAP["up"]:
            tank_position.z += self.SPEED * dt
            self._tank.set_pos(tank_position)

        if KEY_MAP["down"]:
            tank_position.z -= self.SPEED * dt
            self._tank.set_pos(tank_position)

        if KEY_MAP["q"]:
            tank_position.x -= self.SPEED * dt
            self._tank.set_pos(tank_position)

        if KEY_MAP["e"]:
            tank_position.x += self.SPEED * dt
            self._tank.set_pos(tank_position)

        if KEY_MAP["w"]:
            dx = (self.SPEED * dt) * np.cos(np.radians(tank_heading + 90))
            dy = (self.SPEED * dt) * np.sin(np.radians(tank_heading + 90))
            tank_position.y, tank_position.x = tank_position.y + dy, tank_position.x + dx
            self._tank.set_pos(tank_position)

        if KEY_MAP["s"]:
            dx = - (self.SPEED * dt) * np.cos(np.radians(tank_heading + 90))
            dy = - (self.SPEED * dt) * np.sin(np.radians(tank_heading + 90))
            tank_position.y, tank_position.x = tank_position.y + dy, tank_position.x + dx
            self._tank.set_pos(tank_position)

        if KEY_MAP["d"] and not KEY_MAP["s"]:
            tank_heading -= self.TURN_SPEED * dt * 2
            self._tank.set_h(tank_heading)

        if KEY_MAP["a"] and not KEY_MAP["s"]:
            tank_heading += self.TURN_SPEED * dt * 2
            self._tank.set_h(tank_heading)

        if KEY_MAP["d"] and KEY_MAP["s"]:
            tank_heading += self.TURN_SPEED * dt * 2
            self._tank.set_h(tank_heading)

        if KEY_MAP["a"] and KEY_MAP["s"]:
            tank_heading -= self.TURN_SPEED * dt * 2
            self._tank.set_h(tank_heading)

        return task.cont

    def stop(self):
        pass

    def __del__(self):
        logger.info("game session destroyed")


class Controller(object):
    def __init__(self, accept, content: BattleTank):
        self.content: BattleTank = content

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

        accept("space", self.fire_bullet)

    def fire_bullet(self):
        self.content.tank.tank_fire_sound.stop()
        self.content.tank.tank_fire_sound.play()

        position = self.content.tank.gun.get_pos(self.content.f.render)
        heading = self.content.tank.tank.get_h() + 90

        bullet = self.content.f.loader.loadModel("models/misc/sphere")
        bullet.set_pos(position)
        bullet.set_scale(0.3)
        bullet.set_color((0, 0, 0, 1))
        bullet.reparent_to(self.content.f.render)
        self.content.bullets.append([bullet, heading])
