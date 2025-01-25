import pygame
import os

# Инициализация PyGame
pygame.init()

# Настройка окна
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Игра")

# Загрузка фона
background = pygame.image.load(os.path.join("data/1.png"))
background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))

# Размер тайла (блока) на карте - уменьшим для более точных коллизий
TILE_SIZE = 1


def load_collision_map(file_path):
    """
    Загружает матрицу коллизий из текстового файла
    """
    level_map = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                # Преобразуем строку в список чисел
                row = [int(num) for num in line.strip().split(',')]
                level_map.append(row)
        print(f"Размер загруженной карты: {
              len(level_map)}x{len(level_map[0])}")
        return level_map
    except FileNotFoundError:
        print(f"Ошибка: Файл {file_path} не найден")
        return None
    except Exception as e:
        print(f"Произошла ошибка при чтении файла: {e}")
        return None


# Загружаем матрицу из файла
level_map = load_collision_map('data/1.txt')

if not level_map:
    print("Ошибка загрузки карты коллизий!")
    pygame.quit()
    exit()

# Создаем список для хранения стен (препятствий)
walls = []

# Создаем стены на основе карты
for row_index, row in enumerate(level_map):
    for col_index, cell in enumerate(row):
        if cell == 1:  # Если это стена
            wall = pygame.Rect(col_index * TILE_SIZE,
                               row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            walls.append(wall)
            print(f"Создана стена: x={wall.x}, y={wall.y}")

print(f"Создано стен: {len(walls)}")  # Отладочный вывод

# Параметры игрока
player_width = 15
player_height = 15
player_x = 100  # Начальная позиция игрока
player_y = 100
player_speed = 5
player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

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

    # Сохраняем предыдущую позицию
    old_x = player_rect.x
    old_y = player_rect.y

    # Перемещение игрока
    if keys[pygame.K_a]:  # Влево
        player_rect.x -= player_speed
    if keys[pygame.K_d]:  # Вправо
        player_rect.x += player_speed
    if keys[pygame.K_w]:  # Вверх
        player_rect.y -= player_speed
    if keys[pygame.K_s]:  # Вниз
        player_rect.y += player_speed

    # Проверка коллизий со стенами
    collision_occurred = False
    for wall in walls:
        if player_rect.colliderect(wall):
            collision_occurred = True
            print(f"Коллизия! Игрок: {player_rect}, Стена: {
                  wall}")  # Отладочный вывод
            player_rect.x = old_x
            player_rect.y = old_y
            break

    # Отрисовка
    screen.fill((255, 255, 255))
    screen.blit(background, (0, 0))  # Отрисовка фона

    # Отрисовка коллизий (для отладки)
    collision_surface.fill((0, 0, 0, 0))  # Очищаем поверхность
    for wall in walls:
        pygame.draw.rect(collision_surface, (255, 0, 0, 128), wall)
    screen.blit(collision_surface, (0, 0))

    # Отрисовка игрока
    # Синий цвет для лучшей видимости
    pygame.draw.rect(screen, (0, 0, 255), player_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
2
