import json
import math
import sqlite3


# paths = {
#     "object_1": [
#         (35, 31), (35, 33), (35, 38), (35, 42), 
#         (35, 50), (35, 59), (36, 68), (36, 81), 
#         (36, 88), (35, 96), (35, 105), (35, 110), 
#         (34, 116), (34, 120), (33, 125), (33, 126),
#         (33, 127)
#     ],
#     "object_2": [
#     (138, 36), (138, 37), (137, 39), (137, 41),
#     (137, 42), (137, 44), (137, 47), (137, 49), 
#     (137, 50), (137, 52), (137, 54)
#     ]
# }
'''
x1, y1 = 1, 1
x2, y2 = 4, 5

# Разница координат
delta_x = x2 - x1
delta_y = y2 - y1

# Угол в радианах
theta_radians = math.atan2(y2 - y1, x2 - x1)

# Угол в градусах
theta_degrees = round(math.degrees(math.atan2(y2 - y1, x2 - x1)))
'''

# paths = {'bot_0': 
#     {'path': [
#         (75, 57), (77, 57), (79, 57), (83, 58), 
#         (97, 59), (106, 60), (120, 61), (138, 62), 
#         (154, 63), (181, 64), (200, 66), (216, 66), 
#         (227, 66), (240, 67), (251, 67), (256, 67), (257, 67)
#         ],
#     'speed': 1
#     },
# 'bot_1': 
#     {'path': [
#         (718, 430), (719, 435), (719, 444), (720, 449), 
#         (721, 469), (721, 482), (722, 504), (722, 515), 
#         (722, 530), (721, 547), (721, 558), (720, 566), 
#         (719, 574), (719, 580), (719, 581)
#         ], 
#     'speed': 1
#     }
# }

with open('src/bots/set_path/paths.json') as f:
    templates: dict = json.load(f)

print(templates['bot_0']['speed'])

paths = {
    bot: [(x, y) for x, y in data["path"]]
    for bot, data in templates.items()
}
print()
print(paths)
# with open('src/bots/set_path/paths.json', 'w') as f:
#     json.dump(paths, f, indent=2)

# with open('src/bots/set_path/paths.json') as f:
#     print(f.read())




def get_info_from_db(num_level):
    conn = sqlite3.connect('data/levels.sqlite')
    cursor = conn.cursor()

    # Запрос для получения информации по num_lvl
    result = cursor.execute('''
        SELECT paths_bots, bloods, gun, walls FROM info_levels WHERE num_lvl = ?
    ''', (num_level,)).fetchall()

    conn.close()

    if result:
        # Десериализация данных из JSON
        paths_bots = result[0]  # Путь к файлу с данными (например, data/paths_1lvl.json)
        bloods = json.loads(result[1])  # Десериализация крови
        gun = json.loads(result[2])  # Десериализация координат оружия
        walls = json.loads(result[3])  # Десериализация стен

        return paths_bots, bloods, gun, walls
    else:
        # print(f'Данные для уровня {num_level} не найдены')
        return None