import pygame
import math
from boss_fight.settings import WIDTH, HEIGHT
from boss_fight.projectile import Projectile, BigProjectile
import random
import os
import sys


def load_image(name, colorkey=None):
    fullname = os.path.join('data', 'sprites', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class WaveDamage(pygame.sprite.Sprite):
    def __init__(self, x, width, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((width, 20))
        self.image.fill((255, 165, 0))
        self.image.set_alpha(128)
        self.rect = self.image.get_rect()
        self.rect.bottom = HEIGHT
        self.rect.x = x
        self.warning_time = 60
        self.damage_dealt = False
        self.activated = False

    def update(self, player):
        if not self.activated:
            return

        if self.warning_time > 0:
            self.warning_time -= 1
            if self.warning_time % 10 < 5:
                self.image.fill((255, 165, 0))
            else:
                self.image.fill((255, 69, 0))
        else:
            if not self.damage_dealt:
                if (player.rect.colliderect(self.rect) and
                        player.rect.bottom >= HEIGHT - 10):
                    player.hp -= 25
                self.damage_dealt = True
                self.image.fill((255, 0, 0))
            self.kill()


class VerticalBeam(pygame.sprite.Sprite):
    def __init__(self, x, *groups):
        super().__init__(*groups)
        self.width = 120
        self.height = HEIGHT
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((150, 0, 255))
        self.image.set_alpha(128)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.y = 0
        self.lifetime = 12 * 60
        self.damage_timer = 0

    def update(self, player):
        self.lifetime -= 1

        if self.lifetime % 10 < 5:
            self.image.fill((150, 0, 255))
        else:
            self.image.fill((200, 0, 255))
        self.image.set_alpha(128)

        self.damage_timer += 1
        if self.damage_timer >= 60:
            if player.rect.colliderect(self.rect):
                player.hp -= 7
            self.damage_timer = 0

        if self.lifetime <= 0:
            self.kill()


class SlowField(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, *groups):
        super().__init__(*groups)
        self.width = 200
        self.height = 200
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        rect = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.arc(self.image, (0, 191, 255, 128), rect,
                        math.pi, 2 * math.pi, 5)
        pygame.draw.rect(self.image, (0, 191, 255, 128),
                         (0, self.height // 2, self.width, self.height // 2))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = HEIGHT
        self.lifetime = 5 * 60
        self.has_slowed = False

    def update(self, player):
        self.lifetime -= 1
        if self.rect.colliderect(player.rect) and not self.has_slowed:
            player.slow_duration = 20 * 60
            player.speed_multiplier = 0.5
            self.has_slowed = True
        if self.lifetime <= 0:
            self.kill()


class AcidPool(pygame.sprite.Sprite):
    def __init__(self, x, *groups):
        super().__init__(*groups)
        self.width = 150
        self.height = 30
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (124, 252, 0, 160),
                            (0, 0, self.width, self.height))
        pygame.draw.ellipse(self.image, (0, 180, 0, 180),
                            (self.width // 4, self.height // 4,
                             self.width // 2, self.height // 2))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = HEIGHT
        self.lifetime = 10 * 60
        self.damage_timer = 0
        self.affected_players = set()

    def update(self, player):
        self.lifetime -= 1
        self.damage_timer += 1
        if self.rect.colliderect(player.rect):
            if self.damage_timer >= 30:
                player.hp -= 3
                self.damage_timer = 0
            if player not in self.affected_players:
                player.poison_duration = 25 * 60
                self.affected_players.add(player)
        if self.lifetime <= 0:
            self.kill()


class Boss(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        # self.width = 100
        # self.height = 150
        self.frames = []
        self.load_sprite_sheet("boss_sprite_sheet.png")
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        # self.rect = self.image.get_rect(topleft=(WIDTH - 200, HEIGHT - self.height))

        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.rect = self.image.get_rect(topleft=(WIDTH - 200, HEIGHT - self.height))

        # Анимации
        self.current_animation = 'idle'
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.animations = {
            'idle': self.frames[7:14],   # 8-14 кадр - стоит
            'big_attack': self.frames[15:19]  # 16-19 кадры - большая атака
        }

        self.attack_cooldown = 0
        self.projectiles = pygame.sprite.Group()
        self.hp = 500
        self.max_hp = 500
        self.shield_active = False
        self.shield_cooldown = 0
        self.shield_duration = 180
        self.shield_color = (0, 255, 255, 128)
        self.wave_attack_cooldown = 0
        self.wave_segments = pygame.sprite.Group()
        self.current_wave_position = self.rect.x
        self.is_wave_active = False
        self.wave_delay = 0
        self.segment_width = 119
        self.last_segment = None
        self.vertical_beams = pygame.sprite.Group()
        self.vertical_attack_cooldown = 0
        self.vertical_beam = None
        self.slow_fields = pygame.sprite.Group()
        self.slow_field_cooldown = 0
        self.acid_pools = pygame.sprite.Group()
        self.acid_attack_cooldown = 0

    def AttractionAttack(self, player):
        if self.attack_cooldown <= 0:
            projectile = Projectile(self.rect.centerx, self.rect.centery,
                                    player.rect.centerx, player.rect.centery,
                                    self.projectiles)
            self.attack_cooldown = 60

    def load_sprite_sheet(self, sprite_path):
        """Загружает и нарезает спрайтшит"""
        sprite_sheet = load_image(sprite_path)
        sprite_width = sprite_sheet.get_width() // 6
        sprite_height = sprite_sheet.get_height() // 6

        for j in range(6):
            for i in range(6):
                frame_location = (sprite_width * i, sprite_height * j)
                self.frames.append(sprite_sheet.subsurface(pygame.Rect(
                    frame_location, (sprite_width, sprite_height))))

    def set_animation(self, animation_name):
        if self.current_animation != animation_name:
            self.current_animation = animation_name
            self.animation_frame = 0
            self.image = self.animations[self.current_animation][self.animation_frame]

    def update_animation(self):
        self.animation_frame = (self.animation_frame + self.animation_speed) % len(
            self.animations[self.current_animation])
        self.image = self.animations[self.current_animation][int(self.animation_frame)]

    def activate_shield(self):
        if self.shield_cooldown <= 0:
            self.shield_active = True
            self.shield_cooldown = 360

    def deactivate_shield(self):
        self.shield_active = False
        self.shield_duration = 180

    def draw(self, screen):
        # Отрисовка босса
        screen.blit(self.image, self.rect)

        # Отрисовка щита, если он активен
        if self.shield_active:
            shield_surface = pygame.Surface(
                (self.width + 20, self.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(shield_surface, self.shield_color,
                             (0, 0, self.width + 20, self.height + 20),
                             border_radius=10)
            screen.blit(shield_surface,
                        (self.rect.x - 10, self.rect.y - 10))

        # Отрисовка полоски здоровья
        self.draw_hp_bar(screen)

    def draw_hp_bar(self, screen):
        """Отрисовывает полоску здоровья босса."""
        bar_width = self.width
        bar_height = 10
        bar_position = (self.rect.x, self.rect.y - 20)

        # Фон полоски здоровья
        pygame.draw.rect(screen, (128, 128, 128),
                         (*bar_position, bar_width, bar_height))

        # Текущее здоровье
        health_width = (self.hp / self.max_hp) * bar_width
        pygame.draw.rect(screen, (255, 0, 0),
                         (*bar_position, health_width, bar_height))

        # Текст с количеством здоровья
        font = pygame.font.Font(None, 24)
        hp_text = font.render(f'{self.hp}/{self.max_hp}', True, (0, 0, 0))
        text_pos = (bar_position[0] + bar_width // 2 - hp_text.get_width() // 2,
                    bar_position[1] - 15)
        screen.blit(hp_text, text_pos)

    def WaveAttack(self):
        if self.wave_attack_cooldown <= 0 and not self.is_wave_active:
            self.is_wave_active = True
            self.current_wave_position = self.rect.x
            self.wave_attack_cooldown = 240
            self.wave_delay = 0
            self.wave_segments.empty()
            self.last_segment = None

    def SlowFieldAttack(self, target_x, target_y):
        if self.slow_field_cooldown <= 0:
            # Создаем поле рядом с игроком
            field = SlowField(target_x, HEIGHT, target_x,
                              target_y, self.slow_fields)
            self.slow_field_cooldown = 600  # 10 секунд кулдауна

    def AcidPoolAttack(self, target_x):
        if self.acid_attack_cooldown <= 0:
            pool = AcidPool(target_x, self.acid_pools)
            self.acid_attack_cooldown = 480  # 8 секунд кулдауна

    def VerticalBeamAttack(self, target_x):
        if self.vertical_attack_cooldown <= 0:
            if self.vertical_beam:
                self.vertical_beam.kill()
            self.vertical_beam = VerticalBeam(target_x, self.vertical_beams)
            self.vertical_attack_cooldown = 360

    def BigProjectileAttack(self, player):
        """Атака большим снарядом."""
        if self.attack_cooldown <= 0:
            self.set_animation('big_attack')
            projectile = BigProjectile(
                self.rect.centerx, self.rect.centery,
                player.rect.centerx, player.rect.centery,
                self.projectiles
            )
            self.attack_cooldown = 180  # Устанавливаем кулдаун для атаки

    def update(self, player):
        self.update_animation()

        if self.current_animation == 'big_attack' and self.animation_frame >= len(self.animations['big_attack']) - 1:
            self.set_animation('idle')

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.shield_cooldown > 0:
            self.shield_cooldown -= 1
        if self.vertical_attack_cooldown > 0:
            self.vertical_attack_cooldown -= 1
        if self.slow_field_cooldown > 0:
            self.slow_field_cooldown -= 1
        if self.acid_attack_cooldown > 0:
            self.acid_attack_cooldown -= 1

        # Обновляем и проверяем столкновения снарядов
        for projectile in self.projectiles:
            projectile.update(player)
            if projectile.rect.colliderect(player.rect):
                if isinstance(projectile, BigProjectile):
                    player.hp -= 30
                else:
                    player.hp -= 5
                    dx = self.rect.centerx - player.rect.centerx
                    dy = self.rect.centery - player.rect.centery
                    distance = (dx ** 2 + dy ** 2) ** 0.5
                    move_distance = min(50, distance)

                    if distance > 0:
                        new_x = player.rect.x + (dx / distance) * move_distance
                        new_y = player.rect.y + (dy / distance) * move_distance
                        player.rect.x = int(new_x)
                        player.rect.y = int(new_y)

                        if player.rect.colliderect(self.rect):
                            player.hp -= 35
                            if player.rect.centerx < WIDTH // 2:
                                player.rect.right = WIDTH - 50
                            else:
                                player.rect.left = 50
                            player.rect.bottom = HEIGHT

                projectile.kill()

        if self.shield_active:
            self.shield_duration -= 1
            if self.shield_duration <= 0:
                self.shield_active = False
                self.shield_duration = 180

        # Обновление волновой атаки
        if self.is_wave_active:
            if self.wave_delay > 0:
                self.wave_delay -= 1
            elif self.current_wave_position > 0:
                if not self.last_segment or not self.last_segment.warning_time:
                    segment = WaveDamage(
                        self.current_wave_position, self.segment_width, self.wave_segments)
                    self.current_wave_position -= (self.segment_width + 1)
                    self.wave_delay = 10

                    if not self.last_segment:
                        segment.activated = True
                    self.last_segment = segment
            else:
                self.is_wave_active = False
                self.last_segment = None

        active_segments = []
        for segment in self.wave_segments:
            if segment.activated:
                segment.update(player)
                if not segment.warning_time and len(active_segments) < len(self.wave_segments):
                    next_segments = [
                        s for s in self.wave_segments if not s.activated]
                    if next_segments:
                        next_segments[0].activated = True
            active_segments.append(segment)

        # Обновляем вертикальные лучи
        for beam in self.vertical_beams:
            beam.update(player)

        # Обновляем все замедляющие поля
        for field in self.slow_fields:
            field.update(player)

        # Обновляем кислотные лужи
        for pool in self.acid_pools:
            pool.update(player)