import pygame
from settings import WIDTH, HEIGHT


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x = float(x)
        self.y = float(y)
        self.speed = 7

        dx = target_x - x
        dy = target_y - y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        self.dx = (dx / distance) * self.speed if distance > 0 else 0
        self.dy = (dy / distance) * self.speed if distance > 0 else 0

    def update(self, player):
        self.x += self.dx
        self.y += self.dy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if not (0 <= self.rect.x <= WIDTH and 0 <= self.rect.y <= HEIGHT):
            self.kill()


class BigProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, *groups):
        super().__init__(*groups)
        self.width = 30
        self.height = 30
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((255, 165, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x = float(x)
        self.y = float(y)
        self.speed = 3
        self.explosion_radius = 100

        dx = target_x - x
        dy = target_y - y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        self.dx = (dx / distance) * self.speed if distance > 0 else 0
        self.dy = (dy / distance) * self.speed if distance > 0 else 0

    def update(self, player):
        self.x += self.dx
        self.y += self.dy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if not (0 <= self.rect.x <= WIDTH and 0 <= self.rect.y <= HEIGHT):
            self.kill()

    def check_explosion_damage(self, boss):
        dx = boss.rect.centerx - self.rect.centerx
        dy = boss.rect.centery - self.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance <= self.explosion_radius:
            boss.hp -= 50


class PlayerProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((8, 8))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x = float(x)
        self.y = float(y)
        self.speed = 10

        dx = target_x - x
        dy = target_y - y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        self.dx = (dx / distance) * self.speed if distance > 0 else 0
        self.dy = (dy / distance) * self.speed if distance > 0 else 0

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if not (0 <= self.rect.x <= WIDTH and 0 <= self.rect.y <= HEIGHT):
            self.kill()
