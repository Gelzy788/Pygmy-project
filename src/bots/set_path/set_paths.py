import pygame
import json
import math


def smooth_path(path, min_distance=10):
    if not path:
        return []

    smoothed = [path[0]]  # Начинаем с первой точки
    last_point = path[0]

    for point in path[1:]:
        distance = math.sqrt((point[0] - last_point[0]) ** 2 + (point[1] - last_point[1]) ** 2)
        print(distance, distance >= min_distance, last_point, point)
        if distance >= min_distance:
            smoothed.append(point)
            last_point = point
    print('return', smoothed)
    return smoothed


def writing_to_json(paths):
    updated_paths = {}
    for bot_name, bot_data in paths.items():
        # Применяем smooth_path для каждого пути
        smoothed_path = smooth_path(bot_data["path"])
        updated_paths[bot_name] = {**bot_data, "path": smoothed_path}  # Обновляем путь в новом словаре
        print(f"Original path for {bot_name}: {bot_data['path']}")
        print(f"Smoothed path for {bot_name}: {smoothed_path}")

    print('updated_paths', updated_paths)
    with open('src/bots/set_path/paths.json', 'w') as f:
        json.dump(updated_paths, f, indent=2)

'''
def smooth_path(path, min_distance=100):
    if not path:
        return []

    smoothed = [path[0]]  # Начинаем с первой точки

    for i in range(1, len(path)):
        current_point = pygame.Vector2(path[i])
        last_point = pygame.Vector2(smoothed[-1])

        # Вычисляем расстояние между текущей и последней точкой
        dist = current_point.distance_to(last_point)

        # Если расстояние больше минимального порога, добавляем точку
        if dist > min_distance:
            smoothed.append(path[i])

    return smoothed


def writing_to_json(paths):
    with open('src/bots/set_path/paths.json', 'w') as f:
        # Обновляем только пути для каждого бота
        updated_paths = {
            bot_name: {"path": smooth_path(bot_data["path"]), **bot_data}
            for bot_name, bot_data in paths.items()
        }
        json.dump(updated_paths, f, indent=2)
'''
    # with open('set_path/paths.json') as f:
    #     print(f.read())
# data = {bot_name: {"path": smooth_path(bot_data["path"]), **bot_data} for bot_name, bot_data in paths.items()}

def set_path():
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    screen.fill((0, 0, 0))
    pygame.display.set_caption('Пути передвижения ботов')
    temp_paths = []
    paths = {}
    v = 0  # пикселей в секунду
    fps = 60
    velocity = 0
    clock = pygame.time.Clock()
    drawing = False  # режим рисования выключен
    change = False
    running = True
    screens = []
    new_surface = pygame.Surface(screen.get_size())
    new_surface.fill((0, 0, 0))
    screens.append(new_surface.copy())
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                for i, path in enumerate(temp_paths):
                    paths[f'bot_{i}'] = {'path': path,
                                        'speed': 1}
                # print(paths)
                writing_to_json(paths)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not drawing:
                    change = False
                    pygame.draw.circle(screen, (255, 255, 255), (event.pos), 5, 0)
                temp_paths.append([event.pos])
                drawing = True  # включаем режим рисования
            if event.type == pygame.MOUSEMOTION and drawing:
                screen_width, screen_height = screen.get_size()
                x, y = event.pos
                
                if 0 <= x < screen_width and 0 <= y < screen_height:
                    pygame.draw.circle(screen, (255, 255, 255), (event.pos), 5, 0)
                    # print(temp_paths[0])
                    temp_paths[-1].append(event.pos)
                    # print(event.pos)
            if event.type == pygame.MOUSEBUTTONUP:
                screens.append(screen.copy())
                drawing = False
                change = True
            if pygame.key.get_pressed()[pygame.K_z] and pygame.key.get_mods() & pygame.KMOD_LCTRL:
                if len(screens) > 1:
                    screens.pop()
                    temp_paths.pop()
        if change:
            screen.blit(screens[-1], (0, 0))
        clock.tick(fps)
        pygame.display.flip()


if __name__ == '__main__':
    set_path()
