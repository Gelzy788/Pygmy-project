import pygame as pg
import json
import sqlite3
from random import randint

from ray_cast.boundary import Boundary
from ray_cast.particle import Particle
from ray_cast.ray import Ray
from bot import Bot
from set_level.blood import Blood
from set_level.player import Player


def setup():
    # CONFIG
    screen_w = 800
    screen_h = 800
    border_on = True
    num_walls = 3
    num_rays = 45
    viewing_angle = 135
    # END CONFIG

    pg.init()
    screen = pg.display.set_mode((screen_w, screen_h))

    return screen, border_on, num_walls, num_rays, screen_w, screen_h, viewing_angle


def get_info_from_db(num_level):
    conn = sqlite3.connect('data/levels.sqlite')
    cursor = conn.cursor()

    # Запрос для получения информации по num_lvl
    result = cursor.execute('''
        SELECT script_paths, bloods, player, walls FROM info_levels WHERE num_lvl = ?
    ''', (num_level,)).fetchone()

    conn.close()

    if result:
        bloods = json.loads(result[1])
        player = json.loads(result[2])
        walls = json.loads(result[3])

        return bloods, player, walls
    else:
        # print(f'Данные для уровня {num_level} не найдены')
        return None


def render_round(setup, bots: dict[str, Bot], rays: dict[str, list[Ray]], boundaries: list[Boundary], bot_sprites: pg.sprite.Group, num_level):
    screen, border_on, num_walls, num_rays, screen_w, screen_h, viewing_angle = setup

    clock = pg.time.Clock()
    running = True
    pg.event.set_allowed([pg.QUIT, pg.KEYDOWN, pg.KEYUP])

    # Создание спрайтов для игрока
    player_sprites = pg.sprite.Group()

    info = get_info_from_db(num_level)
    if info:
        bloods, cord_player, walls = info
        player = Player(player_sprites, cord_player[0], cord_player[1])
        player.screen_width = screen_w
        player.screen_height = screen_h
    else:
        print(f'Данные для уровня {num_level} не найдены')
        return

    # Если границы включены, добавляем их
    if border_on:
        boundaries.append(
            Boundary(screen, (0, 0), (screen_w, 0), pg.Color('black')))
        boundaries.append(
            Boundary(screen, (screen_w, 0), (screen_w, screen_h)))
        boundaries.append(
            Boundary(screen, (screen_w, screen_h), (0, screen_h)))
        boundaries.append(Boundary(screen, (0, screen_h),
                          (0, 0), pg.Color('black')))

    for (x1, y1), (x2, y2) in walls:
        boundaries.append(Boundary(screen, (x1, y1), (x2, y2)))

    # Создание спрайтов для крови
    blood_sprites = pg.sprite.Group()
    for x, y in bloods:
        Blood(blood_sprites, x, y)

    k = 0
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN or event.type == pg.KEYUP:
                player.update(event)

        player.move()

        screen.fill((0, 0, 0))

        for key, bot in bots.items():
            singal = bot.update(
                screen, viewing_angle, rays[key], boundaries, (player.rect.x, player.rect.y))
            # отлавливаем сигнал о том что бот заметил игрока
            if singal:
                print('-' * 10, 'БОТ ВАС ЗАМЕТИЛ', '-' * 10)
                # pass
        # Обновляем границы
        for b in boundaries:
            b.update(screen)

        blood_sprites.draw(screen)
        bot_sprites.draw(screen)
        player_sprites.draw(screen)

        k += 1
        # print(k)
        pg.display.flip()
        clock.tick(360)
        pg.display.update()
        # надо убирать, пока что оставил, т.к. у меня из-за этого боты не дергаются
        pg.time.wait(25)


if __name__ == "__main__":
    # Инициализация
    set_up = setup()

    # Создание объектов (частицы, лучи, границы)
    particles = [Particle(), Particle()]  # Добавляем несколько частиц
    rays = [Ray(particles[0], i * -135 / 45 - 45)
            for i in range(45)]  # Создаем лучи для каждой частицы
    boundaries = []

    # Координаты, на которые нужно переместить объекты
    coords = [
        (100, 300), (200, 100), (300, 500), (400, 600),
        (500, 700), (600, 800), (700, 900), (800, 100),
    ]

    # Запуск игры
    render_round(set_up, particles, rays, boundaries, coords)
