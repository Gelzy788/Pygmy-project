import pygame
from settings import WIDTH, HEIGHT, GRAVITY, JUMP_STRENGTH
from projectile import PlayerProjectile


class Player(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.height = 100
        self.crouch_height = 50
        self.rect = pygame.Rect(100, HEIGHT - self.height, 50, self.height)
        self.velocity_y = 0
        self.on_ground = True
        self.hp = 100
        self.projectiles = pygame.sprite.Group()
        self.shoot_cooldown = 0
        self.speed_multiplier = 1.0  # Множитель скорости
        self.base_speed = 5  # Базовая скорость движения
        self.slow_duration = 0  # Длительность эффекта замедления
        self.poison_duration = 0  # Длительность эффекта яда
        self.poison_damage_timer = 0  # Таймер для урона от яда

    def shoot(self, target_x, target_y):
        if self.shoot_cooldown <= 0:
            projectile = PlayerProjectile(self.rect.centerx, self.rect.centery,
                                          target_x, target_y, self.projectiles)
            self.shoot_cooldown = 20

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        self.projectiles.update()

        if not self.on_ground:
            self.velocity_y += GRAVITY
            self.rect.y += self.velocity_y

        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.on_ground = True
            self.velocity_y = 0

        # Обработка замедления
        if self.slow_duration > 0:
            self.slow_duration -= 1
            self.speed_multiplier = 0.5
            if self.slow_duration <= 0:
                self.speed_multiplier = 1.0

        self.current_speed = self.base_speed * self.speed_multiplier

        # Обработка урона от яда (1 урон в секунду)
        if self.poison_duration > 0:
            self.poison_duration -= 1
            self.poison_damage_timer += 1
            if self.poison_damage_timer >= 60:  # Каждую секунду
                self.hp -= 1
                self.poison_damage_timer = 0

    def jump(self):
        if self.on_ground:
            self.velocity_y = -JUMP_STRENGTH
            self.on_ground = False

    def crouch(self):
        if self.rect.height != self.crouch_height:
            old_bottom = self.rect.bottom
            self.rect.height = self.crouch_height
            self.rect.bottom = old_bottom

    def stand(self):
        if self.rect.height != self.height:
            old_bottom = self.rect.bottom
            self.rect.height = self.height
            self.rect.bottom = old_bottom

    # ... остальные методы класса Player ...
