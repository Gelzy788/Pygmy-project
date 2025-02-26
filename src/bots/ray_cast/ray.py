from ray_cast.particle import Particle
import pygame as pg
import math
import sqlite3

drawline = pg.draw.line


class Ray:
    def __init__(self, p: Particle, heading: float = 0, user_id: int = None):
        self.start = p.pos
        self.heading = heading
        self.end: pg.math.Vector2 = pg.math.Vector2()
        self.image = None

        # Получаем значение скрытности из БД
        if user_id is not None:
            conn = sqlite3.connect('data/levels.sqlite')
            cursor = conn.cursor()
            cursor.execute('SELECT stealth FROM user WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()
            # Устанавливаем длину луча равной значению скрытности
            self.length = result[0] if result else 100
        else:
            self.length = 100  # значение по умолчанию

        self.signal = False

    def update(self, screen: pg.display, p: Particle, boundaries: list, cord_player, angle_rotation: int = 0):
        self.start = p.pos
        self.end.from_polar((10000, self.heading - angle_rotation))

        closest = float("inf")
        new_end = pg.Vector2()
        flag_r = False  # <======================================================
        x3 = self.start.x
        x4 = self.end.x
        y3 = self.start.y
        y4 = self.end.y

        for b in boundaries:
            x1 = b.start.x
            x2 = b.end.x
            y1 = b.start.y
            y2 = b.end.y

            den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if den == 0:
                return

            t_num = (x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)
            t = t_num / den
            u_num = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3))
            u = u_num / den

            if u >= 0 and 0 <= t <= 1:
                x = x1 + t * (x2 - x1)
                y = y1 + t * (y2 - y1)
                dist = self.start.distance_to((x, y))
                if dist < closest:
                    closest = dist
                    new_end.xy = x, y  # точка пересечения

        '''
        # рабочий способ

        angle_degrees = (math.degrees(math.atan2(cord_player[1] - self.start[1], cord_player[0] - self.start[0])) + 360) % 360
        # angle_degrees = -angle_degrees % 360 if 360 >= angle_degrees >= 180 else angle_degrees
        player_distance = self.start.distance_to(cord_player)
        # temp = -(abs(angle_rotation) % 360) if angle_rotation < 0 else angle_rotation % 360
        temp1 = (360 - angle_rotation) % 360 if -angle_rotation < 0 else (-angle_rotation) % 360
        temp1_145 = (360 + (temp1 - 145)) % 360 if (temp1 - 145) < 0 else (temp1 - 145) % 360
        if (temp1 >= angle_degrees >=  temp1_145) if temp1 >= 145 else ((temp1 >= angle_degrees) or (angle_degrees >=  temp1_145)):
            if (player_distance <= self.length):
                # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ тут надо подобрать формулу для -angle_rotation % 180
                self.signal = True
                print(self.start, self.end)
                # print('=' * 50)
                # print('temp1:',  round(temp1, 3), round(angle_degrees, 3), round(temp1_145, 3), '-----', player_distance)
                flag_r = True
        # отладка
        # print('temp1:',  round(temp1, 3), 
        #      'angle_rotation', round(angle_rotation, 3),
        #      'temp1_145:',  round(temp1_145, 3), '_________', 
        #      round(angle_degrees, 3), '=====', 
        #      round(player_distance, 3))
        '''
        # отладка
        # print(f"Start: {self.start}, End: {self.end}")
        # print(f"Boundary Start: {x1}, End: {x2}")
        # print(f"den: {den}, t: {t}, u: {u}")
        '''
        # рабочий
        if Ray.is_player_in_segment_range(pg.Vector2(self.start), pg.Vector2(self.end[0], self.end[1]), pg.Vector2(cord_player), self.length):
            flag_r = True
            print('луч вас увидел')
        '''

        if closest == float("inf"):
            self.end = self.start
        else:
            # Устанавливаем конечную точку на основе пересечения
            self.end = new_end
            # print('новая длина вектора', pg.Vector2(self.start).distance_to(pg.Vector2(self.end)))

        # Ограничиваем длину луча до self.length
        if self.start.distance_to(self.end) > self.length:
            # Нормализуем вектор направления
            direction = (self.end - self.start).normalize()
            # Устанавливаем конечную точку на максимальной длине
            self.end = self.start + direction * self.length
            if Ray.is_player_in_segment_range(pg.Vector2(self.start), pg.Vector2(self.end[0], self.end[1]), pg.Vector2(cord_player), self.length):
                flag_r = True
                # print('луч вас увидел')
                self.signal = True
        else:
            # print('новая длина вектора', pg.Vector2(self.start).distance_to(pg.Vector2(self.end)))
            len_temp = pg.Vector2(self.start).distance_to(pg.Vector2(self.end))
            if Ray.is_player_in_segment_range(pg.Vector2(self.start), pg.Vector2(self.end[0], self.end[1]), pg.Vector2(cord_player), len_temp):
                flag_r = True
                # print('луч вас увидел')
                self.signal = True

        self.image = drawline(screen, (255, 0, 0) if flag_r else (
            100, 100, 100), self.start, self.end, 1)

        if self.signal:
            # <------------------------------------------------------ нужно убрать для того
            self.signal = False
            # чтобы раунд сразу заканчивался после того как бот заметил игрока
            return True
        return False

    def is_player_in_segment_range(start, end, cord_player, max_distance=100, tolerance=5):
        start = pg.Vector2(start)
        end = pg.Vector2(end)
        cord_player = pg.Vector2(cord_player)

        # Проверка расстояния от игрока до прямой, проходящей через start и end
        line_vec = end - start  # Вектор отрезка
        player_vec = cord_player - start  # Вектор от start до игрока

        # Проекция вектора игрока на вектор линии (скалярное произведение)
        projection_length = player_vec.dot(
            line_vec) / line_vec.length_squared()

        # Вычисляем точку на линии, ближайшую к игроку
        closest_point = start + projection_length * line_vec

        # Проверка, находится ли ближайшая точка на отрезке [start, end]
        if projection_length < 0 or projection_length > 1:
            return False  # Ближайшая точка выходит за границы отрезка

        # Проверка отклонения игрока от прямой
        distance_to_line = cord_player.distance_to(closest_point)
        if distance_to_line > tolerance:
            return False  # Игрок слишком далеко от линии

        # Проверка расстояния от start до игрока
        if start.distance_to(cord_player) > max_distance:
            return False

        return True
