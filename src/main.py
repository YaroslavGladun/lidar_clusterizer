import pygame
import src.controller as W
import src.plugins as P

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

world = W.Controller(W.Room(), W.Robot(500, 250), screen)
simulator = W.Simulator(world, (
    P.RobotDrawer(),
    P.RobotMover(),
    P.MapBuilder(),
    P.MapDrawer(),
    # P.LidarSimulator()
))

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    screen.fill(WHITE)

    simulator.process()

    pygame.display.flip()

    clock.tick(30)

pygame.quit()
