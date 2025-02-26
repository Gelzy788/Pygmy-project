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
import os


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
        user_id = int(sys.argv[2])
        print(f"Запуск уровня {num_level}")
    else:
        print("Не указан номер уровня или id пользователя")
        sys.exit(1)

    pg.init()
    set_up = setup()
    screen = pg.display.get_surface()

    # Если это босс-уровень, не пытаемся загружать ботов
    if num_level == 5:
        pg.quit()
        # Получаем путь к launcher.py
        launcher_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'launcher.py'
        )
        # Запускаем босс-файт через launcher
        subprocess.run([
            sys.executable,
            launcher_path,
            'boss',  # Специальный аргумент для запуска босс-файта
            str(user_id)
        ])
        sys.exit()

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

    rays = {key: [Ray(bot.particle, i * -set_up[6] / set_up[3], user_id)
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
            # Получаем скорость из БД
            conn = sqlite3.connect('data/levels.sqlite')
            cursor = conn.cursor()
            cursor.execute('SELECT speed FROM user WHERE id = ?', (user_id,))
            player_speed = cursor.fetchone()[0]
            conn.close()

            render_result = render_round(
                set_up, bots, rays, boundaries, bot_sprites, num_level, user_id, player_speed)

            # Если получили кортеж (complete, blood_points)
            if isinstance(render_result, tuple):
                result_type, blood_points = render_result
                if result_type == "complete":
                    print(
                        f"Уровень {num_level} пройден! Собрано крови: {blood_points}")

                    # Обновляем базу данных
                    conn = sqlite3.connect('data/levels.sqlite')
                    cursor = conn.cursor()

                    # Обновляем количество крови и уровень
                    cursor.execute('''
                        UPDATE user 
                        SET blood = blood + ?, current_level = ? 
                        WHERE id = ?
                    ''', (blood_points, num_level + 1, user_id))
                    conn.commit()
                    conn.close()

                    # Показываем меню улучшений
                    show_upgrade_menu(screen, user_id)

                    # Запускаем следующий уровень
                    if num_level == 5:  # Если следующий уровень - босс
                        pg.quit()
                        # Получаем путь к launcher.py
                        launcher_path = os.path.join(
                            os.path.dirname(os.path.dirname(__file__)),
                            'launcher.py'
                        )
                        # Запускаем босс-файт через launcher
                        subprocess.run([
                            sys.executable,
                            launcher_path,
                            'boss',  # Специальный аргумент для запуска босс-файта
                            str(user_id)
                        ])
                        sys.exit()
                    else:
                        # Запускаем следующий обычный уровень
                        pg.quit()
                        subprocess.run([sys.executable, sys.argv[0],
                                        str(num_level + 1), str(user_id)])
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


def show_upgrade_menu(screen, user_id):
    """Показывает меню улучшений между уровнями"""
    running = True
    font = pg.font.Font(None, 36)

    # Подключаемся к БД
    conn = sqlite3.connect('data/levels.sqlite')
    cursor = conn.cursor()

    # Получаем текущие характеристики
    cursor.execute('''
        SELECT blood, speed, stealth 
        FROM user WHERE id = ?
    ''', (user_id,))
    stats = cursor.fetchone()
    blood, speed, stealth = stats

    # Стоимость улучшений
    costs = {
        'speed': 10,
        'stealth': 15
    }

    # Изменяем позиции кнопок и текста
    buttons = {
        # Сдвигаем кнопки вправо с 300 до 450
        'speed': pg.Rect(450, 220, 200, 50),
        'stealth': pg.Rect(450, 290, 200, 50),
        'continue': pg.Rect(450, 430, 200, 50)
    }

    names = {
        'speed': 'Скорость',
        'stealth': 'Скрытность'
    }

    while running:
        screen.fill((255, 255, 255))

        # Отображаем количество крови (оставляем слева)
        blood_text = font.render(f'Кровь: {blood}', True, (255, 0, 0))
        screen.blit(blood_text, (50, 50))

        # Отображаем текущие значения (расширяем область для текста)
        speed_text = font.render(
            f'Текущая скорость: {speed}/15', True, (0, 0, 0))
        stealth_text = font.render(
            f'Текущая скрытность: {stealth}', True, (0, 0, 0))
        # Выравниваем по вертикали с кнопками
        screen.blit(speed_text, (50, 235))
        screen.blit(stealth_text, (50, 305))

        # Отображаем кнопки улучшений
        for stat, rect in buttons.items():
            if stat != 'continue':
                can_upgrade = blood >= costs[stat]
                if stat == 'stealth' and stealth <= 30:
                    can_upgrade = False
                elif stat == 'speed' and speed >= 15:
                    can_upgrade = False

                color = (0, 255, 0) if can_upgrade else (200, 200, 200)
                pg.draw.rect(screen, color, rect)
                text = font.render(
                    f'{names[stat]} ({costs[stat]})', True, (0, 0, 0))
                # Немного сдвигаем текст на кнопке
                screen.blit(text, (rect.x + 20, rect.y + 10))
            else:
                pg.draw.rect(screen, (0, 0, 255), rect)
                text = font.render('Продолжить', True, (255, 255, 255))
                # Центрируем текст на кнопке
                screen.blit(text, (rect.x + 35, rect.y + 10))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()

                for stat, rect in buttons.items():
                    if rect.collidepoint(pos):
                        if stat == 'continue':
                            running = False
                        elif blood >= costs[stat]:
                            if stat == 'stealth' and stealth > 30:
                                # Уменьшаем скрытность на 15
                                cursor.execute('''
                                    UPDATE user 
                                    SET blood = blood - ?,
                                        stealth = stealth - ?
                                    WHERE id = ?
                                ''', (costs[stat], 15, user_id))
                                conn.commit()
                                blood -= costs[stat]
                                stealth -= 15
                            elif stat == 'speed' and speed < 15:
                                # Увеличиваем скорость на 1
                                cursor.execute('''
                                    UPDATE user 
                                    SET blood = blood - ?,
                                        speed = speed + ?
                                    WHERE id = ?
                                ''', (costs[stat], 1, user_id))
                                conn.commit()
                                blood -= costs[stat]
                                speed += 1

        pg.display.flip()

    conn.close()


if __name__ == "__main__":
    start_round()
