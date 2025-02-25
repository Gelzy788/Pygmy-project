import pygame
import random
from boss_fight.settings import WIDTH, HEIGHT, WHITE, RED, FPS, screen
from boss_fight.boss_fight_player import Player
from boss_fight.boss import Boss
from boss_fight.projectile import BigProjectile
from boss_fight.utils import draw_death_menu
from boss_fight.boss_script_manager import BossScriptManager


def draw_death_menu(screen):
    # Затемнение экрана
    dark = pygame.Surface(screen.get_size()).convert_alpha()
    dark.fill((0, 0, 0, 128))  # Полупрозрачный черный
    screen.blit(dark, (0, 0))

    # Текст "GAME OVER"
    font = pygame.font.Font(None, 74)
    text = font.render('GAME OVER', True, RED)
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
    screen.blit(text, text_rect)

    # Подсказки управления
    small_font = pygame.font.Font(None, 36)
    restart_text = small_font.render('Нажмите R для перезапуска', True, WHITE)
    quit_text = small_font.render('Нажмите Q для выхода', True, WHITE)

    restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 30))
    quit_rect = quit_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 70))

    screen.blit(restart_text, restart_rect)
    screen.blit(quit_text, quit_rect)


def scripted_boss_fight(script_name="default_fight"):
    all_sprites = pygame.sprite.Group()
    clock = pygame.time.Clock()
    player = Player(all_sprites)
    boss = Boss(all_sprites)
    script_manager = BossScriptManager()

    if not script_manager.load_script(script_name):
        return "quit"

    shield_sequence = script_manager.get_shield_sequence()
    attack_sequence = script_manager.get_attack_sequence()
    random_attacks = script_manager.get_random_attack_config()

    shield_index = 0
    attack_index = 0
    last_random_attack_time = 0

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

                keys = pygame.key.get_pressed()
                if keys[pygame.K_r]:  # Перезапуск
                    return "restart"
                if keys[pygame.K_q]:  # Выход
                    return "quit"

                # Отрисовка текущего состояния игры
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
                boss.slow_fields.draw(screen)
                boss.acid_pools.draw(screen)

                # Отрисовка меню смерти поверх игры
                draw_death_menu(screen)
                pygame.display.flip()
                clock.tick(FPS)

        # Обработка щита
        if shield_index < len(shield_sequence):
            shield_event = shield_sequence[shield_index]
            if frame_counter == shield_event["time"]:
                boss.activate_shield()
            elif frame_counter == shield_event["time"] + shield_event["duration"]:
                boss.deactivate_shield()
                shield_index += 1

        # Обработка атак по скрипту
        if attack_index < len(attack_sequence):
            attack_event = attack_sequence[attack_index]
            if frame_counter == attack_event["time"]:
                attack_type = attack_event["type"]
                if attack_type == "BigProjectile":
                    boss.BigProjectileAttack(player)
                elif attack_type == "Wave":
                    boss.WaveAttack()
                elif attack_type == "VerticalBeam":
                    boss.VerticalBeamAttack(player.rect.centerx)
                elif attack_type == "Attraction":
                    boss.AttractionAttack(player)
                elif attack_type == "SlowField":
                    boss.SlowFieldAttack(
                        player.rect.centerx, player.rect.centery)
                elif attack_type == "AcidPool":
                    boss.AcidPoolAttack(player.rect.centerx)
                attack_index += 1

        # Случайные атаки
        if random_attacks and random_attacks["enabled"]:
            current_time = frame_counter
            if current_time - last_random_attack_time >= random_attacks["min_delay"]:
                if random.randint(0, random_attacks["max_delay"] - random_attacks["min_delay"]) == 0:
                    attack_type = random.choice(random_attacks["types"])
                    if attack_type == "BigProjectile":
                        boss.BigProjectileAttack(player)
                    elif attack_type == "Wave":
                        boss.WaveAttack()
                    elif attack_type == "VerticalBeam":
                        boss.VerticalBeamAttack(player.rect.centerx)
                    elif attack_type == "Attraction":
                        boss.AttractionAttack(player)
                    elif attack_type == "SlowField":
                        boss.SlowFieldAttack(
                            player.rect.centerx, player.rect.centery)
                    elif attack_type == "AcidPool":
                        boss.AcidPoolAttack(player.rect.centerx)
                    last_random_attack_time = current_time

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
