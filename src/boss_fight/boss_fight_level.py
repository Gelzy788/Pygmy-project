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


class PlayerProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((8, 8))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x = float(x)
        self.y = float(y)
        self.speed = 10

        dx = target_x - x
        dy = target_y - y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        self.dx = (dx / distance) * self.speed if distance > 0 else 0
        self.dy = (dy / distance) * self.speed if distance > 0 else 0

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if not (0 <= self.rect.x <= WIDTH and 0 <= self.rect.y <= HEIGHT):
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.height = 100
        self.crouch_height = 50
        self.rect = pygame.Rect(100, HEIGHT - self.height, 50, self.height)
        self.velocity_y = 0
        self.on_ground = True
        self.hp = 100
        self.projectiles = pygame.sprite.Group()
        self.shoot_cooldown = 0

    def shoot(self, target_x, target_y):
        if self.shoot_cooldown <= 0:
            projectile = PlayerProjectile(self.rect.centerx, self.rect.centery,
                                          target_x, target_y, self.projectiles)
            self.shoot_cooldown = 20  # Кулдаун в кадрах (1/3 секунды)

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        self.projectiles.update()

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
        self.x = float(x)
        self.y = float(y)
        self.speed = 7

        dx = target_x - x
        dy = target_y - y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        self.dx = (dx / distance) * self.speed if distance > 0 else 0
        self.dy = (dy / distance) * self.speed if distance > 0 else 0

    def update(self, player):
        self.x += self.dx
        self.y += self.dy

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Удаляем снаряд, если он вышел за пределы экрана
        if not (0 <= self.rect.x <= WIDTH and 0 <= self.rect.y <= HEIGHT):
            self.kill()


class BigProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y, *groups):
        super().__init__(*groups)
        self.width = 30
        self.height = 30
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((255, 165, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x = float(x)
        self.y = float(y)
        self.speed = 3
        self.explosion_radius = 100

        dx = target_x - x
        dy = target_y - y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        self.dx = (dx / distance) * self.speed if distance > 0 else 0
        self.dy = (dy / distance) * self.speed if distance > 0 else 0

    def update(self, player):
        self.x += self.dx
        self.y += self.dy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if not (0 <= self.rect.x <= WIDTH and 0 <= self.rect.y <= HEIGHT):
            self.kill()

    def check_explosion_damage(self, boss):
        dx = boss.rect.centerx - self.rect.centerx
        dy = boss.rect.centery - self.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance <= self.explosion_radius:
            boss.hp -= 50


class WaveDamage(pygame.sprite.Sprite):
    def __init__(self, x, width, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((width, 20))
        self.image.fill((255, 165, 0))
        self.image.set_alpha(128)
        self.rect = self.image.get_rect()
        self.rect.bottom = HEIGHT
        self.rect.x = x
        self.warning_time = 60
        self.damage_dealt = False
        self.activated = False

    def update(self, player):
        if not self.activated:
            return

        if self.warning_time > 0:
            self.warning_time -= 1
            if self.warning_time % 10 < 5:
                self.image.fill((255, 165, 0))
            else:
                self.image.fill((255, 69, 0))
        else:
            if not self.damage_dealt:
                if (player.rect.colliderect(self.rect) and
                        player.rect.bottom >= HEIGHT - 10):
                    player.hp -= 25
                self.damage_dealt = True
                self.image.fill((255, 0, 0))
            self.kill()  # Удаляем сегмент сразу после взрыва


class VerticalBeam(pygame.sprite.Sprite):
    def __init__(self, x, *groups):
        super().__init__(*groups)
        self.width = 120
        self.height = HEIGHT
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((150, 0, 255))
        self.image.set_alpha(128)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.y = 0
        self.lifetime = 12 * 60
        self.damage_timer = 0

    def update(self, player):
        self.lifetime -= 1

        if self.lifetime % 10 < 5:
            self.image.fill((150, 0, 255))
        else:
            self.image.fill((200, 0, 255))
        self.image.set_alpha(128)

        self.damage_timer += 1
        if self.damage_timer >= 60:
            if player.rect.colliderect(self.rect):
                player.hp -= 7
            self.damage_timer = 0

        if self.lifetime <= 0:
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
        self.hp = 500
        self.max_hp = 500
        self.shield_active = False
        self.shield_cooldown = 0
        self.shield_duration = 180  # 3 секунды
        self.shield_color = (0, 255, 255, 128)  # Голубой полупрозрачный
        self.big_attack_cooldown = 0
        self.wave_attack_cooldown = 0
        self.wave_segments = pygame.sprite.Group()
        self.current_wave_position = self.rect.x
        self.is_wave_active = False
        self.wave_delay = 0
        self.segment_width = 119
        self.last_segment = None
        self.vertical_beam = None
        self.vertical_attack_cooldown = 0
        self.vertical_beams = pygame.sprite.Group()

    def activate_shield(self):
        if self.shield_cooldown <= 0:
            self.shield_active = True
            self.shield_cooldown = 360

    def deactivate_shield(self):
        self.shield_active = False
        self.shield_duration = 180  # Сбрасываем длительность для следующего использования

    def draw_hp_bar(self, screen):
        bar_width = self.width
        bar_height = 10
        bar_position = (self.rect.x, self.rect.y - 20)

        pygame.draw.rect(screen, (128, 128, 128),
                         (*bar_position, bar_width, bar_height))

        health_width = (self.hp / self.max_hp) * bar_width
        pygame.draw.rect(screen, (255, 0, 0),
                         (*bar_position, health_width, bar_height))

        font = pygame.font.Font(None, 24)
        hp_text = font.render(f'{self.hp}/{self.max_hp}', True, (0, 0, 0))
        text_pos = (bar_position[0] + bar_width//2 - hp_text.get_width()//2,
                    bar_position[1] - 15)
        screen.blit(hp_text, text_pos)

    def AttractionAttack(self, player):
        if self.attack_cooldown <= 0:
            # Создаем снаряд
            projectile = Projectile(self.rect.centerx, self.rect.centery,
                                    player.rect.centerx, player.rect.centery,
                                    self.projectiles)
            # КД в кадрах (1 секунда при 60 FPS)
            self.attack_cooldown = 60

    def BigProjectileAttack(self, player):
        if self.big_attack_cooldown <= 0:
            projectile = BigProjectile(self.rect.centerx, self.rect.centery,
                                       player.rect.centerx, player.rect.centery,
                                       self.projectiles)
            self.big_attack_cooldown = 180  #

    def WaveAttack(self):
        if self.wave_attack_cooldown <= 0 and not self.is_wave_active:
            self.is_wave_active = True
            self.current_wave_position = self.rect.x
            self.wave_attack_cooldown = 240
            self.wave_delay = 0
            self.wave_segments.empty()
            self.last_segment = None

    def VerticalBeamAttack(self, target_x):
        if self.vertical_attack_cooldown <= 0:
            if self.vertical_beam:
                self.vertical_beam.kill()
            self.vertical_beam = VerticalBeam(
                target_x, self.vertical_beams)
            self.vertical_attack_cooldown = 360

    def update(self, player):
        # Обновление щита
        if self.shield_active:
            self.shield_duration -= 1
            if self.shield_duration <= 0:
                self.shield_active = False
                self.shield_duration = 180

        if self.shield_cooldown > 0:
            self.shield_cooldown -= 1

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.big_attack_cooldown > 0:
            self.big_attack_cooldown -= 1
        if self.wave_attack_cooldown > 0:
            self.wave_attack_cooldown -= 1
        if self.vertical_attack_cooldown > 0:
            self.vertical_attack_cooldown -= 1

        if self.is_wave_active:
            if self.wave_delay > 0:
                self.wave_delay -= 1
            elif self.current_wave_position > 0:
                if not self.last_segment or not self.last_segment.warning_time:
                    segment = WaveDamage(
                        self.current_wave_position, self.segment_width, self.wave_segments)
                    self.current_wave_position -= (self.segment_width + 1)
                    self.wave_delay = 10

                    if not self.last_segment:
                        segment.activated = True
                    self.last_segment = segment
            else:
                self.is_wave_active = False
                self.last_segment = None

        active_segments = []
        for segment in self.wave_segments:
            if segment.activated:
                segment.update(player)
                if not segment.warning_time and len(active_segments) < len(self.wave_segments):
                    next_segments = [
                        s for s in self.wave_segments if not s.activated]
                    if next_segments:
                        next_segments[0].activated = True
            active_segments.append(segment)

        for beam in self.vertical_beams:
            beam.update(player)

        for projectile in self.projectiles:
            projectile.update(player)
            if projectile.rect.colliderect(player.rect):
                if isinstance(projectile, BigProjectile):
                    player.hp -= 30
                else:
                    player.hp -= 5
                if isinstance(projectile, BigProjectile):
                    projectile.check_explosion_damage(self)
                if not isinstance(projectile, BigProjectile):
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

        # Если игрок рядом с боссом
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

    def draw(self, screen):
        # Отрисовка босса
        screen.blit(self.image, self.rect)

        # Отрисовка щита
        if self.shield_active:
            shield_surface = pygame.Surface(
                (self.width + 20, self.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(shield_surface, self.shield_color,
                             (0, 0, self.width + 20, self.height + 20),
                             border_radius=10)
            screen.blit(shield_surface,
                        (self.rect.x - 10, self.rect.y - 10))

        # Отрисовка полоски здоровья
        self.draw_hp_bar(screen)


def draw_death_menu(screen):
    menu_width = 400
    menu_height = 200
    menu_surface = pygame.Surface((menu_width, menu_height))
    menu_surface.fill((50, 50, 50))

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

    # Загрузка изображения фона
    background = pygame.image.load("data/backgrounds/boss_level_1_background.jpg").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    player.shoot(mouse_x, mouse_y)

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
                boss.vertical_beams.draw(screen)
                player.projectiles.draw(screen)
                boss.wave_segments.draw(screen)

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

        if keys[pygame.K_z]:
            boss.WaveAttack()

        if keys[pygame.K_q]:
            boss.BigProjectileAttack(player)

        if keys[pygame.K_x]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            boss.VerticalBeamAttack(mouse_x)

        if keys[pygame.K_c]:
            boss.activate_shield()

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

        # Отрисовка фона
        screen.blit(background, (0, 0))

        for sprite in all_sprites:
            if isinstance(sprite, Player):
                pygame.draw.rect(screen, RED, sprite.rect)
            elif isinstance(sprite, Boss):
                boss.draw(screen)  # Используем новый метод draw
            else:
                screen.blit(sprite.image, sprite.rect)

        boss.projectiles.draw(screen)
        boss.vertical_beams.draw(screen)
        player.projectiles.draw(screen)
        boss.wave_segments.draw(screen)

        hp_text = pygame.font.Font(None, 36).render(
            f'HP: {player.hp}', True, (0, 0, 0))
        screen.blit(hp_text, (10, 10))

        # Проверяем попадания снарядов игрока в босса
        for player_projectile in player.projectiles:
            if player_projectile.rect.colliderect(boss.rect):
                if not boss.shield_active:  # Проверяем наличие щита
                    boss.hp -= 10
                player_projectile.kill()
                if boss.hp <= 0:
                    return "victory"

            for boss_projectile in boss.projectiles:
                if (isinstance(boss_projectile, BigProjectile) and
                        player_projectile.rect.colliderect(boss_projectile.rect)):
                    boss_projectile.check_explosion_damage(boss)
                    boss_projectile.kill()
                    player_projectile.kill()
                    break

        # Отрисовка полоски здоровья босса
        boss.draw_hp_bar(screen)

        pygame.display.flip()
        clock.tick(FPS)


def draw_victory_menu(screen):
    menu_width = 400
    menu_height = 200
    menu_surface = pygame.Surface((menu_width, menu_height))
    menu_surface.fill((50, 50, 50))

    font = pygame.font.Font(None, 48)
    victory_text = font.render("VICTORY!", True, (0, 255, 0))
    restart_text = font.render("Press R to Restart", True, (255, 255, 255))
    exit_text = font.render("Press Q to Quit", True, (255, 255, 255))

    menu_surface.blit(victory_text,
                      (menu_width//2 - victory_text.get_width()//2, 40))
    menu_surface.blit(restart_text,
                      (menu_width//2 - restart_text.get_width()//2, 100))
    menu_surface.blit(exit_text,
                      (menu_width//2 - exit_text.get_width()//2, 140))

    screen.blit(menu_surface,
                (WIDTH//2 - menu_width//2, HEIGHT//2 - menu_height//2))


def main():
    while True:
        result = game_loop()
        if result == "quit":
            break
        elif result == "victory":
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                keys = pygame.key.get_pressed()
                if keys[pygame.K_r]:
                    break
                if keys[pygame.K_q]:
                    pygame.quit()
                    sys.exit()

                draw_victory_menu(screen)
                pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
