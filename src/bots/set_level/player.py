import pygame
import os
import sys


def load_image(name, colorkey=None, scale=1):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)

    # Получаем текущие размеры
    size = image.get_size()
    # Вычисляем новые размеры
    new_size = (int(size[0] * scale), int(size[1] * scale))
    # Масштабируем изображение
    image = pygame.transform.scale(image, new_size)
    return image


class Player(pygame.sprite.Sprite):
    image_bot = load_image("player1.png", scale=0.3)

    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = Player.image_bot
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.add(group)

# Параметры движения
        self.moving_left = False
        self.moving_right = False
        self.moving_up = False
        self.moving_down = False
        self.is_sprinting = False
        
        self.base_speed = 6      # Постоянная скорость ходьбы
        self.sprint_speed = 10    # Скорость при спринте
        self.current_speed = self.base_speed

    def update(self, event):
        # Обработка нажатий клавиш
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.moving_left = True
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.moving_right = True
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.moving_up = True
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.moving_down = True
            if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                self.is_sprinting = True
                self.current_speed = self.sprint_speed

        # Обработка отпускания клавиш
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.moving_left = False
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.moving_right = False
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.moving_up = False
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.moving_down = False
            if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                self.is_sprinting = False
                self.current_speed = self.base_speed

    def move(self):
        # Вычисляем направление движения
        dx = 0
        dy = 0
        
        if self.moving_left:
            dx -= 1
        if self.moving_right:
            dx += 1
        if self.moving_up:
            dy -= 1
        if self.moving_down:
            dy += 1

        # Нормализация диагонального движения
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        # Применяем текущую скорость
        self.rect.x += dx * self.current_speed
        self.rect.y += dy * self.current_speed