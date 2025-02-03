import pygame as pg
import json
from render_round import setup, render_round
from ray_cast.particle import Particle
from ray_cast.ray import Ray
from bot import Bot
import sqlite3
import json

def get_info_from_db(num_level):
    conn = sqlite3.connect('data/levels.sqlite')
    cursor = conn.cursor()

    # Запрос для получения информации по num_lvl
    result = cursor.execute('''
        SELECT paths_bots, bloods, gun, walls FROM info_levels WHERE num_lvl = ?
    ''', (num_level,)).fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        return None


def start_round():
    pg.init()
    set_up = setup()
    num_level = int(input('Введите номер уровня: '))
    paths_bots = get_info_from_db(num_level)
    print(paths_bots)
    if not paths_bots:
        print(f'Данные для уровня {num_level} не найдены')
        return

    bot_sprites = pg.sprite.Group()
    bots: dict[str, Bot] = {}
    
    with open(paths_bots) as f:
        templates: dict = json.load(f)

    for i in range(len(templates)):
        bots[f'bot_{i}'] = Bot(
            bot_sprites, i, templates[f'bot_{i}']['path'], 
            Particle(speed=5), 0, 1)
    
    rays = {key: [Ray(bot.particle, i * -set_up[6] / set_up[3]) for i in range(set_up[3])] for key, bot in bots.items()}
    boundaries = []

    render_round(set_up, bots, rays, boundaries, bot_sprites, num_level)

if __name__ == "__main__":
    start_round()