import pygame
import src.controller as W
import src.plugins as P

pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

size = (1280, 720)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Lidar clusterize")

clock = pygame.time.Clock()

world = W.Controller(W.Room(), W.Robot(500, 250), screen)
simulator = W.Simulator(world, (
    P.RobotDrawer(),
    P.RobotMover(),
    P.MapBuilder(),
    P.MapDrawer(),
    P.LidarSimulator(rays_num=72, std=3),
    P.LidarDataDrawer()
))

done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
    screen.fill(WHITE)
    simulator.process()
    pygame.display.flip()
    clock.tick(30)
pygame.quit()
