from boss_fight.settings import WIDTH, HEIGHT, WHITE, RED, FPS, screen
from boss_fight.boss_fight_player import Player
from boss_fight.boss import Boss
from boss_fight.utils import draw_death_menu
from boss_fight.projectile import BigProjectile
import pygame
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_game():
    all_sprites = pygame.sprite.Group()
    clock = pygame.time.Clock()
    player = Player(all_sprites)
    boss = Boss(all_sprites)

    # Словарь с подсказками по управлению
    controls_info = {
        "1": "Притягивающая атака",
        "2": "Большой снаряд",
        "3": "Волновая атака",
        "4": "Вертикальный луч",
        "5": "Щит",
        "6": "Замедляющее поле",
        "7": "Кислотная лужа",
    }

    font = pygame.font.Font(None, 24)

    while True:
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    player.shoot(mouse_x, mouse_y)

        keys = pygame.key.get_pressed()

        # Тестовые атаки по цифрам
        if keys[pygame.K_1]:
            boss.AttractionAttack(player)
        if keys[pygame.K_2]:
            boss.BigProjectileAttack(player)
        if keys[pygame.K_3]:
            boss.WaveAttack()
        if keys[pygame.K_4]:
            boss.VerticalBeamAttack(mouse_x)
        if keys[pygame.K_5]:
            if not boss.shield_active:
                boss.activate_shield()
            else:
                boss.deactivate_shield()
        if keys[pygame.K_6]:
            boss.SlowFieldAttack(player.rect.centerx, player.rect.centery)
        if keys[pygame.K_7]:
            boss.AcidPoolAttack(player.rect.centerx)

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
                draw_death_menu(screen)
                pygame.display.flip()
                clock.tick(FPS)

        # Управление игроком
        old_x = player.rect.x
        if keys[pygame.K_a]:
            player.rect.x -= player.current_speed
            # Проверка столкновения с боссом
            if player.rect.colliderect(boss.rect):
                player.rect.x = old_x
            if player.rect.left < 0:
                player.rect.x = 0

        if keys[pygame.K_d]:
            player.rect.x += player.current_speed
            # Проверка столкновения с боссом
            if player.rect.colliderect(boss.rect):
                player.rect.x = old_x
            if player.rect.right > WIDTH:
                player.rect.x = WIDTH - player.rect.width

        if keys[pygame.K_w]:
            player.jump()
        if keys[pygame.K_s]:
            player.crouch()
        else:
            player.stand()

        old_y = player.rect.y
        player.update()
        boss.update(player)

        # Проверка столкновения с боссом по вертикали
        if player.rect.colliderect(boss.rect):
            player.rect.y = old_y
            player.velocity_y = 0
            if old_y < boss.rect.y:
                player.on_ground = True

        # Проверяем попадания снарядов игрока в босса
        for player_projectile in player.projectiles:
            if player_projectile.rect.colliderect(boss.rect):
                if not boss.shield_active:  # Проверяем наличие щита
                    boss.hp -= 10
                player_projectile.kill()
                if boss.hp <= 0:
                    return "victory"

            # Проверяем столкновение с большими снарядами
            for boss_projectile in boss.projectiles:
                if (isinstance(boss_projectile, BigProjectile) and
                        player_projectile.rect.colliderect(boss_projectile.rect)):
                    boss_projectile.check_explosion_damage(boss)
                    boss_projectile.kill()
                    player_projectile.kill()
                    break

        # Отрисовка
        screen.fill(WHITE)

        # Отрисовка подсказок управления
        y_offset = 10
        for key, description in controls_info.items():
            text = font.render(f"{key}: {description}", True, (0, 0, 0))
            screen.blit(text, (WIDTH - 250, y_offset))
            y_offset += 25

        # Отрисовка спрайтов
        for sprite in all_sprites:
            if isinstance(sprite, Player):
                pygame.draw.rect(screen, RED, sprite.rect)
                player.draw_effect_icons(screen)
            elif isinstance(sprite, Boss):
                boss.draw(screen)
            else:
                screen.blit(sprite.image, sprite.rect)

        boss.projectiles.draw(screen)
        boss.vertical_beams.draw(screen)
        player.projectiles.draw(screen)
        boss.wave_segments.draw(screen)
        boss.slow_fields.draw(screen)
        boss.acid_pools.draw(screen)

        # Отображение HP
        hp_text = font.render(f'HP: {player.hp}', True, (0, 0, 0))
        screen.blit(hp_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)


def main():
    while True:
        result = test_game()
        if result == "quit":
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
