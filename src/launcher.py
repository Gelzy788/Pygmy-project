import pygame
import sys
import subprocess
import os
import sqlite3
from boss_fight.game import scripted_boss_fight
from database import Database

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Boss Fight Launcher")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

# Шрифты
font = pygame.font.Font(None, 74)
button_font = pygame.font.Font(None, 50)
save_font = pygame.font.Font(None, 36)

# База данных
db = Database()


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)


def draw_input_box(screen, text, input_rect):
    pygame.draw.rect(screen, BLACK, input_rect, 2)
    text_surface = save_font.render(text, True, BLACK)
    screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))


def start_level(user_id, level):
    if level == 5:  # Босс файт
        # Получаем путь к скрипту босса из базы данных
        conn = sqlite3.connect('data/levels.sqlite')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT script_paths FROM info_levels WHERE num_lvl = ?
        ''', (level,))
        result = cursor.fetchone()
        conn.close()

        if result:
            script_path = result[0]
            while True:
                fight_result = scripted_boss_fight(script_path)
                if fight_result == "restart":
                    continue  # Перезапускаем босс-файт
                elif fight_result == "quit":
                    return "quit"
                else:
                    return fight_result
        else:
            print(f"Ошибка: не найден скрипт для уровня {level}")
            return "quit"
    else:
        start_round_path = os.path.join(
            os.path.dirname(__file__), 'bots', 'start_round.py')

        pygame.display.quit()
        pygame.quit()

        try:
            subprocess.run(
                [sys.executable, start_round_path, str(level), str(user_id)], check=True)
            sys.exit()
        except subprocess.CalledProcessError:
            sys.exit()


def saves_menu():
    input_active = False
    current_save_slot = None
    input_text = ""
    input_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2, 200, 32)

    while True:
        screen.fill(WHITE)
        draw_text('Сохранения', font, BLACK, screen, WIDTH//2, 50)

        saves = db.get_all_saves()
        saves_dict = {}
        for index, save in enumerate(saves):
            saves_dict[index + 1] = (save[0], save[1])

        save_slots = []
        delete_buttons = []  # Список кнопок удаления
        for i in range(5):
            slot_rect = pygame.Rect(WIDTH//2 - 150, 150 + i*80, 300, 60)
            save_slots.append(slot_rect)
            # Кнопка удаления справа от слота
            delete_button = pygame.Rect(WIDTH//2 + 160, 165 + i*80, 30, 30)
            delete_buttons.append(delete_button)

        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # ЛКМ
                    # Проверяем клики по кнопкам удаления
                    for i, delete_button in enumerate(delete_buttons):
                        if delete_button.collidepoint(mx, my):
                            slot_number = i + 1
                            if slot_number in saves_dict:
                                user_id = saves_dict[slot_number][0]
                                if db.delete_save(user_id):
                                    print(f"Сохранение {slot_number} удалено")
                                continue

                    # Проверяем клики по слотам
                    for i, slot in enumerate(save_slots):
                        if slot.collidepoint(mx, my):
                            slot_number = i + 1
                            if slot_number not in saves_dict:
                                input_active = True
                                current_save_slot = slot_number
                            else:
                                user_id = saves_dict[slot_number][0]
                                current_level = db.get_current_level(user_id)
                                result = start_level(user_id, current_level)
                                if result == "menu":
                                    return
                                elif result == "quit":
                                    pygame.quit()
                                    sys.exit()

            if event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_RETURN:
                        if input_text.strip():
                            db.create_save(input_text)
                            input_active = False
                            input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        if len(input_text) < 20:  # Ограничение длины ника
                            input_text += event.unicode
                if event.key == pygame.K_ESCAPE:
                    return

        # Отрисовка слотов и кнопок удаления
        for i in range(5):
            slot_rect = save_slots[i]
            delete_button = delete_buttons[i]

            pygame.draw.rect(screen, GRAY, slot_rect)
            if i + 1 in saves_dict:
                # Отрисовка информации о сохранении
                nickname = saves_dict[i + 1][1]
                draw_text(f'Слот {i + 1}: {nickname}', save_font,
                          BLACK, screen, slot_rect.centerx, slot_rect.centery)

                # Отрисовка кнопки удаления
                pygame.draw.rect(screen, RED, delete_button)
                draw_text('X', save_font, WHITE, screen,
                          delete_button.centerx, delete_button.centery)
            else:
                draw_text(f'Слот {i + 1}: Пусто', save_font, BLACK,
                          screen, slot_rect.centerx, slot_rect.centery)

        # Отрисовка поля ввода
        if input_active:
            draw_input_box(screen, input_text, input_rect)

        pygame.display.flip()


def main_menu():
    while True:
        screen.fill(WHITE)
        draw_text('Vampire Game', font, BLACK, screen, WIDTH//2, HEIGHT//4)

        mx, my = pygame.mouse.get_pos()

        play_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50)
        settings_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)

        if play_button.collidepoint((mx, my)):
            if pygame.mouse.get_pressed()[0]:
                saves_menu()

        if settings_button.collidepoint((mx, my)):
            if pygame.mouse.get_pressed()[0]:
                settings_menu()

        pygame.draw.rect(screen, GRAY, play_button)
        pygame.draw.rect(screen, GRAY, settings_button)

        draw_text('Играть', button_font, BLACK,
                  screen, WIDTH//2, HEIGHT//2 - 25)
        draw_text('Настройки', button_font, BLACK,
                  screen, WIDTH//2, HEIGHT//2 + 75)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()


def settings_menu():
    running = True
    while running:
        screen.fill(WHITE)
        draw_text('Настройки', font, BLACK, screen, WIDTH//2, HEIGHT//4)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        pygame.display.flip()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'boss':
        # Прямой запуск босс-файта
        user_id = int(sys.argv[2])

        # Получаем путь к скрипту босса из базы данных
        conn = sqlite3.connect('data/levels.sqlite')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT script_paths FROM info_levels WHERE num_lvl = ?
        ''', (5,))  # 5 - уровень босса
        result = cursor.fetchone()
        conn.close()

        if result:
            script_path = result[0]  # Получаем путь к скрипту
            scripted_boss_fight(script_path)
        else:
            print(f"Ошибка: не найден скрипт для уровня босса")
    else:
        # Обычный запуск лаунчера
        main_menu()
        db.close()
