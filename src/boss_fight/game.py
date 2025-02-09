import pygame
import random
from settings import WIDTH, WHITE, RED, FPS, screen
from boss_fight_player import Player
from boss import Boss
from projectile import BigProjectile
from utils import draw_death_menu
from boss_script_manager import BossScriptManager


def scripted_boss_fight(script_name="default_fight"):
    all_sprites = pygame.sprite.Group()
    clock = pygame.time.Clock()
    player = Player(all_sprites)
    boss = Boss(all_sprites)

    # Загружаем скрипт боя
    script_manager = BossScriptManager()
    if not script_manager.load_script(script_name):
        print(f"Error: Script '{script_name}' not found!")
        return "quit"

    shield_sequence = script_manager.get_shield_sequence()
    attack_sequence = script_manager.get_attack_sequence()
    random_attacks = script_manager.get_random_attack_config()

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
                        player.draw_effect_icons(screen)
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
                if attack["attack"] == "slow_field":
                    # Создаем поле в случайной точке рядом с игроком
                    target_x = player.rect.centerx + random.randint(-100, 100)
                    target_y = player.rect.centery + random.randint(-100, 100)
                    boss.SlowFieldAttack(target_x, target_y)
                elif attack["attack"] == "attraction":
                    boss.AttractionAttack(player)
                elif attack["attack"] == "wave":
                    boss.WaveAttack()
                elif attack["attack"] == "big":
                    boss.BigProjectileAttack(player)
                elif attack["attack"] == "vertical":
                    boss.VerticalBeamAttack(mouse_x)
                elif attack["attack"] == "acid_pool":
                    target_x = player.rect.centerx
                    boss.AcidPoolAttack(target_x)

        # Случайные атаки после заскриптованной последовательности
        if random_attacks and frame_counter > random_attacks["start_time"]:
            if random.randint(0, random_attacks["interval"]) == 0:
                attack_type = random.choice(random_attacks["attacks"])
                if attack_type == "attraction":
                    boss.AttractionAttack(player)
                elif attack_type == "wave":
                    boss.WaveAttack()
                elif attack_type == "big":
                    boss.BigProjectileAttack(player)
                elif attack_type == "vertical":
                    x = random.randint(100, 700)
                    boss.VerticalBeamAttack(x)
                elif attack_type == "shield":
                    boss.activate_shield()
                elif attack_type == "slow_field":
                    target_x = player.rect.centerx + random.randint(-100, 100)
                    target_y = player.rect.centery + random.randint(-100, 100)
                    boss.SlowFieldAttack(target_x, target_y)
                elif attack_type == "acid_pool":
                    target_x = player.rect.centerx
                    boss.AcidPoolAttack(target_x)

        frame_counter += 1

        old_x = player.rect.x

        if keys[pygame.K_a]:
            player.rect.x -= player.current_speed
            for sprite in all_sprites:
                if sprite != player and player.rect.colliderect(sprite.rect):
                    player.rect.x = old_x
                    break
            if player.rect.left < 0:
                player.rect.x = 0

        if keys[pygame.K_d]:
            player.rect.x += player.current_speed
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
                player.draw_effect_icons(screen)
            elif isinstance(sprite, Boss):
                boss.draw(screen)
            else:
                screen.blit(sprite.image, sprite.rect)

        boss.projectiles.draw(screen)
        boss.vertical_beams.draw(screen)
        player.projectiles.draw(screen)
        boss.wave_segments.draw(screen)

        # Отрисовка замедляющих полей
        boss.slow_fields.draw(screen)

        # Отрисовка луж
        boss.acid_pools.draw(screen)

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
        # Можно выбирать разные скрипты боя
        result = scripted_boss_fight("aggressive_fight")
        if result == "quit":
            break
        elif result == "victory":
            # Показываем экран победы
            pass

    pygame.quit()


if __name__ == "__main__":
    main()
