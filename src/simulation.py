import pygame
import numpy as np
from pygame import Surface
from typing import Tuple
from src.geometry import Point, Segment
from src.graphics_core import draw_point, draw_segment


class Robot:

    def __init__(self, x, y):
        self.position = Point(x, y)


class Room:

    def __init__(self):
        self.segments = []


class World:

    def __init__(self, room: Room, robot: Robot, surface: Surface):
        self.room = room
        self.robot = robot
        self.surface = surface


class PluginBase:

    def process(self, world: World):
        raise NotImplemented


class RobotDrawer(PluginBase):

    def __init__(self):
        self.image = pygame.image.load(r'../images/robot.png')

    def process(self, world: World):
        rect = self.image.get_rect()
        rect.center = world.robot.position.values.tolist()
        world.surface.blit(self.image, rect)


class RobotMover(PluginBase):

    def __init__(self, activate_radius=20):
        self.activate_radius = activate_radius
        self.last_mouse_position = Point(*pygame.mouse.get_pos())
        self.is_holding = False

    def process(self, world: World):
        this_mouse_position = Point(*pygame.mouse.get_pos())
        is_inside = this_mouse_position.dist_to_point(world.robot.position) < self.activate_radius
        if pygame.mouse.get_pressed(3)[0] and (is_inside or self.is_holding):

            delta = this_mouse_position - self.last_mouse_position
            world.robot.position.x += delta.x
            world.robot.position.y += delta.y
            self.is_holding = True
        else:
            self.is_holding = False
        self.last_mouse_position = this_mouse_position


class MapBuilder(PluginBase):

    def __init__(self):
        self.is_holding = False
        self.segment = Segment(Point(0, 0), Point(0, 0))

    def process(self, world: World):
        if not self.is_holding and pygame.mouse.get_pressed(3)[0]:
            self.is_holding = True
            mouse_pos = pygame.mouse.get_pos()
            self.segment.a.x = self.segment.b.x = mouse_pos[0]
            self.segment.a.y = self.segment.b.y = mouse_pos[1]
        elif self.is_holding and pygame.mouse.get_pressed(3)[0]:
            mouse_pos = pygame.mouse.get_pos()
            self.segment.b.x = mouse_pos[0]
            self.segment.b.y = mouse_pos[1]
            draw_segment(world.surface, 3 * [0], self.segment)
        else:
            world.room.segments.append(self.segment.copy())
            self.segment.a.x = self.segment.b.x = 0
            self.segment.a.y = self.segment.b.y = 0
            self.is_holding = False


class MapDrawer(PluginBase):

    def __init__(self):
        pass

    def process(self, world: World):
        for segment in world.room.segments:
            draw_segment(world.surface, 3 * [0], segment)


class Simulator:

    def __init__(self, world: World, plugins: Tuple[PluginBase]):
        self.plugins = plugins
        self.world = world

    def process(self):
        for plugin in self.plugins:
            plugin.process(self.world)
