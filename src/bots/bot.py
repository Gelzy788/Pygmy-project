import pygame
import math
import os
import sys
from ray_cast.particle import Particle
from ray_cast.ray import Ray


def load_image(name, colorkey=None, scale=1):
    fullname = os.path.join('data', name)
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


class Bot(pygame.sprite.Sprite):
    image_bot_stay = load_image("bot/bot_stay.png", scale=0.7)
    images_bots = [load_image(f'bot/bot_{i}.png', scale=0.7) for i in range(1, 18)]

    def __init__(self, group, bot_id, path: list, particle: Particle, indices, direction, speed=1):
        super().__init__(group)
        self.image = Bot.image_bot_stay
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.index_current_image = 0
        self.bot_id = bot_id
        self.path = path
        self.particle = particle
        self.indices = indices
        self.direction = direction
        self.speed = speed
        self.frame_counter = 0
        self.add(group)
    
    def update(self, screen, viewing_angle, ray: list[Ray], boundaries, cord_player):
        index = self.indices
        speed = self.particle.speed
        direction = self.direction
        
        index += direction * speed

        # Зацикливаем индекс по пути (если бот достиг конца пути)
        if index >= len(self.path):  # Достигнут конец пути
            index = len(self.path) - 1
            self.direction = -1  # Меняем направление на обратное
        elif index < 0:  # Достигнут начало пути
            index = 0
            self.direction = 1  # Меняем направление на прямое
        
        # Получаем координаты текущей точки пути
        x, y = self.path[int(index)]

        if self.direction == 1:
            future_index = min(int(index) + 10, len(self.path) - 1)
        else:
            future_index = max(int(index) - 10, 0)

        xf, yf = self.path[future_index]

        x0, y0 = self.particle.pos
        # Вычисляем угол к будущей точке пути с учетом направления движения
        angle_rotation = -math.degrees(math.atan2(yf - y0, xf - x0)) - viewing_angle / 2
        # print(angle_rotation, '\t', self.particle.current_angle)

        # Вычисляем минимальную разницу углов
        delta_angle = (angle_rotation - self.particle.current_angle + 180) % 360 - 180

        # Увеличиваем скорость поворота для резких углов
        smooth_speed = 0.05  # Базовая скорость
        angle_difference = abs(delta_angle)

        # Увеличиваем скорость плавного изменения для резких поворотов
        if angle_difference > 60:  # Если угол больше 60 градусов, увеличиваем скорость
            smooth_speed *= 3
        elif angle_difference > 30:  # Если угол больше 30 градусов, увеличиваем скорость
            smooth_speed *= 2

        # Применяем плавное изменение угла
        self.particle.current_angle += delta_angle * smooth_speed

        # Обновляем позицию частицы
        self.particle.update(screen, x, y)

        # Добавляем обновление позиции спрайта
        self.rect.centerx = int(x)  # используем centerx для центрирования спрайта
        self.rect.centery = int(y)  # используем centery для центрирования спрайта


        # Проверяем, изменилось ли положение
        if self.path[int(index)] == self.path[int(self.indices)]:
            self.image = Bot.image_bot_stay  # Если стоит, то обычное изображение
            # Поворачиваем изображение
            self.image = rotate_image(self.image, self.particle.current_angle + 67.5)
            self.index_current_image = 0
        else:
            # Чередуем анимацию
            self.frame_counter += 1
            if self.frame_counter % 5 == 0:  # Каждые 10 кадров смена изображения
                self.original_image = Bot.images_bots[self.index_current_image]
                self.index_current_image += 1
                self.index_current_image %= 17

            # Поворачиваем изображение
            self.image = rotate_image(self.original_image, self.particle.current_angle + 67.5)
        # Обновляем rect для изображения
        self.rect = self.image.get_rect(center=self.rect.center)

        self.indices = index
        # print(self.particle.current_angle, delta_angle) # -67,5 смотрит вправо

        '''
        # Проверяем, находится ли игрок в поле зрения и в пределах видимости
        if self.is_player_in_sight(cord_player, viewing_angle, max_distance=100):
            print("Игрок в поле зрения бота и в пределах видимости!")
        '''
        # Обновляем лучи для этой частицы
        # signal = False
        signal_temp = []
        for r in ray:
            signal_temp.append(r.update(screen, self.particle, boundaries, cord_player, self.particle.current_angle))

        if any(signal_temp):
            return True
        return False
    
    def is_player_in_sight(self, player_pos, viewing_angle, max_distance):
        # Рассчитываем угол между направлением взгляда бота и позицией игрока
        dx = player_pos[0] - self.particle.pos[0]
        dy = player_pos[1] - self.particle.pos[1]
        player_angle = math.degrees(math.atan2(dy, dx))

        # Нормализуем угол зрения бота
        angle_diff = (player_angle - self.particle.current_angle + 180) % 360 - 180
        half_fov = viewing_angle #/ 2  # Половина угла зрения

        # Рассчитываем расстояние между ботом и игроком
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Проверяем, попадает ли игрок в поле зрения и находится ли он в пределах видимости
        if abs(angle_diff) <= half_fov and distance <= max_distance:
            # print(distance)
            return True
        return False