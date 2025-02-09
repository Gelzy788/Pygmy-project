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
    image_bot = load_image("player1.png", scale=0.5)

    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = Player.image_bot
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.add(group)

        self.screen_width = 800
        self.screen_height = 800
        self.base_speed = 6
        self.sprint_speed = 12
        self.current_speed = self.base_speed

    def update(self, event):
        move_x = 0
        move_y = 0

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                move_x = -self.current_speed
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                move_x = self.current_speed
            elif event.key in [pygame.K_UP, pygame.K_w]:
                move_y = -self.current_speed
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                move_y = self.current_speed

            if event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                self.current_speed = self.sprint_speed

        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                self.current_speed = self.base_speed

        self.move(move_x, move_y)

    def move(self, move_x, move_y):
        new_x = self.rect.x + move_x
        new_y = self.rect.y + move_y

        if 0 <= new_x <= self.screen_width - self.rect.width:
            self.rect.x = new_x
        if 0 <= new_y <= self.screen_height - self.rect.height:
            self.rect.y = new_y
