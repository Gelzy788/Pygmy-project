import pygame
import random
from settings import WIDTH, WHITE, RED, FPS, screen
from boss_fight_player import Player
from boss import Boss
from projectile import BigProjectile
from utils import draw_death_menu


def scripted_boss_fight():
    all_sprites = pygame.sprite.Group()
    clock = pygame.time.Clock()
    player = Player(all_sprites)
    boss = Boss(all_sprites)

    # Упрощенный скрипт с щитом
    shield_sequence = [
        {"time": 180, "action": "activate"},   # 3 сек - включить щит
        {"time": 300, "action": "deactivate"},  # 5 сек - выключить щит
        {"time": 420, "action": "activate"},   # 7 сек - снова включить
        {"time": 540, "action": "deactivate"},  # 9 сек - снова выключить
    ]

    attack_sequence = [
        {"time": 180, "attack": "attraction"},
        {"time": 300, "attack": "wave"},
        {"time": 420, "attack": "big"},
        {"time": 540, "attack": "vertical"},
    ]

    frame_counter = 0
    mouse_x, mouse_y = 400, 300

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

                draw_death_menu(screen)
                pygame.display.flip()
                clock.tick(FPS)

        # Проверяем последовательность щита
        for shield_action in shield_sequence:
            if frame_counter == shield_action["time"]:
                if shield_action["action"] == "activate":
                    boss.activate_shield()
                else:
                    boss.deactivate_shield()

        # Проверяем заскриптованные атаки
        for attack in attack_sequence:
            if frame_counter == attack["time"]:
                if attack["attack"] == "attraction":
                    boss.AttractionAttack(player)
                elif attack["attack"] == "wave":
                    boss.WaveAttack()
                elif attack["attack"] == "big":
                    boss.BigProjectileAttack(player)
                elif attack["attack"] == "vertical":
                    boss.VerticalBeamAttack(mouse_x)

        # Случайные атаки после заскриптованной последовательности
        if frame_counter > 720:  # После 12 секунд
            if random.randint(0, 180) == 0:  # Примерно раз в 3 секунды
                attack_type = random.choice(
                    ["attraction", "wave", "big", "vertical", "shield"])
                if attack_type == "attraction":
                    boss.AttractionAttack(player)
                elif attack_type == "wave":
                    boss.WaveAttack()
                elif attack_type == "big":
                    boss.BigProjectileAttack(player)
                elif attack_type == "vertical":
                    x = random.randint(100, 700)  # Случайная позиция по X
                    boss.VerticalBeamAttack(x)
                elif attack_type == "shield":
                    boss.activate_shield()

        frame_counter += 1

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
            elif isinstance(sprite, Boss):
                boss.draw(screen)
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
                if not boss.shield_active:
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

        pygame.display.flip()
        clock.tick(FPS)


def main():
    while True:
        result = scripted_boss_fight()
        if result == "quit":
            break
        elif result == "victory":
            # Показываем экран победы
            pass

    pygame.quit()


if __name__ == "__main__":
    main()
