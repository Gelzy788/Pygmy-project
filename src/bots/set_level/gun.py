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


class Gun(pygame.sprite.Sprite):
    image_bot = load_image("gun.png", scale=0.1)

    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = Gun.image_bot
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.add(group)