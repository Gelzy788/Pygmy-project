import pygame
import os
import sys
import math


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


def rotate_image(image, angle):
    # Функция для поворота изображения
    return pygame.transform.rotate(image, angle)


class Player(pygame.sprite.Sprite):
    images_player_front = [load_image(
        f'player/player_{i}.png', scale=1) for i in range(1, 5)]
    image_player_back_left = load_image(
        f'player/player_back_left.png', scale=1)
    image_player_back_right = load_image(
        f'player/player_back_right.png', scale=1)
    image_player_back_up = load_image(f'player/player_back_up.png', scale=1)

    def __init__(self, group, x, y, blood_points=0, speed=6):
        super().__init__(group)
        self.image = Player.images_player_front[0]
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.blood_points = blood_points
        self.level_blood_points = 0
        self.speed = speed
        self.add(group)

        self.total_blood = blood_points  # Общее количество крови
        self.frame_counter = 1
        self.index_current_image = 0

        # Параметры движения
        self.moving_left = False
        self.moving_right = False
        self.moving_up = False
        self.moving_down = False
        self.is_sprinting = False

        self.base_speed = 6      # Постоянная скорость ходьбы
        self.sprint_speed = 10    # Скорость при спринте
        self.current_speed = self.base_speed
        self.safe_distance = 3

        self.screen_width = 800
        self.screen_height = 800

    def update(self, event):
        # Обработка нажатий клавиш
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.moving_left = True
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.moving_right = True
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.moving_up = True
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.moving_down = True
            if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                self.is_sprinting = True
                self.current_speed = self.sprint_speed

        # Обработка отпускания клавиш
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.moving_left = False
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.moving_right = False
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.moving_up = False
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.moving_down = False
            if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                self.is_sprinting = False
                self.current_speed = self.base_speed

        if self.moving_down and not (self.moving_left or self.moving_right):
            self.frame_counter += 1

            if self.frame_counter % 3 == 0:
                self.original_image = Player.images_player_front[self.index_current_image]
                self.index_current_image += 1
                self.index_current_image %= 4

            self.image = Player.images_player_front[self.index_current_image]
        else:
            self.frame_counter = 0
            self.index_current_image = 0

            if self.moving_up:
                self.original_image = Player.image_player_back_up
                if self.moving_right:
                    self.image = rotate_image(self.original_image, -45)
                elif self.moving_left:
                    self.image = rotate_image(self.original_image, 45)
                else:
                    self.image = self.original_image

            elif self.moving_right:
                if self.moving_down:
                    self.image = rotate_image(
                        Player.image_player_back_right, -45)
                else:
                    self.image = Player.image_player_back_right

            elif self.moving_left:
                if self.moving_down:
                    self.image = rotate_image(
                        Player.image_player_back_left, 45)
                else:
                    self.image = Player.image_player_back_left
        # Обновляем rect для изображения
        self.rect = self.image.get_rect(center=self.rect.center)

    def collect_blood(self, blood_sprites, bloods):
        for blood in blood_sprites:
            if self.rect.colliderect(blood.rect):
                blood.kill()
                self.level_blood_points += 1
                self.total_blood += 1  # Сразу увеличиваем общее количество

    def draw_blood_points(self, screen):
        font = pygame.font.Font(None, 36)
        text = font.render(
            # Показываем общее количество
            f'Очки крови: {self.total_blood}', True, (255, 0, 0))
        screen.blit(text, (10, 10))

    def distance_to_line(self, point, line_start, line_end):
        """ Вычисляет расстояние от точки до линии, заданной двумя точками """
        p = pygame.Vector2(point)
        a = pygame.Vector2(line_start)
        b = pygame.Vector2(line_end)

        ab = b - a
        ap = p - a
        proj = ab.dot(ap) / \
            ab.length_squared() if ab.length_squared() != 0 else 0
        closest = a + ab * max(0, min(1, proj))  # Проекция точки на отрезок

        return p.distance_to(closest)

    def get_collision_points(self, x, y):
        """ Возвращает ключевые точки для проверки столкновений """
        return [
            (x, y),  # Верхний левый угол
            (x + self.rect.width, y),  # Верхний правый угол
            (x, y + self.rect.height),  # Нижний левый угол
            (x + self.rect.width, y + self.rect.height),  # Нижний правый угол
            (x + self.rect.width // 2, y),  # Центр верхней грани
            (x + self.rect.width // 2, y + self.rect.height),  # Центр нижней грани
            (x, y + self.rect.height // 2),  # Центр левой грани
            (x + self.rect.width, y + self.rect.height // 2)  # Центр правой грани
        ]

    def check_collision(self, new_x, new_y, boundaries):
        """ Проверяет, уменьшится ли расстояние до стены после движения """
        for boundary in boundaries:
            for point in self.get_collision_points(self.rect.x, self.rect.y):
                dist_before = self.distance_to_line(
                    point, boundary.start, boundary.end)

            for point in self.get_collision_points(new_x, new_y):
                dist_after = self.distance_to_line(
                    point, boundary.start, boundary.end)

                if dist_after < self.safe_distance and dist_after < dist_before:
                    return True  # Если после движения расстояние уменьшилось до критического значения, отменяем действие
        return False

    def move(self, boundaries):
        keys = pygame.key.get_pressed()
        old_x = self.rect.x
        old_y = self.rect.y
        dx = 0
        dy = 0

        # Определяем направление движения
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed

        # Нормализация диагонального движения
        if dx != 0 and dy != 0:
            dx *= 0.7071  # 1/√2
            dy *= 0.7071

        # Проверяем новые координаты
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy

        # Проверяем столкновения
        if not self.check_collision(new_x, self.rect.y, boundaries):
            self.rect.x = new_x
        if not self.check_collision(self.rect.x, new_y, boundaries):
            self.rect.y = new_y

        # Проверка границ экрана
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.screen_width:
            self.rect.right = self.screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > self.screen_height:
            self.rect.bottom = self.screen_height
