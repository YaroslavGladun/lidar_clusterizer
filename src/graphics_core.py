import pygame
from src.geometry import Point, Segment


def draw_point(screen, color, point: Point, radius=4):
    pygame.draw.circle(screen, color, point.values, radius)


def draw_segment(screen, color, segment: Segment):
    pygame.draw.line(screen, color, segment.a.values, segment.b.values)
