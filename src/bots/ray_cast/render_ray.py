import pygame as pg
import math
from random import randint

from ray_cast.boundary import Boundary
from ray_cast.particle import Particle
from ray_cast.ray import Ray


def setup():
    ### CONFIG
    screen_w = 800
    screen_h = 800
    border_on = True
    num_walls = 1
    num_rays = 45
    viewing_angle = 135
    ### END CONFIG

    pg.init()
    screen = pg.display.set_mode((screen_w, screen_h))

    return screen, border_on, num_walls, num_rays, screen_w, screen_h, viewing_angle


def render_ray(setup, particles: dict[str, Particle], rays: dict[str, list[Ray]], boundaries, paths):
    screen, border_on, num_walls, num_rays, screen_w, screen_h, viewing_angle = setup

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
    directions = {key: 1 for key in paths.keys()}  # Добавляем флаг направления (1 - вперед, -1 - назад)

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        screen.fill((0, 0, 0))

        # Обновляем объекты по их путям
        for key, particle in particles.items():
            index = indices[key]
            speed = particle.speed
            direction = directions[key]  # Получаем текущий флаг направления

            # Перемещаем индекс в зависимости от направления
            index += direction * speed

            # Зацикливаем индекс по пути (если бот достиг конца пути)
            if index >= len(paths[key]):  # Достигнут конец пути
                index = len(paths[key]) - 1
                directions[key] = -1  # Меняем направление на обратное
            elif index < 0:  # Достигнут начало пути
                index = 0
                directions[key] = 1  # Меняем направление на прямое

            # Получаем координаты текущей точки пути
            x, y = paths[key][int(index)]

            x0, y0 = particle.pos
            # Вычисляем угол, на который нужно повернуться
            angle_rotation = -math.degrees(math.atan2(y - y0, x - x0)) - viewing_angle / 2

            # Вычисляем минимальную разницу углов
            delta_angle = (angle_rotation - particle.current_angle + 180) % 360 - 180

            # Увеличиваем скорость поворота для резких углов
            smooth_speed = 0.1  # Базовая скорость
            angle_difference = abs(delta_angle)

            # Увеличиваем скорость плавного изменения для резких поворотов
            if angle_difference > 60:  # Если угол больше 60 градусов, увеличиваем скорость
                smooth_speed *= 3
            elif angle_difference > 30:  # Если угол больше 30 градусов, увеличиваем скорость
                smooth_speed *= 2

            # Применяем плавное изменение угла
            particle.current_angle += delta_angle * smooth_speed

            # Обновляем позицию частицы
            particle.update(screen, x, y)

            # Обновляем лучи для этой частицы
            for ray in rays[key]:
                ray.update(screen, particle, boundaries, particle.current_angle)

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