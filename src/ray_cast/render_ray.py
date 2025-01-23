import pygame as pg
from random import randint

from boundary import Boundary
from particle import Particle
from ray import Ray


def setup():
    ### CONFIG
    screen_w = 1000
    screen_h = 1000
    border_on = True
    num_walls = 6
    num_rays = 45
    ### END CONFIG

    pg.init()
    screen = pg.display.set_mode((screen_w, screen_h))

    return screen, border_on, num_walls, num_rays, screen_w, screen_h


def render_ray(setup, particles, rays, boundaries, paths):
    screen, border_on, num_walls, num_rays, screen_w, screen_h = setup

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

    # Индексы для каждого объекта в словаре
    indices = {key: 0 for key in paths.keys()}

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        screen.fill((0, 0, 0))

        # Обновляем объекты по их путям
        for key, particle in particles.items():
            index = indices[key]
            speed = particle.speed

            # Перемещаем индекс на несколько шагов, пропуская точки в зависимости от скорости
            index += speed

            # Зацикливаем индекс, если он выходит за пределы пути
            index = index % len(paths[key])

            # Получаем координаты текущей точки пути
            x, y = paths[key][int(index)]

            # Обновляем позицию частицы
            particle.update(screen, x, y)

            # Обновляем лучи для этой частицы
            for ray in rays[key]:
                ray.update(screen, particle, boundaries)

            # Обновляем индекс для следующего шага
            indices[key] = index

        # Обновляем границы
        for b in boundaries:
            b.update(screen)

        pg.display.update()
        pg.time.wait(75)


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