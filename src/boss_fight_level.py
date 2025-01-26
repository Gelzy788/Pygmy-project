import pygame
import sys

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = 10

# Цвета
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# Настройка экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Boss Fight")


class Player(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.height = 100  # Нормальная высота
        self.crouch_height = 50  # Высота при приседании
        self.rect = pygame.Rect(100, HEIGHT - self.height, 50, self.height)
        self.velocity_y = 0
        self.on_ground = True
        self.hp = 100

    def update(self):
        # Обработка гравитации
        if not self.on_ground:
            self.velocity_y += GRAVITY
            self.rect.y += self.velocity_y

        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.on_ground = True
            self.velocity_y = 0

    def jump(self):
        if self.on_ground:
            self.velocity_y = -JUMP_STRENGTH
            self.on_ground = False

    def crouch(self):
        if self.rect.height != self.crouch_height:
            old_bottom = self.rect.bottom
            self.rect.height = self.crouch_height
            self.rect.bottom = old_bottom

    def stand(self):
        if self.rect.height != self.height:
            old_bottom = self.rect.bottom
            self.rect.height = self.height
            self.rect.bottom = old_bottom


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        dx = target_x - x
        dy = target_y - y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        self.speed = 7
        self.dx = (dx / distance) * self.speed if distance > 0 else 0
        self.dy = (dy / distance) * self.speed if distance > 0 else 0

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        # Удаляем снаряд, если он вышел за пределы экрана
        if not (0 <= self.rect.x <= WIDTH and 0 <= self.rect.y <= HEIGHT):
            self.kill()


class Boss(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.width = 100
        self.height = 150
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH - 200
        self.rect.y = HEIGHT - self.height
        self.attack_cooldown = 0
        self.projectiles = pygame.sprite.Group()

    def AttractionAttack(self, player):
        if self.attack_cooldown <= 0:
            # Создаем снаряд
            projectile = Projectile(self.rect.centerx, self.rect.centery,
                                    player.rect.centerx, player.rect.centery,
                                    self.projectiles)
            # КД в кадрах (1 секунда при 60 FPS)
            self.attack_cooldown = 60

    def update(self, player):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.projectiles.update()

        for projectile in self.projectiles:
            if projectile.rect.colliderect(player.rect):
                player.hp -= 5

                # Притягиваем игрока к боссу
                dx = self.rect.centerx - player.rect.centerx
                dy = self.rect.centery - player.rect.centery
                distance = (dx ** 2 + dy ** 2) ** 0.5

                move_distance = min(50, distance)
                if distance > 0:
                    player.rect.x += (dx / distance) * move_distance
                    player.rect.y += (dy / distance) * move_distance

                projectile.kill()

        # Проверяем близость игрока к боссу
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # Если игрок рядом с боссом, но не внутри него
        if distance <= self.width/2 + player.rect.width/2 + 10 and not self.rect.colliderect(player.rect):
            player.hp -= 15

            # Отталкиваем игрока от босса
            if distance > 0:
                push_x = -(dx / distance) * 400
                push_y = -(dy / distance) * 400

                player.rect.x += push_x
                player.rect.y += push_y

                player.rect.x = max(
                    0, min(player.rect.x, WIDTH - player.rect.width))
                player.rect.y = max(
                    0, min(player.rect.y, HEIGHT - player.rect.height))


def draw_death_menu(screen):
    menu_width = 400
    menu_height = 200
    menu_surface = pygame.Surface((menu_width, menu_height))
    menu_surface.fill((50, 50, 50))  # Тёмно-серый фон

    font = pygame.font.Font(None, 48)
    game_over_text = font.render("GAME OVER", True, (255, 0, 0))
    restart_text = font.render("Press R to Restart", True, (255, 255, 255))
    exit_text = font.render("Press Q to Quit", True, (255, 255, 255))

    menu_surface.blit(game_over_text,
                      (menu_width//2 - game_over_text.get_width()//2, 40))
    menu_surface.blit(restart_text,
                      (menu_width//2 - restart_text.get_width()//2, 100))
    menu_surface.blit(exit_text,
                      (menu_width//2 - exit_text.get_width()//2, 140))

    screen.blit(menu_surface,
                (WIDTH//2 - menu_width//2, HEIGHT//2 - menu_height//2))


def game_loop():
    all_sprites = pygame.sprite.Group()
    clock = pygame.time.Clock()
    player = Player(all_sprites)
    boss = Boss(all_sprites)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

        keys = pygame.key.get_pressed()

        # Проверка смерти игрока
        if player.hp <= 0:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "quit"

                death_keys = pygame.key.get_pressed()
                if death_keys[pygame.K_r]:
                    return "restart"
                if death_keys[pygame.K_q]:
                    return "quit"

                screen.fill(WHITE)
                for sprite in all_sprites:
                    if isinstance(sprite, Player):
                        pygame.draw.rect(screen, RED, sprite.rect)
                    else:
                        screen.blit(sprite.image, sprite.rect)
                boss.projectiles.draw(screen)

                # Отрисовка меню смерти поверх игры
                draw_death_menu(screen)

                pygame.display.flip()
                clock.tick(FPS)

        old_x = player.rect.x

        if keys[pygame.K_a]:
            player.rect.x -= 5
            for sprite in all_sprites:
                if sprite != player and player.rect.colliderect(sprite.rect):
                    player.rect.x = old_x
                    break
            if player.rect.left < 0:
                player.rect.x = 0

        if keys[pygame.K_d]:
            player.rect.x += 5
            for sprite in all_sprites:
                if sprite != player and player.rect.colliderect(sprite.rect):
                    player.rect.x = old_x
                    break
            if player.rect.right > WIDTH:
                player.rect.x = WIDTH - player.rect.width

        if keys[pygame.K_w]:
            player.jump()
        if keys[pygame.K_s]:
            player.crouch()
        else:
            player.stand()

        if keys[pygame.K_e]:
            boss.AttractionAttack(player)

        old_y = player.rect.y

        player.update()
        boss.update(player)

        for sprite in all_sprites:
            if sprite != player and player.rect.colliderect(sprite.rect):
                player.rect.y = old_y
                player.velocity_y = 0
                if old_y < sprite.rect.y:
                    player.on_ground = True
                break

        screen.fill(WHITE)
        for sprite in all_sprites:
            if isinstance(sprite, Player):
                pygame.draw.rect(screen, RED, sprite.rect)
            else:
                screen.blit(sprite.image, sprite.rect)

        boss.projectiles.draw(screen)

        hp_text = pygame.font.Font(None, 36).render(
            f'HP: {player.hp}', True, (0, 0, 0))
        screen.blit(hp_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)


def main():
    while True:
        result = game_loop()
        if result == "quit":
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
