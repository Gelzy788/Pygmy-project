import pygame
import json
import math

# сделать сглаживание пути, наоборот
# добовлять дополнительные точки между теми у которых большое расстояние
# !
# !
# !
# !
# !
# проблема с ctrl + z



def smooth_path(path):
    n = 50 # задержка
    if not path:
        return []

    smoothed = []
    smoothed += [path[0]] * (n - 1)
    for i in range(len(path) - 1):
        x0, y0 = path[i][0], path[i][1]
        x1, y1 = path[i + 1][0], path[i + 1][1]
        if math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2) == 1:
            smoothed.append((x0, y0))
            continue
        
        while not(x0 == x1 and y0 == y1):
            smoothed.append((x0, y0))
            x_d = x1 - x0
            y_d = y1 - y0
            if abs(x_d) == abs(y_d):
                x0 += x_d // abs(x_d)
                y0 += y_d // abs(y_d)
            elif abs(x_d) > abs(y_d):
                x0 += x_d // abs(x_d)
            else:
                y0 += y_d // abs(y_d)
    smoothed += [path[-1]] * n

    return smoothed


def writing_to_json(paths):
    updated_paths = {}
    for bot_name, bot_data in paths.items():
        # Применяем smooth_path для каждого пути
        smoothed_path = smooth_path(bot_data["path"])
        updated_paths[bot_name] = {**bot_data, "path": smoothed_path}  # Обновляем путь в новом словаре
        print(f"Original path for {bot_name}: {bot_data['path']}")
        # print(f"Smoothed path for {bot_name}: {smoothed_path}")

    # print('updated_paths', updated_paths)
    with open('src/bots/set_path/paths.json', 'w') as f:
        json.dump(updated_paths, f, indent=2)


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
