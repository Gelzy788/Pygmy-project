import pygame as pg


class Boundary:
    def __init__(self, screen: pg.display, start: tuple, end: tuple, color=pg.Color('white')):
        self.start = pg.Vector2(start)
        self.end = pg.Vector2(end)
        self.image = None
        self.color = color

    def update(self, screen: pg.display):
        self.image = pg.draw.line(screen, self.color, self.start, self.end, 2)