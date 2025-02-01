import pygame as pg
import math
from random import randint

from ray_cast.boundary import Boundary
from ray_cast.particle import Particle
from ray_cast.ray import Ray
from bot import Bot


def setup():
    ### CONFIG
    screen_w = 800
    screen_h = 800
    border_on = True
    num_walls = 3
    num_rays = 45
    viewing_angle = 135
    ### END CONFIG

    pg.init()
    screen = pg.display.set_mode((screen_w, screen_h))

    return screen, border_on, num_walls, num_rays, screen_w, screen_h, viewing_angle


# render_ray(set_up, bots, particles, rays, boundaries)
# particles: dict[str, Particle],
def render_ray(setup, bots: dict[str, Bot], rays: dict[str, list[Ray]], boundaries: list[Boundary], all_sprites: pg.sprite.Group):
    screen, border_on, num_walls, num_rays, screen_w, screen_h, viewing_angle = setup

    clock = pg.time.Clock()
    running = True
    pg.event.set_allowed([pg.QUIT, pg.KEYDOWN, pg.KEYUP])

    # Если границы включены, добавляем их
    if border_on:
        boundaries.append(Boundary(screen, (0, 0), (screen_w, 0), pg.Color('black')))
        boundaries.append(Boundary(screen, (screen_w, 0), (screen_w, screen_h)))
        boundaries.append(Boundary(screen, (screen_w, screen_h), (0, screen_h)))
        boundaries.append(Boundary(screen, (0, screen_h), (0, 0), pg.Color('black')))
    
    for i in range(num_walls):
        boundaries.append(Boundary(screen,
                                    (randint(0, screen_w), randint(0, screen_h)),
                                    (randint(0, screen_w), randint(0, screen_h))))
    k = 0
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        screen.fill((0, 0, 0))

        for key, bot in bots.items():
            bot.update(screen, viewing_angle, rays[key], boundaries)

        # Обновляем границы
        for b in boundaries:
            b.update(screen)

        all_sprites.draw(screen)
        k += 1
        print(k)
        pg.display.flip()
        clock.tick(60)
        pg.display.update()
        # pg.time.wait(25)


if __name__ == "__main__":
    # Инициализация
    set_up = setup()

    # Создание объектов (частицы, лучи, границы)
    particles = [Particle(), Particle()]  # Добавляем несколько частиц
    rays = [Ray(particles[0], i * -135 / 45 - 45) for i in range(45)]  # Создаем лучи для каждой частицы
    boundaries = []

    # Координаты, на которые нужно переместить объекты
    coords = [
        (100, 300), (200, 100), (300, 500), (400, 600),
        (500, 700), (600, 800), (700, 900), (800, 100),
    ]

    # Запуск игры
    render_ray(set_up, particles, rays, boundaries, coords)