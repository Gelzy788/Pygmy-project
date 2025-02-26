import pygame
from boss_fight.settings import WIDTH, HEIGHT, GRAVITY, JUMP_STRENGTH
from boss_fight.projectile import PlayerProjectile
import os
import sys


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class Player(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.height = 68
        self.crouch_height = 50
        self.width = 50

        # Инициализируем базовые атрибуты до загрузки спрайтов
        root_dir = os.path.dirname(os.path.dirname(
            os.path.dirname(__file__)))
        data_dir = os.path.join(root_dir, 'data')
        sprites_dir = os.path.join(data_dir, 'sprites')
        sprite_path = os.path.join(sprites_dir, 'main_person.png')

        self.velocity_y = 0
        self.on_ground = True
        self.hp = 100
        self.projectiles = pygame.sprite.Group()
        self.shoot_cooldown = 0
        self.speed_multiplier = 1.0
        self.base_speed = 5
        self.current_speed = self.base_speed
        self.slow_duration = 0
        self.poison_duration = 0
        self.poison_damage_timer = 0
        self.is_crouching = False
        self.is_dead = False
        self.facing_right = True
        self.frames = []
        self.load_sprite_sheet(sprite_path)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect(topleft=(100, 6))

        # Анимация
        self.current_animation = 'idle'
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.animation_time = 0

        self.rect = self.image.get_rect(topleft=(100, 6))


        # Создаем иконки эффектов
        self.slow_icon = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.slow_icon, (0, 191, 255, 200),
                           (10, 10), 8)  # Голубая иконка
        pygame.draw.polygon(self.slow_icon, (255, 255, 255, 200),
                            # Белая стрелка внутри
                            [(5, 10), (15, 5), (15, 15)])

        self.poison_icon = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.poison_icon, (124, 252, 0, 200),
                           (10, 10), 8)  # Зеленая иконка
        pygame.draw.polygon(self.poison_icon, (0, 180, 0, 200),
                            # Темно-зеленый череп
                            [(10, 4), (16, 16), (4, 16)])

        print(
            f"Пытаюсь загрузить спрайт из: {os.path.abspath(sprite_path)}")

        if not os.path.exists(sprite_path):
            print("No")
        else:
            self.load_sprite_sheet(sprite_path)

    def load_sprite_sheet(self, sprite_path):
        """Загружает и нарезает спрайтшит"""
        sprite_sheet = load_image(sprite_path)
        print(
            f"Спрайт успешно загружен. Размеры: {sprite_sheet.get_size()}")

        sprite_width = sprite_sheet.get_width() // 7
        sprite_height = sprite_sheet.get_height() // 6

        self.rect = pygame.Rect(0, 0, sprite_sheet.get_width() // 6,
                                sprite_sheet.get_height() // 7)
        self.rect.topleft = (0, 532)
        for j in range(7):
            for i in range(6):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sprite_sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

        # Определение анимаций
        self.animations = {
            'idle': [self.frames[0]],  # 1 кадр - стоит
            'walk': self.frames[6:12],  # с 7 по 12 кадр - ходьба
            'crouch': self.frames[12:14],  # 13-14 - присяд
            'uncrouch': self.frames[14:16],  # 15-16 - встать с присяда
            'jump': self.frames[18:24],  # 19-24 - прыжок
            'death': self.frames[30:35]  # 31-35 - смерть
        }

        # Устанавливаем начальную анимацию
        self.current_animation = 'idle'
        self.animation_frame = 0
        self.image = self.animations[self.current_animation][self.animation_frame]

    def set_animation(self, animation_name):
        if self.current_animation != animation_name:
            self.current_animation = animation_name
            self.animation_frame = 0
            self.image = self.animations[self.current_animation][self.animation_frame]

    def shoot(self, target_x, target_y):
        if self.shoot_cooldown <= 0:
            projectile = PlayerProjectile(self.rect.centerx, self.rect.centery,
                                          target_x, target_y, self.projectiles)
            self.shoot_cooldown = 20

    def update(self):
        # Обновление анимации
        self.animation_frame = (self.animation_frame + self.animation_speed) % len(
            self.animations[self.current_animation])
        self.image = self.animations[self.current_animation][int(self.animation_frame)]

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
            self.set_animation('jump')

    def crouch(self):
        if self.rect.height != self.crouch_height:
            old_bottom = self.rect.bottom
            self.rect.height = self.crouch_height
            self.rect.bottom = old_bottom
            self.set_animation('crouch')

    def stand(self):
        if self.rect.height != self.height:
            old_bottom = self.rect.bottom
            self.rect.height = self.height
            self.rect.bottom = old_bottom
            self.set_animation('uncrouch')

    def draw_effect_icons(self, screen):
        # Отрисовка иконки замедления
        if self.slow_duration > 0:
            screen.blit(self.slow_icon, (10, 40))
            # Полоска длительности
            duration_width = (self.slow_duration / (20 * 60)
                              ) * 20  # 20 секунд максимум
            pygame.draw.rect(screen, (128, 128, 128), (10, 62, 20, 3))
            pygame.draw.rect(screen, (0, 191, 255),
                             (10, 62, duration_width, 3))

        # Отрисовка иконки отравления
        if self.poison_duration > 0:
            screen.blit(self.poison_icon, (40, 40))
            # Полоска длительности
            duration_width = (self.poison_duration / (25 * 60)
                              ) * 20  # 25 секунд максимум
            pygame.draw.rect(screen, (128, 128, 128), (40, 62, 20, 3))
            pygame.draw.rect(screen, (124, 252, 0),
                             (40, 62, duration_width, 3))