import pygame
from src.geometry import Point, Segment


def draw_point(screen, color, point: Point, radius=4, *args, **kwargs):
    pygame.draw.circle(screen, color, point.values, radius, *args, **kwargs)


def draw_segment(screen, color, segment: Segment, *args, **kwargs):
    pygame.draw.line(screen, color, segment.a.values, segment.b.values, *args, **kwargs)
