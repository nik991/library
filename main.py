import pygame
import random
import sys

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Космический захватчик")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Игрок
player_width = 50
player_height = 30
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 20
player_speed = 5

# Пули
bullets = []
bullet_speed = 7
bullet_width = 5
bullet_height = 15

# Враги
enemies = []
enemy_width = 40
enemy_height = 40
enemy_speed = 2
enemy_drop = 20
enemy_spawn_rate = 30

# Игровые переменные
score = 0
game_over = False
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

def draw_player(x, y):
    pygame.draw.rect(screen, GREEN, (x, y, player_width, player_height))
    # Нос корабля
    pygame.draw.polygon(screen, GREEN, [(x + player_width // 2, y - 10), 
                                        (x + 10, y), 
                                        (x + player_width - 10, y)])

def draw_bullet(x, y):
    pygame.draw.rect(screen, WHITE, (x, y, bullet_width, bullet_height))

def draw_enemy(x, y):
    pygame.draw.rect(screen, RED, (x, y, enemy_width, enemy_height))
    # Глаза врага
    pygame.draw.circle(screen, BLACK, (x + 10, y + 15), 5)
    pygame.draw.circle(screen, BLACK, (x + enemy_width - 10, y + 15), 5)

def show_score():
    score_text = font.render(f"Счет: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

def show_game_over():
    game_over_text = font.render("ИГРА ОКОНЧЕНА! Нажмите R для рестарта", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - 250, HEIGHT // 2))

def reset_game():
    global player_x, player_y, bullets, enemies, score, game_over
    player_x = WIDTH // 2 - player_width // 2
    player_y = HEIGHT - player_height - 20
    bullets = []
    enemies = []
    score = 0
    game_over = False

# Основной игровой цикл
running = True
while running:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                reset_game()
            if event.key == pygame.K_SPACE and not game_over:
                # Создание новой пули
                bullet_x = player_x + player_width // 2 - bullet_width // 2
                bullet_y = player_y
                bullets.append([bullet_x, bullet_y])
    
    if not game_over:
        # Управление игроком
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
            player_x += player_speed
        
        # Движение пуль
        for bullet in bullets[:]:
            bullet[1] -= bullet_speed
            if bullet[1] < 0:
                bullets.remove(bullet)
        
        # Создание врагов
        if random.randint(1, enemy_spawn_rate) == 1:
            enemy_x = random.randint(0, WIDTH - enemy_width)
            enemy_y = 0
            enemies.append([enemy_x, enemy_y])
        
        # Движение врагов
        for enemy in enemies[:]:
            enemy[1] += enemy_speed
            
            # Проверка столкновения врага с игроком
            if (player_x < enemy[0] + enemy_width and
                player_x + player_width > enemy[0] and
                player_y < enemy[1] + enemy_height and
                player_y + player_height > enemy[1]):
                game_over = True
            
            # Проверка выхода за границы
            if enemy[1] > HEIGHT:
                enemies.remove(enemy)
                score -= 10  # Штраф за пропущенного врага
                if score < 0:
                    score = 0
        
        # Проверка столкновений пуль с врагами
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if (bullet[0] < enemy[0] + enemy_width and
                    bullet[0] + bullet_width > enemy[0] and
                    bullet[1] < enemy[1] + enemy_height and
                    bullet[1] + bullet_height > enemy[1]):
                    
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 100
                    break
    
    # Отрисовка игровых объектов
    draw_player(player_x, player_y)
    
    for bullet in bullets:
        draw_bullet(bullet[0], bullet[1])
    
    for enemy in enemies:
        draw_enemy(enemy[0], enemy[1])
    
    show_score()
    
    if game_over:
        show_game_over()
    
    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
