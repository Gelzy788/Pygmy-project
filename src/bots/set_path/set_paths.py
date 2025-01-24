import pygame
import json


def writing_to_json(paths):
    with open('src/bots/set_path/paths.json', 'w') as f:
        json.dump(paths, f, indent=2)

    # with open('set_path/paths.json') as f:
    #     print(f.read())


def set_path():
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    screen.fill((0, 0, 0))
    pygame.display.set_caption('Пути передвижения ботов')
    temp_paths = []
    paths = {}
    x1, y1 = 0, 0
    w, h = 0, 0
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
