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
    2: {"right": 3, 'down': 5, "left": 1},    # Из третьего фона
    3: {"right": 4, "up": 0},    # Из четвертого фона
    4: {"right": 5, "up": 1, 'left': 3},    # Из пятого фона
    5: {"up": 2, 'left': 4},    # Из шестого фона
}

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

    # Проверка переходов между фонами
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
    pygame.draw.rect(screen, (0, 0, 0), (player_x,
                     player_y, player_width, player_height))
    pygame.display.flip()

    # Ограничение FPS
    clock.tick(60)

pygame.quit()
