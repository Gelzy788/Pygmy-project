import pygame


class Door(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.width = 50
        self.height = 80
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((255, 0, 0))  # Красный цвет
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.add(group)
