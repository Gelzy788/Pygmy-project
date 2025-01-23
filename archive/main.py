import pygame
import os

# Инициализация PyGame
pygame.init()

# Настройка окна
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Игра")

# Загрузка фонов
backgrounds = []
for i in range(1, 7):  # Загружаем фоны с 1 по 6
    bg = pygame.image.load(os.path.join(f"data/{i}.png"))
    bg = pygame.transform.scale(bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
    backgrounds.append(bg)

# Размер тайла для коллизий
TILE_SIZE = 1


def load_collision_map(file_path):
    """
    Загружает матрицу коллизий из текстового файла
    """
    level_map = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                row = [int(num) for num in line.strip().split(',')]
                level_map.append(row)
        return level_map
    except FileNotFoundError:
        print(f"Ошибка: Файл {file_path} не найден")
        return None
    except Exception as e:
        print(f"Произошла ошибка при чтении файла: {e}")
        return None


# Словарь для хранения стен каждого фона
walls_by_background = {}

# Загружаем карты коллизий для каждого фона
for i in range(1, 7):
    walls = []
    level_map = load_collision_map(f'data/{i}.txt')
    if level_map:
        for row_index, row in enumerate(level_map):
            for col_index, cell in enumerate(row):
                if cell == 1:  # Если это стена
                    wall = pygame.Rect(col_index * TILE_SIZE,
                                       row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    walls.append(wall)
        walls_by_background[i-1] = walls
    else:
        walls_by_background[i-1] = []  # Пустой список, если файл не найден

# Параметры игрока
player_width = 15
player_height = 15
player_x = WINDOW_WIDTH // 2 - player_width // 2
player_y = WINDOW_HEIGHT // 2 - player_height // 2
player_speed = 5

# Текущий фон (начинаем с первого, индекс 0)
current_bg = 0

# Словарь переходов между фонами
transitions = {
    0: {"right": 1, "down": 3},  # Из первого фона
    1: {"right": 2, "down": 4, 'left': 0},  # Из второго фона
    2: {'down': 5, "left": 1},    # Из третьего фона
    3: {"right": 4, "up": 0},    # Из четвертого фона
    4: {"right": 5, "up": 1, 'left': 3},    # Из пятого фона
    5: {"up": 2, 'left': 4},    # Из шестого фона
}

# Создаем поверхность для отображения коллизий
collision_surface = pygame.Surface(
    (WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

# Игровой цикл
running = True
clock = pygame.time.Clock()

while running:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Управление игроком
    keys = pygame.key.get_pressed()
    old_x, old_y = player_x, player_y

    if keys[pygame.K_a]:  # Влево
        player_x -= player_speed
    if keys[pygame.K_d]:  # Вправо
        player_x += player_speed
    if keys[pygame.K_w]:  # Вверх
        player_y -= player_speed
    if keys[pygame.K_s]:  # Вниз
        player_y += player_speed

    # Создаем прямоугольник игрока для проверки коллизий
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

    # Проверка коллизий со стенами текущего фона
    collision_occurred = False
    for wall in walls_by_background[current_bg]:
        if player_rect.colliderect(wall):
            collision_occurred = True
            player_x, player_y = old_x, old_y
            break

    # Если нет коллизии, проверяем переходы между фонами
    if not collision_occurred:
        if player_x >= WINDOW_WIDTH - player_width and current_bg in transitions and "right" in transitions[current_bg]:
            current_bg = transitions[current_bg]["right"]
            player_x = 0
        elif player_x < 0 and current_bg in transitions and "left" in transitions[current_bg]:
            current_bg = transitions[current_bg]["left"]
            player_x = WINDOW_WIDTH - player_width
        elif player_y >= WINDOW_HEIGHT - player_height and current_bg in transitions and "down" in transitions[current_bg]:
            current_bg = transitions[current_bg]["down"]
            player_y = 0
        elif player_y < 0 and current_bg in transitions and "up" in transitions[current_bg]:
            current_bg = transitions[current_bg]["up"]
            player_y = WINDOW_HEIGHT - player_height
        else:
            # Если перехода нет, ограничиваем движение границами экрана
            player_x = max(0, min(player_x, WINDOW_WIDTH - player_width))
            player_y = max(0, min(player_y, WINDOW_HEIGHT - player_height))

    # Отрисовка
    screen.blit(backgrounds[current_bg], (0, 0))

    # Отрисовка коллизий (для отладки)
    collision_surface.fill((0, 0, 0, 0))
    for wall in walls_by_background[current_bg]:
        pygame.draw.rect(collision_surface, (255, 0, 0, 128), wall)
    screen.blit(collision_surface, (0, 0))

    # Отрисовка игрока
    pygame.draw.rect(screen, (0, 0, 255), (player_x,
                     player_y, player_width, player_height))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
