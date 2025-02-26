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
        root_dir = os.path.dirname(os.path.dirname(
            os.path.dirname(__file__))) 
        data_dir = os.path.join(root_dir, 'data')
        sprites_dir = os.path.join(data_dir, 'sprites')

        sprite_path = os.path.join(sprites_dir, 'main_person.png')
        self.load_sprite_sheet(sprite_path)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]

        # Анимация
        self.current_animation = 'idle'
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.animation_time = 0

        self.rect.x = 100  # Начальная позиция по X
        self.rect.y = HEIGHT - self.height

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


        # Инициализация спрайта
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = HEIGHT - self.height

    def load_sprite_sheet(self, sprite_path):
        """Загружает и нарезает спрайтшит"""
        sprite_sheet = load_image(sprite_path)
        print(
            f"Спрайт успешно загружен. Размеры: {sprite_sheet.get_size()}")

        sprite_width = sprite_sheet.get_width() // 7
        sprite_height = sprite_sheet.get_height() // 6

        self.rect = pygame.Rect(0, 0, sprite_sheet.get_width() // 6, 
                                sprite_sheet.get_height() // 7)
        for j in range(7):
            for i in range(6):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sprite_sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

                
        # self.animations = {
        #     'idle': [self._get_sprite(sprite_sheet, 0, 0, sprite_width, sprite_height)],
        #     'walk': [self._get_sprite(sprite_sheet, x, 1, sprite_width, sprite_height)
        #                 for x in range(6)],
        #     'crouch': [self._get_sprite(sprite_sheet, x, 2, sprite_width, sprite_height)
        #                 for x in range(2)],
        #     'uncrouch': [self._get_sprite(sprite_sheet, x, 2, sprite_width, sprite_height)
        #                     for x in range(2, 4)],
        #     'jump': [self._get_sprite(sprite_sheet, x, 3, sprite_width, sprite_height)
        #                 for x in range(6)],
        #     'death': [self._get_sprite(sprite_sheet, x, 5, sprite_width, sprite_height)
        #                 for x in range(5)]
        # }

        # Устанавливаем начальный спрайт
        # self.image = self.animations['idle'][0]
        # print("Все анимации успешно загружены")
        # # Отладочная информация
        # for anim_name, frames in self.animations.items():
        #     print(f"Анимация {anim_name}: {len(frames)} кадров")
        #     if not frames:
        #         print(f"ОШИБКА: Нет кадров для анимации {anim_name}")

    def shoot(self, target_x, target_y):
        if self.shoot_cooldown <= 0:
            projectile = PlayerProjectile(self.rect.centerx, self.rect.centery,
                                          target_x, target_y, self.projectiles)
            self.shoot_cooldown = 20

    def update(self):
        # print(self.cur_frame, self.frames)
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

        print(self.cur_frame)

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

    # ... остальные методы класса Player ...
