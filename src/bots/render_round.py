import pygame as pg
import math
import json
import sqlite3
from random import randint

from ray_cast.boundary import Boundary
from ray_cast.particle import Particle
from ray_cast.ray import Ray
from bot import Bot
from set_level.blood import Blood
from set_level.gun import Gun


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

def get_info_from_db(num_level):
    conn = sqlite3.connect('data/levels.sqlite')
    cursor = conn.cursor()

    # Запрос для получения информации по num_lvl
    result = cursor.execute('''
        SELECT paths_bots, bloods, gun, walls FROM info_levels WHERE num_lvl = ?
    ''', (num_level,)).fetchone()

    conn.close()

    if result:
        bloods = json.loads(result[1])  # Десериализация крови
        gun = json.loads(result[2])  # Десериализация координат оружия
        walls = json.loads(result[3])  # Десериализация стен

        return bloods, gun, walls
    else:
        # print(f'Данные для уровня {num_level} не найдены')
        return None

def render_round(setup, bots: dict[str, Bot], rays: dict[str, list[Ray]], boundaries: list[Boundary], bot_sprites: pg.sprite.Group, num_level):
    screen, border_on, num_walls, num_rays, screen_w, screen_h, viewing_angle = setup

    clock = pg.time.Clock()
    running = True
    pg.event.set_allowed([pg.QUIT, pg.KEYDOWN, pg.KEYUP])

    info = get_info_from_db(num_level)
    if info:
        bloods, cord_gun, walls = info
    else:
        print(f'Данные для уровня {num_level} не найдены')
        return

    # Если границы включены, добавляем их
    if border_on:
        boundaries.append(Boundary(screen, (0, 0), (screen_w, 0), pg.Color('black')))
        boundaries.append(Boundary(screen, (screen_w, 0), (screen_w, screen_h)))
        boundaries.append(Boundary(screen, (screen_w, screen_h), (0, screen_h)))
        boundaries.append(Boundary(screen, (0, screen_h), (0, 0), pg.Color('black')))
    
    for (x1, y1), (x2, y2) in walls:
        boundaries.append(Boundary(screen, (x1, y1), (x2, y2)))
    
    # Создание спрайтов для крови
    blood_sprites = pg.sprite.Group()
    for x, y in bloods:
        Blood(blood_sprites, x, y)

    # Создание спрайтов для оружия
    gun_sprites = pg.sprite.Group()
    Gun(gun_sprites, cord_gun[0], cord_gun[1])

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

        blood_sprites.draw(screen)
        gun_sprites.draw(screen)
        bot_sprites.draw(screen)

        k += 1
        # print(k)
        pg.display.flip()
        clock.tick(60)
        pg.display.update()
        pg.time.wait(25) # надо убирать, пока что оставил, т.к. у меня из-за этого боты не дергаются


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
    render_round(set_up, particles, rays, boundaries, coords)