import pygame
import os


def load_image(name, colorkey=None, scale=1):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        # Возвращаем пустую поверхность если файл не найден
        return pygame.Surface((50, 80))
    image = pygame.image.load(fullname)
    size = image.get_size()
    new_size = (int(size[0] * scale), int(size[1] * scale))
    image = pygame.transform.scale(image, new_size)
    return image


class Door(pygame.sprite.Sprite):
    # Подставьте свою картинку двери
    image_door = load_image("door.png", scale=0.2)

    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = Door.image_door
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.add(group)
