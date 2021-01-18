import pygame

from src.colfig import get_config
from src.geometry import Point, Segment
from abc import ABC, abstractmethod

from src.utils import color_str_to_list

COLORS = get_config('../config/colors.yaml')
for key in COLORS:
    COLORS[key] = color_str_to_list(COLORS[key])


def draw_point(screen, color, point: Point, radius=3, *args, **kwargs):
    pygame.draw.circle(screen, color, point.values, radius, *args, **kwargs)


def draw_segment(screen, color, segment: Segment, *args, **kwargs):
    pygame.draw.line(screen, color, segment.a.values, segment.b.values, *args, **kwargs)


class UIComponent(ABC):

    @abstractmethod
    def process(self, surface: pygame.Surface):
        raise NotImplemented


class Button(UIComponent):

    def process(self, surface: pygame.Surface):
        mouse_pos = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed(3)[0]
        if self.x <= mouse_pos[0] <= self.x + self.w and self.y <= mouse_pos[1] <= self.y + self.h and self.last_pressed and not pressed:
            self.on_click()
        if self.x <= mouse_pos[0] <= self.x + self.w and self.y <= mouse_pos[1] <= self.y + self.h:
            color = COLORS['color1']
        else:
            color = COLORS['color4'] if self.__active else 3 * [255]
        pygame.draw.rect(surface, color, pygame.Rect((self.x, self.y), (self.w, self.h)))
        text = self.f1.render(self.test, True, 3 * [0])
        text.get_rect()
        surface.blit(text, (self.x, self.y))
        self.last_pressed = pressed

    def enable(self):
        self.__active = True

    def disable(self):
        self.__active = False

    def __init__(self, x, y, w, h, text, active=False, on_click=lambda: None):
        self.f1 = pygame.font.Font('../fonts/Dosis-Medium.ttf', 14)
        self.test = text
        self.h = h
        self.w = w
        self.y = y
        self.x = x
        self.on_click = on_click
        self.last_pressed = False
        self.__active = active
