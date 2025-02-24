import pygame
import json
import math
import sqlite3


def smooth_path(path):
    n = 50  # задержка
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

        while not (x0 == x1 and y0 == y1):
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


def writing_path_to_json(paths, num_level):
    updated_paths = {}
    for bot_name, bot_data in paths.items():
        # Применяем smooth_path для каждого пути
        smoothed_path = smooth_path(bot_data["path"])
        # Обновляем путь в новом словаре
        updated_paths[bot_name] = {**bot_data, "path": smoothed_path}
        # print(f"Original path for {bot_name}: {bot_data['path']}")
        # print(f"Smoothed path for {bot_name}: {smoothed_path}")

    # print('updated_paths', updated_paths)
    with open(f'data/paths_{num_level}lvl.json', 'w') as f:
        json.dump(updated_paths, f, indent=2)


def add_info_to_db(paths, temp_paths, num_level, walls, bloods, cord_player):
    # Преобразование путей
    for i, path in enumerate(temp_paths):
        paths[f'bot_{i}'] = {'path': path, 'speed': 1}
    writing_path_to_json(paths, num_level)

    # Подготовка данных для вставки
    json_paths = f'data/paths_{num_level}lvl.json'
    json_bloods = json.dumps(bloods)
    json_player = json.dumps(cord_player if cord_player else [])
    json_walls = json.dumps(walls)

    conn = sqlite3.connect('data/levels.sqlite')
    cursor = conn.cursor()
    # SELECT script_paths, bloods, player, walls FROM info_levels WHERE num_lvl = ?
    cursor.execute('''
        INSERT OR REPLACE INTO info_levels (num_lvl, script_paths, bloods, player, walls)
        VALUES (?, ?, ?, ?, ?)
    ''', (num_level, json_paths, json_bloods, json_player, json_walls))

    conn.commit()
    conn.close()
    print(f'Данные уровня {num_level} успешно добавлены в базу данных')


def add_level():
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    screen.fill((0, 0, 0))
    pygame.display.set_caption('Создание нового уровня')

    # Создаем группу спрайтов для дверей
    door_sprites = pygame.sprite.Group()

    num_level = int(input('Введите номер уровня: '))
    player = int(input('Будет ли игрок на этом уровне? (1 = да/0 = нет): '))

    temp_paths = []
    bloods = []
    walls = []
    cord_player = ()
    paths = {}

    fps = 60
    clock = pygame.time.Clock()
    drawing = False  # режим рисования выключен
    set_wall = False  # ----------------------------------------<<<<<<
    have_player = False
    set_blood = False
    first_point = False
    change = False
    running = True
    screens = []
    print('---------------------------------|')
    print('Для расстановки стен нажминте "w"|')
    print('Для размещения крови нажмите "b" |')
    if have_player:
        print('Для размещения игрока нажмите "g"|')
    print('---------------------------------|')
    new_surface = pygame.Surface(screen.get_size())
    new_surface.fill((0, 0, 0))
    screens.append(new_surface.copy())
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                add_info_to_db(paths, temp_paths, num_level,
                               walls, bloods, cord_player)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if set_wall:
                    print('жми, то да се')
                    if not first_point:
                        x1, y1 = event.pos
                        pygame.draw.circle(
                            screen, (255, 255, 255), (x1, y1), 4, 0)
                        first_point = True
                        change = False
                    else:
                        pygame.draw.line(screen, (0, 0, 255),
                                         (x1, y1), (event.pos), 5)
                        pygame.draw.circle(
                            screen, (255, 255, 255), (x1, y1), 4, 0)
                        pygame.draw.circle(
                            screen, (255, 255, 255), (event.pos), 4, 0)
                        first_point = False
                        walls.append(((x1, y1), event.pos))
                        x1, y1 = 0, 0
                        change = False
                elif player and have_player and not cord_player:
                    print('[======================================================]')
                    print('[Задайте место расположения иргока нажитием кнопки мыши]')
                    print('[======================================================]')
                    #      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^изменить место вывода текста
                    pygame.draw.circle(screen, (0, 255, 0), (event.pos), 10, 0)
                    cord_player = event.pos
                    print(cord_player, '=======-=-==-=-=-=-=-=-=-=-=')
                    change = False
                elif set_blood:
                    pygame.draw.circle(screen, (255, 0, 0), (event.pos), 5, 0)
                    bloods.append(event.pos)
                    change = False
                else:
                    print('рисую ботов')
                    if not drawing:
                        change = False
                        pygame.draw.circle(
                            screen, (255, 255, 255), (event.pos), 5, 0)
                    temp_paths.append([event.pos])
                    drawing = True  # включаем режим рисования
            if event.type == pygame.MOUSEMOTION and drawing and not set_blood and not (have_player and not cord_player):
                screen_width, screen_height = screen.get_size()
                x, y = event.pos
                if 0 <= x < screen_width and 0 <= y < screen_height:
                    pygame.draw.circle(
                        screen, (255, 255, 255), (event.pos), 5, 0)
                    # print(temp_paths[0])
                    temp_paths[-1].append(event.pos)
                    # print(event.pos)
            if event.type == pygame.MOUSEBUTTONUP:
                screens.append(screen.copy())
                drawing = False
                change = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    if player:
                        have_player = not have_player
                        if have_player:
                            set_blood = False
                            set_wall = False
                            print('Включен режим размещения оружия')
                            print(
                                'Нажмите мышкой на место на котором хотите расположить оружие')
                            print('     -> для выключения нажмите "g"')
                        else:
                            print('Режим размещения ружия вылкючен')
                if event.key == pygame.K_w:
                    set_wall = not set_wall
                    if set_wall:
                        set_blood = False
                        have_player = False
                        print(
                            'Для размещения стены укажите 2 точки нажатием клавишы мыши')
                        # для выкл w
                    else:
                        first_point = False
                        if not (x1 == 0 and y1 == 0):
                            pygame.draw.circle(
                                screen, (0, 0, 0), (x1, y1), 4, 0)
                        # не хорошо работает
                        change = False
                if event.key == pygame.K_b:
                    set_blood = not set_blood
                    if set_blood:
                        set_wall = False
                        have_player = False
                        print('--------------------------------------------------|')
                        print('Включен режим размещения крови                    |')
                        print('Нажимайте на те места где хотите разместить кровь |')
                        print('                                                  |')
                        print('     -> для выключения нажмите "b"                |')
                        print('--------------------------------------------------|')
                        print('                                                  =')
                    else:
                        print('--------------------------------------------------|')
                        print('Режим размещения крови выключен                   |')
                        print('     -> для включения нажмите "b"                 |')
                        print('--------------------------------------------------|')
                        print('                                                  =')
                if event.key == pygame.K_p:
                    # Разместить дверь в текущей позиции мыши
                    door_x, door_y = pygame.mouse.get_pos()
                    door = Door(door_sprites, door_x, door_y)
                    print("Дверь размещена")
            if pygame.key.get_pressed()[pygame.K_z] and pygame.key.get_mods() & pygame.KMOD_LCTRL:
                if len(screens) > 1:
                    screens.pop()
                    temp_paths.pop()
        if change:
            screen.blit(screens[-1], (0, 0))
        # Отрисовка дверей
        door_sprites.draw(screen)
        clock.tick(fps)
        pygame.display.flip()


if __name__ == '__main__':
    add_level()
