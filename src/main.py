import pygame
import os
import sys
import random


pygame.init()
WIDTH = 800
HEIGHT = 600
PROTECTION = 50
screen = pygame.display.set_mode((WIDTH, HEIGHT))
done = False
hp = 100
protection_chance = 0
speed = 3
stealth = [8, 10]  # Изменил на список для возможности модификации
damage = 50
blood_points = 0
improve_menu_active = False  # Добавляем флаг для отслеживания состояния меню

# Добавляем шрифт для отображения очков и меню
font = pygame.font.Font(None, 36)

# Создаем поверхность для меню с прозрачностью
MENU_WIDTH = 400
MENU_HEIGHT = 300
menu_surface = pygame.Surface((MENU_WIDTH, MENU_HEIGHT))
menu_surface.set_alpha(200)  # Устанавливаем прозрачность (0-255)
menu_rect = pygame.Rect(WIDTH//2 - MENU_WIDTH//2, HEIGHT //
                        2 - MENU_HEIGHT//2, MENU_WIDTH, MENU_HEIGHT)

# Создаем кнопки для прокачки
button_width = 300
button_height = 40
button_margin = 10

speed_button = pygame.Rect(
    MENU_WIDTH//2 - button_width//2, 50, button_width, button_height)
hp_button = pygame.Rect(MENU_WIDTH//2 - button_width//2,
                        100, button_width, button_height)
stealth_button = pygame.Rect(
    MENU_WIDTH//2 - button_width//2, 150, button_width, button_height)
exit_button = pygame.Rect(MENU_WIDTH//2 - button_width //
                          2, 200, button_width, button_height)

clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
items = pygame.sprite.Group()  # Группа для предметов


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class Player(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.image = load_image('ball.png')
        self.rect = self.image.get_rect()
        self.rect.x = 5
        self.rect.y = 20

    def update(self):
        global blood_points  # Добавляем глобальную переменную
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_UP] and self.rect.y > 0:
            self.rect.y -= speed
        if pressed[pygame.K_DOWN] and self.rect.y < HEIGHT - self.rect.height:
            self.rect.y += speed
        if pressed[pygame.K_LEFT] and self.rect.x > 0:
            self.rect.x -= speed
        if pressed[pygame.K_RIGHT] and self.rect.x < WIDTH - self.rect.width:
            self.rect.x += speed

        # Проверка столкновений с предметами
        collected_items = pygame.sprite.spritecollide(self, items, True)
        if collected_items:
            blood_points += len(collected_items)
            print(f"Очки крови: {blood_points}")


class Item(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 0, 0))  # Заполняем красным цветом
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(0, HEIGHT - self.rect.height)


# Создаем игрока
player = Player()
all_sprites.add(player)

# Создаем несколько предметов в случайных местах
for _ in range(10):  # Создаем 10 предметов
    item = Item()
    items.add(item)
    all_sprites.add(item)


while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_y:
                improve_menu_active = not improve_menu_active  # Переключаем состояние меню
            if event.key == pygame.K_SPACE:
                is_blue = not is_blue

        # Обработка кликов в меню прокачки
        if event.type == pygame.MOUSEBUTTONDOWN and improve_menu_active:
            mouse_pos = pygame.mouse.get_pos()
            # Преобразуем координаты мыши относительно меню
            menu_mouse_pos = (mouse_pos[0] - (WIDTH//2 - MENU_WIDTH//2),
                              mouse_pos[1] - (HEIGHT//2 - MENU_HEIGHT//2))

            if blood_points > 0:  # Проверяем, есть ли очки крови
                if speed_button.collidepoint(menu_mouse_pos):
                    speed += 3
                    blood_points -= 1
                elif hp_button.collidepoint(menu_mouse_pos):
                    hp += 20
                    blood_points -= 1
                elif stealth_button.collidepoint(menu_mouse_pos):
                    if stealth[0] > 5:
                        stealth[0] = stealth[0] - 1
                        stealth[1] = stealth[1] - 1
                        blood_points -= 1

            if exit_button.collidepoint(menu_mouse_pos):
                improve_menu_active = False

    screen.fill((0, 0, 0))

    if not improve_menu_active:
        # Обычный игровой процесс
        all_sprites.draw(screen)
        all_sprites.update()

        # Отображение характеристик
        stats_text = [
            f'Blood: {blood_points}',
            f'Speed: {speed}',
            f'HP: {hp}',
            f'Stealth: {stealth}'
        ]

        for i, text in enumerate(stats_text):
            text_surface = font.render(text, True, (255, 0, 0))
            screen.blit(text_surface, (10, 10 + i * 30))

    else:
        # Отрисовка меню прокачки
        menu_surface.fill((50, 50, 50))

        title_text = font.render('Меню прокачки', True, (255, 255, 255))
        title_rect = title_text.get_rect(centerx=MENU_WIDTH//2, y=10)
        menu_surface.blit(title_text, title_rect)

        # Кнопки прокачки
        buttons = [
            (speed_button, f'Скорость +3 ({blood_points} кровь)'),
            (hp_button, f'HP +20 ({blood_points} кровь)'),
            (stealth_button, f'Скрытность -1 ({blood_points} кровь)'),
            (exit_button, 'Закрыть')
        ]

        for button, text in buttons:
            pygame.draw.rect(menu_surface, (128, 128, 128), button)
            button_text = font.render(text, True, (255, 255, 255))
            text_rect = button_text.get_rect(center=button.center)
            menu_surface.blit(button_text, text_rect)

        # Отображаем меню на экране
        screen.blit(menu_surface, (WIDTH//2 - MENU_WIDTH //
                    2, HEIGHT//2 - MENU_HEIGHT//2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
