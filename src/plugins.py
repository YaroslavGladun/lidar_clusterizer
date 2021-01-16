import pygame
import src.controller as W
import src.geometry as gm
import numpy as np
from src.graphics_core import draw_segment, draw_point
from src.colfig import get_config
from src.utils import color_str_to_list
from abc import ABC, abstractmethod

COLORS = get_config('../config/colors.yaml')
for key in COLORS:
    COLORS[key] = color_str_to_list(COLORS[key])


class Observer(ABC):

    @abstractmethod
    def update(self, subject) -> None:
        raise NotImplemented


class Subject(ABC):

    @abstractmethod
    def attach(self, observer: Observer) -> None:
        raise NotImplemented

    @abstractmethod
    def detach(self, observer: Observer) -> None:
        raise NotImplemented

    @abstractmethod
    def notify(self) -> None:
        raise NotImplemented


class PluginBase:

    def process(self, world: W.Controller):
        raise NotImplemented


class RobotDrawer(PluginBase):

    def __init__(self):
        self.image = pygame.image.load(r'../images/robot.png')

    def process(self, world: W.Controller):
        rect = self.image.get_rect()
        rect.center = world.robot.position.values.tolist()
        res = world.surface.blit(self.image, rect)


class RobotMover(PluginBase):

    def __init__(self, activate_radius=50):
        self.activate_radius = activate_radius
        self.last_mouse_position = gm.Point(*pygame.mouse.get_pos())
        self.is_holding = False

    def process(self, world: W.Controller):
        if world.action not in [W.Action.NONE, W.Action.MOVE_ROBOT]:
            return
        this_mouse_position = gm.Point(*pygame.mouse.get_pos())
        is_inside = this_mouse_position.distance_to(world.robot.position) < self.activate_radius
        if pygame.mouse.get_pressed(3)[0] and (is_inside or self.is_holding):
            world.action = W.Action.MOVE_ROBOT
            delta = this_mouse_position - self.last_mouse_position
            world.robot.position.x += delta.x
            world.robot.position.y += delta.y
            del delta
            self.is_holding = True
        else:
            world.action = W.Action.NONE
            self.is_holding = False
        del self.last_mouse_position
        self.last_mouse_position = this_mouse_position


class MapBuilder(PluginBase):

    def __init__(self):
        self.is_holding = False
        self.segment = gm.Segment(gm.Point(0, 0), gm.Point(0, 0))

    def process(self, world: W.Controller):
        if world.action not in [W.Action.NONE, W.Action.BUILD_MAP]:
            return
        if not self.is_holding and pygame.mouse.get_pressed(3)[0]:
            world.action = W.Action.BUILD_MAP
            self.is_holding = True
            mouse_pos = pygame.mouse.get_pos()
            self.segment.a.x = self.segment.b.x = mouse_pos[0]
            self.segment.a.y = self.segment.b.y = mouse_pos[1]
        elif self.is_holding and pygame.mouse.get_pressed(3)[0]:
            world.action = W.Action.BUILD_MAP
            mouse_pos = pygame.mouse.get_pos()
            self.segment.b.x = mouse_pos[0]
            self.segment.b.y = mouse_pos[1]
            draw_segment(world.surface, COLORS['color3'], self.segment, width=3)
        else:
            world.action = W.Action.NONE
            world.room.append_segment(self.segment.copy())
            self.segment.a.x = self.segment.b.x = 0
            self.segment.a.y = self.segment.b.y = 0
            self.is_holding = False


class MapDrawer(PluginBase):

    def __init__(self):
        pass

    def process(self, world: W.Controller):
        for segment in world.room.polygon.segments:
            draw_segment(world.surface, COLORS['color2'], segment, width=3)


class LidarSimulator(PluginBase):

    def __init__(self):
        self.iter_seg = gm.Segment(gm.Point(0, 0), gm.Point(0, 0))

    def process(self, world: W.Controller):
        self.iter_seg.a = world.robot.position
        for alpha in np.linspace(0, 2 * np.pi, 18 + 1)[:-1]:
            self.iter_seg.b.x = self.iter_seg.a.x + np.cos(alpha)
            self.iter_seg.b.y = self.iter_seg.a.y + np.sin(alpha)
            ray = gm.Ray(self.iter_seg)
            intersect = ray.intersect_with_polygon(world.room.polygon)
            if intersect is not None:
                draw_point(world.surface, COLORS['color1'], intersect)
                del intersect
            del ray
