import pygame
from src.geometry import Segment, Point
from src.graphics_core import draw_segment, draw_point
import src.simulation as sim

pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

size = (1280, 720)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("lidar clusterize")

done = False
clock = pygame.time.Clock()

world = sim.World(sim.Room(), sim.Robot(500, 250), screen)
simulator = sim.Simulator(world, (
    sim.RobotDrawer(),
    sim.RobotMover(),
    sim.MapBuilder(),
    sim.MapDrawer()
))

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    screen.fill(WHITE)

    simulator.process()

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
