import pygame as pg
import json
from render_round import setup, render_round
from ray_cast.particle import Particle
from ray_cast.ray import Ray
from bot import Bot
import sqlite3
import json
import sys
import subprocess


def draw_death_menu(screen):
    font = pg.font.Font(None, 74)
    small_font = pg.font.Font(None, 36)

    # Затемнение экрана
    dark = pg.Surface(screen.get_size()).convert_alpha()
    dark.fill((0, 0, 0, 128))
    screen.blit(dark, (0, 0))

    # Текст "GAME OVER"
    text = font.render('GAME OVER', True, (255, 0, 0))
    text_rect = text.get_rect(
        center=(screen.get_width() // 2, screen.get_height() // 2 - 50))
    screen.blit(text, text_rect)

    # Подсказки управления
    restart_text = small_font.render(
        'Нажмите R для перезапуска', True, (255, 255, 255))
    quit_text = small_font.render(
        'Нажмите Q для выхода', True, (255, 255, 255))

    restart_rect = restart_text.get_rect(
        center=(screen.get_width() // 2, screen.get_height() // 2 + 30))
    quit_rect = quit_text.get_rect(
        center=(screen.get_width() // 2, screen.get_height() // 2 + 70))

    screen.blit(restart_text, restart_rect)
    screen.blit(quit_text, quit_rect)


def get_info_from_db(num_level):
    conn = sqlite3.connect('data/levels.sqlite')
    cursor = conn.cursor()

    # Запрос для получения информации по num_lvl
    result = cursor.execute('''
        SELECT script_paths, bloods, player, walls FROM info_levels WHERE num_lvl = ?
    ''', (num_level,)).fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        return None


def start_round():
    if len(sys.argv) > 1:
        num_level = int(sys.argv[1])
        user_id = int(sys.argv[2])  # Добавляем получение user_id
        print(f"Запуск уровня {num_level}")
    else:
        print("Не указан номер уровня или id пользователя")
        sys.exit(1)

    pg.init()
    set_up = setup()
    screen = pg.display.get_surface()
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
            Particle(speed=1), 0, 1)

    rays = {key: [Ray(bot.particle, i * -set_up[6] / set_up[3])
                  for i in range(set_up[3])] for key, bot in bots.items()}
    boundaries = []

    running = True
    player_detected = False

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                return "quit"

            if player_detected:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_r:
                        return start_round()
                    elif event.key == pg.K_q:
                        pg.quit()
                        sys.exit()

        if not player_detected:
            render_result = render_round(
                set_up, bots, rays, boundaries, bot_sprites, num_level, user_id)

            # Если получили кортеж (complete, blood_points)
            if isinstance(render_result, tuple):
                result_type, blood_points = render_result
                if result_type == "complete":
                    print(
                        f"Уровень {num_level} пройден! Собрано крови: {blood_points}")

                    # Обновляем количество крови в базе данных
                    conn = sqlite3.connect('data/levels.sqlite')
                    cursor = conn.cursor()

                    # Получаем текущее количество крови
                    cursor.execute(
                        'SELECT blood FROM user WHERE id = ?', (user_id,))
                    current_blood = cursor.fetchone()[0] or 0

                    # Обновляем количество крови
                    new_blood = current_blood + blood_points
                    cursor.execute('UPDATE user SET blood = ? WHERE id = ?',
                                   (new_blood, user_id))
                    conn.commit()
                    conn.close()

                    # Запускаем следующий уровень
                    next_level = num_level + 1
                    pg.quit()
                    subprocess.run([sys.executable, sys.argv[0],
                                   str(next_level), str(user_id)])
                    sys.exit()
            elif render_result == "detected":
                player_detected = True
                continue
            elif render_result == "quit":
                return "quit"

        if player_detected:
            screen.fill((0, 0, 0))
            draw_death_menu(screen)
            pg.display.flip()

    pg.quit()
    return "quit"


if __name__ == "__main__":
    start_round()
