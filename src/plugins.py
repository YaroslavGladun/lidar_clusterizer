import pygame
import src.controller as C
import src.geometry as gm
import numpy as np
from src.graphics_core import draw_segment, draw_point
from src.colfig import get_config
from src.utils import color_str_to_list
from abc import ABC, abstractmethod

COLORS = get_config('../config/colors.yaml')
for key in COLORS:
    COLORS[key] = color_str_to_list(COLORS[key])


class ProcessReduce:

    def __init__(self, n):
        self.n = n
        self.i = 0

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            if not self.i:
                func(*args, **kwargs)
            self.i = (self.i + 1) % self.n

        return wrapper


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


class PluginBase(ABC):

    @abstractmethod
    def process(self, controller: C.Controller):
        raise NotImplemented


class RobotDrawer(PluginBase):

    def __init__(self):
        self.image = pygame.image.load(r'../images/robot.png')

    def process(self, controller: C.Controller):
        rect = self.image.get_rect()
        rect.center = controller.robot.position.values.tolist()
        controller.surface.blit(self.image, rect)


class RobotMover(PluginBase):

    def __init__(self, activate_radius=50):
        self.activate_radius = activate_radius
        self.last_mouse_position = gm.Point(*pygame.mouse.get_pos())
        self.is_holding = False

    def process(self, controller: C.Controller):
        if controller.action not in [C.Action.NONE, C.Action.MOVE_ROBOT]:
            return
        this_mouse_position = gm.Point(*pygame.mouse.get_pos())
        is_inside = this_mouse_position.distance_to(controller.robot.position) < self.activate_radius
        if pygame.mouse.get_pressed(3)[0] and (is_inside or self.is_holding):
            controller.action = C.Action.MOVE_ROBOT
            delta = this_mouse_position - self.last_mouse_position
            controller.robot.position.x += delta.x
            controller.robot.position.y += delta.y
            del delta
            self.is_holding = True
        else:
            controller.action = C.Action.NONE
            self.is_holding = False
        del self.last_mouse_position
        self.last_mouse_position = this_mouse_position


class MapBuilder(PluginBase):

    def __init__(self):
        self.is_holding = False
        self.segment = gm.Segment(gm.Point(0, 0), gm.Point(0, 0))

    def process(self, controller: C.Controller):
        if controller.action not in [C.Action.NONE, C.Action.BUILD_MAP]:
            return
        if not self.is_holding and pygame.mouse.get_pressed(3)[0]:
            controller.action = C.Action.BUILD_MAP
            self.is_holding = True
            mouse_pos = pygame.mouse.get_pos()
            self.segment.a.x = self.segment.b.x = mouse_pos[0]
            self.segment.a.y = self.segment.b.y = mouse_pos[1]
        elif self.is_holding and pygame.mouse.get_pressed(3)[0]:
            controller.action = C.Action.BUILD_MAP
            mouse_pos = pygame.mouse.get_pos()
            self.segment.b.x = mouse_pos[0]
            self.segment.b.y = mouse_pos[1]
            draw_segment(controller.surface, COLORS['color3'], self.segment, width=3)
        else:
            controller.action = C.Action.NONE
            controller.room.append_segment(self.segment.copy())
            self.segment.a.x = self.segment.b.x = 0
            self.segment.a.y = self.segment.b.y = 0
            self.is_holding = False


class MapDrawer(PluginBase):

    def __init__(self):
        pass

    def process(self, controller: C.Controller):
        for segment in controller.room.polygon.segments:
            draw_segment(controller.surface, COLORS['color2'], segment, width=3)


class LidarSimulator(PluginBase):

    def __init__(self, rays_num=72, std=3):
        self.std = std
        self.rays_num = rays_num
        self.iter_seg = gm.Segment(gm.Point(0, 0), gm.Point(0, 0))

    @ProcessReduce(15)
    def process(self, controller: C.Controller):
        self.iter_seg.a = controller.robot.position
        controller.lidar_points.clear()
        for alpha in np.linspace(0, 2 * np.pi, self.rays_num + 1)[:-1]:
            self.iter_seg.b.x = self.iter_seg.a.x + np.cos(alpha)
            self.iter_seg.b.y = self.iter_seg.a.y + np.sin(alpha)
            ray = gm.Ray(self.iter_seg)
            intersect = ray.intersect_with_polygon(controller.room.polygon)
            if intersect is not None:
                controller.lidar_points.append(
                    intersect + (self.iter_seg.b - self.iter_seg.a) * np.random.normal(scale=self.std))
            del ray


class LidarDataDrawer(PluginBase):

    def __init__(self):
        pass

    def process(self, controller: C.Controller):
        for point in controller.lidar_points:
            draw_point(controller.surface, COLORS['color1'], point)
