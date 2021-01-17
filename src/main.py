import pygame
import src.controller as W
import src.plugins as P
pygame.font.init()

pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

size = (1280, 720)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Lidar clusterize")

clock = pygame.time.Clock()

world = W.Controller(W.Room(), W.Robot(500, 250), screen)
processor = W.Processor(world, (
    P.RobotDrawer(),
    P.RobotMover(),
    P.MapBuilder(),
    P.MapDrawer(),
    P.LidarSimulator(rays_num=72, std=3),
    P.LidarDataDrawer(radius=3),
    P.Menu(x=10, y=10, w=100, h=200, menu_state=world.menu_state),
    P.Clusterizer()
))

done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
    screen.fill(WHITE)
    processor.process()
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
