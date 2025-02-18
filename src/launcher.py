import pygame
import sys
import subprocess
import os
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
    if level == 5:  # Предположим, что 5 уровень - это босс файт
        return scripted_boss_fight("aggressive_fight")
    else:
        # Получаем путь к start_round.py относительно launcher.py
        start_round_path = os.path.join(
            os.path.dirname(__file__), 'bots', 'start_round.py')

        # Запускаем уровень через start_round.py
        try:
            subprocess.run(
                [sys.executable, start_round_path, str(level)], check=True)
            return "continue"
        except subprocess.CalledProcessError:
            return "quit"


def saves_menu():
    input_active = False
    current_save_slot = None
    input_text = ""
    input_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2, 200, 32)

    while True:
        screen.fill(WHITE)
        draw_text('Сохранения', font, BLACK, screen, WIDTH//2, 50)

        saves = db.get_all_saves()
        # Создаем словарь с индексами слотов
        saves_dict = {}
        for index, save in enumerate(saves):
            # index -> (id, nickname)
            saves_dict[index + 1] = (save[0], save[1])

        # Создаем прямоугольники для каждого слота сохранения
        save_slots = []
        for i in range(5):
            slot_rect = pygame.Rect(WIDTH//2 - 150, 150 + i*80, 300, 60)
            save_slots.append(slot_rect)

        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # ЛКМ
                    # Проверяем клики по слотам
                    for i, slot in enumerate(save_slots):
                        if slot.collidepoint(mx, my):
                            slot_number = i + 1
                            if slot_number not in saves_dict:
                                input_active = True
                                current_save_slot = slot_number
                            else:
                                # Получаем текущий уровень пользователя
                                user_id = saves_dict[slot_number][0]
                                current_level = db.get_current_level(user_id)

                                # Запускаем соответствующий уровень
                                result = start_level(user_id, current_level)
                                if result == "quit":
                                    return

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

        # Отрисовка слотов сохранений
        for i, slot in enumerate(save_slots):
            slot_number = i + 1
            pygame.draw.rect(screen, GRAY, slot)

            if slot_number in saves_dict:
                # Отрисовка информации о сохранении
                save_id, nickname = saves_dict[slot_number]
                draw_text(nickname, save_font, BLACK,
                          screen, slot.centerx, slot.centery)

                # Кнопка удаления
                delete_rect = pygame.Rect(slot.right - 30, slot.y + 15, 20, 20)
                pygame.draw.rect(screen, RED, delete_rect)
                draw_text("×", save_font, WHITE, screen,
                          delete_rect.centerx, delete_rect.centery)
            else:
                draw_text("+", save_font, BLACK, screen,
                          slot.centerx, slot.centery)

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
    main_menu()
    db.close()
