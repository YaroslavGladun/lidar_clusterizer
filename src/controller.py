import src.geometry as gm
from pygame import Surface
from typing import Tuple
from enum import Enum
from src.menu import MenuState


class Robot:

    def __init__(self, x, y):
        self.position = gm.Point(x, y)


class Room:

    def __init__(self):
        self.polygon = gm.Polygon([])

    def append_segment(self, segment: gm.Segment):
        self.polygon.segments.append(segment)


class Action(Enum):
    NONE = 0
    MOVE_ROBOT = 1
    BUILD_MAP = 2


class Controller:

    def __init__(self, room: Room, robot: Robot, surface: Surface):
        self.room = room
        self.robot = robot
        self.surface = surface
        self.action = Action.NONE
        self.lidar_points = []
        self.menu_state = MenuState()


class Processor:

    def __init__(self, world: Controller, plugins: Tuple):
        self.plugins = plugins
        self.world = world

    def process(self):
        for plugin in self.plugins:
            plugin.process(self.world)
