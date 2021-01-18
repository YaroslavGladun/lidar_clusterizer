import pygame
import src.controller as C
import src.geometry as gm
import numpy as np
import src.graphics_core as gc
from src.colfig import get_config
from src.utils import color_str_to_list
from abc import ABC, abstractmethod
from src.menu import ClusteringMethod
from sklearn.cluster import KMeans, DBSCAN, OPTICS
from sklearn.mixture import GaussianMixture

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
            gc.draw_segment(controller.surface, COLORS['color3'], self.segment, width=3)
        elif self.is_holding:
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
            gc.draw_segment(controller.surface, COLORS['color1'], segment, width=3)


class LidarSimulator(PluginBase):

    def __init__(self, rays_num=72, std=3):
        self.std = std
        self.rays_num = rays_num
        self.iter_seg = gm.Segment(gm.Point(0, 0), gm.Point(0, 0))

    @ProcessReduce(30)
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

    def __init__(self, radius=3):
        self.radius = radius

    def process(self, controller: C.Controller):
        for point in controller.lidar_points:
            gc.draw_point(controller.surface, COLORS['color2'], point, radius=self.radius)


class Menu(PluginBase):

    def __init__(self, x, y, w, h, menu_state):
        self.h = h
        self.w = w
        self.y = y
        self.x = x
        self.menu_state = menu_state
        self.none_button = gc.Button(x + 10, y + 10, x + w - 20, 20, "None",
                                     on_click=lambda: self.menu_state.set_clustering_method(ClusteringMethod.NONE))
        self.k_means_button = gc.Button(x + 10, y + 40, x + w - 20, 20, "K-Means",
                                        on_click=lambda: self.menu_state.set_clustering_method(
                                            ClusteringMethod.K_MEANS))
        self.dbscan_button = gc.Button(x + 10, y + 70, x + w - 20, 20, "DBSCAN",
                                       on_click=lambda: self.menu_state.set_clustering_method(ClusteringMethod.DBSCAN))

        self.optics_button = gc.Button(x + 10, y + 100, x + w - 20, 20, "OPTICS",
                                       on_click=lambda: self.menu_state.set_clustering_method(ClusteringMethod.OPTICS))

        self.gaussian_mixture_button = gc.Button(x + 10, y + 130, x + w - 20, 20, "Gaussian mixture",
                                                 on_click=lambda: self.menu_state.set_clustering_method(
                                                     ClusteringMethod.GAUSSIAN_MIXTURE))

    def process(self, controller: C.Controller):

        self.none_button.disable()
        self.dbscan_button.disable()
        self.k_means_button.disable()
        self.optics_button.disable()
        self.gaussian_mixture_button.disable()
        if controller.menu_state.clustering_method == ClusteringMethod.NONE:
            self.none_button.enable()
        elif controller.menu_state.clustering_method == ClusteringMethod.K_MEANS:
            self.k_means_button.enable()
        elif controller.menu_state.clustering_method == ClusteringMethod.DBSCAN:
            self.dbscan_button.enable()
        elif controller.menu_state.clustering_method == ClusteringMethod.OPTICS:
            self.optics_button.enable()
        elif controller.menu_state.clustering_method == ClusteringMethod.GAUSSIAN_MIXTURE:
            self.gaussian_mixture_button.enable()

        pygame.draw.rect(controller.surface, COLORS['color5'],
                         pygame.Rect((self.x, self.y), (self.x + self.w, self.y + self.h)))
        self.none_button.process(controller.surface)
        self.k_means_button.process(controller.surface)
        self.dbscan_button.process(controller.surface)
        self.optics_button.process(controller.surface)
        self.gaussian_mixture_button.process(controller.surface)


class Clusterizer(PluginBase):

    def __init__(self):
        self.k_means = KMeans(n_clusters=6)
        self.dbscan = DBSCAN(eps=50)
        self.optics = OPTICS()
        self.gaussian_mixture = GaussianMixture(n_components=6)
        self.colors = [
            [255, 0, 0],
            [0, 255, 0],
            [0, 0, 255],
            [255, 255, 0],
            [255, 0, 255],
            [0, 255, 255]
        ]
        self.labels = []

    @ProcessReduce(30)
    def clusterize(self, controller: C.Controller):
        if not len(controller.lidar_points):
            return
        X = np.array(list(map(lambda x: x.values, controller.lidar_points)))
        if controller.menu_state.clustering_method == ClusteringMethod.K_MEANS:
            labels = self.k_means.fit(X).labels_
            label_values = []
            for t in labels:
                if t not in label_values:
                    label_values.append(t)
            labels_new = np.zeros_like(labels)
            for i, label_value in enumerate(label_values):
                labels_new[labels == label_value] = i
            self.labels = labels_new
        elif controller.menu_state.clustering_method == ClusteringMethod.DBSCAN:
            self.labels = self.dbscan.fit(X).labels_
        elif controller.menu_state.clustering_method == ClusteringMethod.OPTICS:
            self.labels = self.optics.fit(X).labels_
        elif controller.menu_state.clustering_method == ClusteringMethod.GAUSSIAN_MIXTURE:
            labels = self.gaussian_mixture.fit_predict(X)
            label_values = []
            for t in labels:
                if t not in label_values:
                    label_values.append(t)
            labels_new = np.zeros_like(labels)
            for i, label_value in enumerate(label_values):
                labels_new[labels == label_value] = i
            self.labels = labels_new
        else:
            self.labels = []

    def process(self, controller: C.Controller):
        self.clusterize(controller)
        if not len(controller.lidar_points):
            return
        for i in range(len(self.labels)):
            gc.draw_point(controller.surface, self.colors[self.labels[i] % len(self.colors)],
                          controller.lidar_points[i])
