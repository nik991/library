import pygame
import random
import sys
from game_objects import Player, Bullet, Enemy, GameState, Explosion


def main():
    """Основная функция игры"""
    
    # Инициализация Pygame
    pygame.init()
    pygame.mixer.init()

    # Настройки экрана
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Космический захватчик: Продвинутая версия")

    # Цвета
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)

    # Игровые объекты
    player = Player(WIDTH // 2 - 25, HEIGHT - 50)
    bullets = []
    enemies = []
    explosions = []
    game_state = GameState()

    # Игровые переменные
    game_over = False
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    big_font = pygame.font.SysFont(None, 72)
    enemy_spawn_rate = 30
    last_spawn_time = 0
    spawn_interval = 1000  # миллисекунды

    # Загрузка звуков
    try:
        shoot_sound = pygame.mixer.Sound('shoot.wav')
        explosion_sound = pygame.mixer.Sound('explosion.wav')
        game_over_sound = pygame.mixer.Sound('game_over.wav')
    except FileNotFoundError:
        # Создание заглушек, если файлы не найдены
        shoot_sound = pygame.mixer.Sound(buffer=bytearray(100))
        explosion_sound = pygame.mixer.Sound(buffer=bytearray(100))
        game_over_sound = pygame.mixer.Sound(buffer=bytearray(100))

    def spawn_enemy():
        """Создание нового врага"""
        enemy_x = random.randint(0, WIDTH - 40)
        enemy_y = 0
        enemies.append(Enemy(enemy_x, enemy_y))

    def show_game_info():
        """Отображение игровой информации"""
        score_text = font.render(f"Счет: {game_state.score}", True, WHITE)
        high_score_text = font.render(f"Рекорд: {game_state.high_score}", True, WHITE)
        level_text = font.render(f"Уровень: {game_state.level}", True, WHITE)
        
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 50))
        screen.blit(level_text, (10, 90))

    def show_game_over():
        """Отображение экрана завершения игры"""
        game_over_text = big_font.render("ИГРА ОКОНЧЕНА", True, RED)
        restart_text = font.render("Нажмите R для рестарта", True, WHITE)
        final_score_text = font.render(f"Финальный счет: {game_state.score}", True, WHITE)
        
        screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2 - 100))
        screen.blit(final_score_text, (WIDTH // 2 - 100, HEIGHT // 2))
        screen.blit(restart_text, (WIDTH // 2 - 120, HEIGHT // 2 + 50))

    def show_level_start():
        """Отображение сообщения о начале уровня"""
        level_text = big_font.render(f"Уровень {game_state.level}", True, GREEN)
        screen.blit(level_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
        pygame.display.update()
        pygame.time.delay(1500)

    def reset_game():
        """Сброс игры для начала заново"""
        nonlocal bullets, enemies, explosions, game_over, enemy_spawn_rate, last_spawn_time
        
        player.reset(WIDTH // 2 - 25, HEIGHT - 50)
        bullets = []
        enemies = []
        explosions = []
        game_over = False
        enemy_spawn_rate = max(10, 30 - (game_state.level * 2))
        last_spawn_time = pygame.time.get_ticks()
        game_state.reset()
        show_level_start()

    def check_collisions():
        """Проверка столкновений"""
        nonlocal game_over
        
        # Столкновения пуль с врагами
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    explosions.append(Explosion(
                        enemy.x + enemy.width // 2, 
                        enemy.y + enemy.height // 2
                    ))
                    explosion_sound.play()
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    game_state.score += 100 * game_state.level
                    
                    # Проверка перехода на новый уровень
                    if game_state.score >= game_state.level * 1000:
                        game_state.increase_level()
                        reset_game()
                    break
        
        # Столкновения игрока с врагами
        for enemy in enemies[:]:
            if player.rect.colliderect(enemy.rect) and not player.exploding:
                player.explode()
                explosions.append(Explosion(
                    player.x + player.width // 2, 
                    player.y + player.height // 2
                ))
                explosion_sound.play()
                game_over_sound.play()
                game_state.update_high_score()
                game_over = True
            
            # Враги за пределами экрана
            if enemy.y > HEIGHT:
                enemies.remove(enemy)
                game_state.score = max(0, game_state.score - 10)

    # Основной игровой цикл
    running = True
    show_level_start()

    while running:
        current_time = pygame.time.get_ticks()
        
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    reset_game()
                if event.key == pygame.K_SPACE and not game_over and not player.exploding:
                    bullets.append(Bullet(player.x + player.width // 2 - 2, player.y))
                    shoot_sound.play()
        
        # Создание врагов
        if not game_over and current_time - last_spawn_time > spawn_interval:
            if random.randint(1, enemy_spawn_rate) == 1:
                spawn_enemy()
                last_spawn_time = current_time
        
        # Обновление игровых объектов
        if not game_over:
            keys = pygame.key.get_pressed()
            player.update(keys)
            
            for bullet in bullets[:]:
                bullet.update()
                if bullet.y < 0:
                    bullets.remove(bullet)
            
            for enemy in enemies:
                enemy.update()
            
            for explosion in explosions[:]:
                explosion.update()
                if explosion.is_complete():
                    explosions.remove(explosion)
            
            check_collisions()
        
        # Отрисовка
        screen.fill(BLACK)
        
        # Отрисовка звёздного фона
        for _ in range(5):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            pygame.draw.circle(screen, WHITE, (x, y), 1)
        
        player.draw(screen)
        
        for bullet in bullets:
            bullet.draw(screen)
        
        for enemy in enemies:
            enemy.draw(screen)
        
        for explosion in explosions:
            explosion.draw(screen)
        
        show_game_info()
        
        if game_over:
            show_game_over()
        
        pygame.display.update()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
