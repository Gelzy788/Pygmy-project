import pygame
import os
import sys
import random


pygame.init()
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
done = False
is_blue = True
x = 30
y = 30
blood_points = 0
menu_active = False  # Добавляем флаг для отслеживания состояния меню

# Добавляем шрифт для отображения очков и меню
font = pygame.font.Font(None, 36)

# Создаем поверхность для меню с прозрачностью
MENU_WIDTH = 300
MENU_HEIGHT = 200
menu_surface = pygame.Surface((MENU_WIDTH, MENU_HEIGHT))
menu_surface.set_alpha(200)  # Устанавливаем прозрачность (0-255)
menu_rect = pygame.Rect(WIDTH//2 - MENU_WIDTH//2, HEIGHT //
                        2 - MENU_HEIGHT//2, MENU_WIDTH, MENU_HEIGHT)

exit_button = pygame.Rect(MENU_WIDTH//2 - 60, MENU_HEIGHT//2 - 25, 120, 50)

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
            self.rect.y -= 3
        if pressed[pygame.K_DOWN] and self.rect.y < HEIGHT - self.rect.height:
            self.rect.y += 3
        if pressed[pygame.K_LEFT] and self.rect.x > 0:
            self.rect.x -= 3
        if pressed[pygame.K_RIGHT] and self.rect.x < WIDTH - self.rect.width:
            self.rect.x += 3

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
                menu_active = not menu_active  # Переключаем состояние меню
            if event.key == pygame.K_SPACE:
                is_blue = not is_blue

        # Обработка кликов мыши в меню
        if event.type == pygame.MOUSEBUTTONDOWN and menu_active:
            mouse_pos = event.pos
            if exit_button.collidepoint(mouse_pos):
                done = True

    screen.fill((0, 0, 0))

    if not menu_active:
        # Обычный игровой процесс
        all_sprites.draw(screen)
        all_sprites.update()

        # Отображение очков в правом верхнем углу
        score_text = font.render(f'Blood: {blood_points}', True, (255, 0, 0))
        score_rect = score_text.get_rect()
        score_rect.topright = (790, 10)
        screen.blit(score_text, score_rect)
    else:
        # Отрисовка меню
        menu_surface.fill((50, 50, 50))  # Заполняем цветом фон меню

        # Отрисовка кнопки выхода на поверхности меню
        pygame.draw.rect(menu_surface, (128, 128, 128), exit_button)
        exit_text = font.render('Exit', True, (255, 255, 255))
        exit_text_rect = exit_text.get_rect(
            center=(MENU_WIDTH//2, MENU_HEIGHT//2))
        menu_surface.blit(exit_text, exit_text_rect)

        # Отображаем меню на экране
        screen.blit(menu_surface, (WIDTH//2 - MENU_WIDTH //
                    2, HEIGHT//2 - MENU_HEIGHT//2))

        # Обновляем позицию кнопки для проверки кликов
        exit_button_screen = pygame.Rect(
            WIDTH//2 - 60,  # Центрируем относительно экрана
            HEIGHT//2 - 25,
            120, 50
        )

        # Обновляем проверку клика по кнопке
        if event.type == pygame.MOUSEBUTTONDOWN and menu_active:
            mouse_pos = event.pos
            if exit_button_screen.collidepoint(mouse_pos):
                done = True

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
