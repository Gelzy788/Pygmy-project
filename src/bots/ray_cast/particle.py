import pygame as pg
from random import randint


class Particle:
    def __init__(self, speed=1):
        info = pg.display.Info()
        self.image = None
        pg.math.Vector2()
        # self.pos = pg.Vector2(randint(0, info.current_w), randint(0, info.current_h))
        self.pos = pg.Vector2(info.current_w // 2, info.current_h // 2)  ##
        self.speed = speed  # Скорость (в точках за секунду)
        self.heading = 0
        self.vel = pg.math.Vector2((0, 0))

    def update(self, screen: pg.display, x, y):
        self.pos.x = x
        self.pos.y = y
        self.image = pg.draw.circle(screen, pg.Color('white'), (int(self.pos[0]), int(self.pos[1])), 4, 2)