import pygame
from boss_fight.settings import WIDTH, HEIGHT, GRAVITY, JUMP_STRENGTH
from boss_fight.projectile import PlayerProjectile
import os


class Player(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.height = 100
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

        # Анимация
        self.current_animation = 'idle'
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.animation_time = 0

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

        # Загрузка спрайтов
        try:
            root_dir = os.path.dirname(os.path.dirname(
                os.path.dirname(__file__)))  # путь к src
            data_dir = os.path.join(root_dir, 'data')
            sprites_dir = os.path.join(data_dir, 'sprites')

            # Создаем директории, если их нет
            os.makedirs(sprites_dir, exist_ok=True)

            sprite_path = os.path.join(sprites_dir, 'main_person.jpg')
            print(
                f"Пытаюсь загрузить спрайт из: {os.path.abspath(sprite_path)}")

            if not os.path.exists(sprite_path):
                print("No")
            else:
                self.load_sprite_sheet(sprite_path)

        except Exception as e:
            print(f"ОШИБКА при загрузке спрайта: {e}")
            self.create_debug_sprite()

        # Инициализация спрайта
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = HEIGHT - self.height

    def load_sprite_sheet(self, sprite_path):
        """Загружает и нарезает спрайтшит"""
        try:
            sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
            print(
                f"Спрайт успешно загружен. Размеры: {sprite_sheet.get_size()}")

            sprite_width = sprite_sheet.get_width() // 7
            sprite_height = sprite_sheet.get_height() // 6

            print(f"Размеры одного спрайта: {sprite_width}x{sprite_height}")

            self.animations = {
                'idle': [self._get_sprite(sprite_sheet, 0, 0, sprite_width, sprite_height)],
                'walk': [self._get_sprite(sprite_sheet, x, 1, sprite_width, sprite_height)
                         for x in range(6)],
                'crouch': [self._get_sprite(sprite_sheet, x, 2, sprite_width, sprite_height)
                           for x in range(2)],
                'uncrouch': [self._get_sprite(sprite_sheet, x, 2, sprite_width, sprite_height)
                             for x in range(2, 4)],
                'jump': [self._get_sprite(sprite_sheet, x, 3, sprite_width, sprite_height)
                         for x in range(6)],
                'death': [self._get_sprite(sprite_sheet, x, 5, sprite_width, sprite_height)
                          for x in range(5)]
            }

            # Устанавливаем начальный спрайт
            self.image = self.animations['idle'][0]
            print("Все анимации успешно загружены")
            # Отладочная информация
            for anim_name, frames in self.animations.items():
                print(f"Анимация {anim_name}: {len(frames)} кадров")
                if not frames:
                    print(f"ОШИБКА: Нет кадров для анимации {anim_name}")

        except Exception as e:
            print(f"ОШИБКА при загрузке спрайтшита: {e}")
            self.create_debug_sprite()

    def _get_sprite(self, sheet, column, row, width, height):
        """Получает отдельный спрайт из спрайтшита"""
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(sheet, (0, 0), (column * width,
                   row * height, width, height))
        return pygame.transform.scale(image, (self.width, self.height))

    def set_animation(self, animation_name):
        """Устанавливает текущую анимацию"""
        if animation_name in self.animations and self.current_animation != animation_name:
            print(f"Смена анимации на: {animation_name}")  # Отладочный вывод
            self.current_animation = animation_name
            self.animation_frame = 0
            self.animation_time = 0
            # Сразу устанавливаем первый кадр новой анимации
            self.image = self.animations[animation_name][0]
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
            # Отладочная информация
            print(f"Установлен спрайт размером: {self.image.get_size()}")

    def update_animation(self):
        """Обновляет текущий кадр анимации"""
        self.animation_time += self.animation_speed
        if self.animation_time >= 1:
            self.animation_time = 0
            self.animation_frame = (
                self.animation_frame + 1) % len(self.animations[self.current_animation])

        # Получаем текущий кадр
        current_frame = self.animations[self.current_animation][self.animation_frame]

        # Отражаем спрайт, если нужно
        if not self.facing_right:
            current_frame = pygame.transform.flip(current_frame, True, False)

        self.image = current_frame

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
