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


class Player(pygame.sprite.Sprite):
    image_bot = load_image("player1.png", scale=0.2)

    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = Player.image_bot
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.add(group)

        self.blood_points = 0

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
    
    def collect_blood(self, blood_sprites, bloods):
        for blood in blood_sprites.sprites():
            if self.rect.colliderect(blood.rect):  # Проверяем столкновение игрока с кровью
                print(f"Координаты перед удалением спрайта: {blood.rect.x}, {blood.rect.y}")
                self.blood_points += 1
                blood.kill()  # Удаляем спрайт
    
    def draw_blood_points(self, screen):
        font = pygame.font.Font(None, 36)  # Размер шрифта 36
        text = font.render(f'Очки крови: {self.blood_points}', True, (255, 0, 0))  # Красный цвет
        screen.blit(text, (10, 10))  # Рисуем в левом верхнем углу

    def distance_to_line(self, point, line_start, line_end):
        """ Вычисляет расстояние от точки до линии, заданной двумя точками """
        p = pygame.Vector2(point)
        a = pygame.Vector2(line_start)
        b = pygame.Vector2(line_end)

        ab = b - a
        ap = p - a
        proj = ab.dot(ap) / ab.length_squared() if ab.length_squared() != 0 else 0
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
                dist_before = self.distance_to_line(point, boundary.start, boundary.end)

            for point in self.get_collision_points(new_x, new_y):
                dist_after = self.distance_to_line(point, boundary.start, boundary.end)

                if dist_after < self.safe_distance and dist_after < dist_before:
                    return True  # Если после движения расстояние уменьшилось до критического значения, отменяем действие
        return False

    def move(self, boundaries):
        dx, dy = 0, 0

        if self.moving_left:
            dx -= 1
        if self.moving_right:
            dx += 1
        if self.moving_up:
            dy -= 1
        if self.moving_down:
            dy += 1

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        new_x = self.rect.x + dx * self.current_speed
        new_y = self.rect.y + dy * self.current_speed

        if not self.check_collision(new_x, self.rect.y, boundaries):
            self.rect.x = new_x

        if not self.check_collision(self.rect.x, new_y, boundaries):
            self.rect.y = new_y