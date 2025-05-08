import pygame
import random
import json
import os


class Player:
    """Класс игрока (космического корабля)"""
    
    def __init__(self, x, y):
        """Инициализация игрока"""
        self.x = x
        self.y = y
        self.width = 50
        self.height = 30
        self.speed = 5
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((0, 255, 0))
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.explosion_frames = []
        self.load_explosion()
        self.exploding = False
        self.explosion_index = 0
        self.explosion_counter = 0
        
    def load_explosion(self):
        """Загрузка анимации взрыва"""
        colors = [(255, 255, 0), (255, 165, 0), (255, 0, 0)]
        for color in colors:
            frame = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
            pygame.draw.circle(frame, color, (self.width // 2 + 10, self.height // 2 + 10), 15)
            self.explosion_frames.append(frame)
    
    def update(self, keys):
        """Обновление позиции игрока"""
        if not self.exploding:
            if keys[pygame.K_LEFT] and self.x > 0:
                self.x -= self.speed
            if keys[pygame.K_RIGHT] and self.x < 800 - self.width:
                self.x += self.speed
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        """Отрисовка игрока на экране"""
        if not self.exploding:
            # Рисуем нос корабля
            pygame.draw.polygon(screen, (0, 255, 0), [
                (self.x + self.width // 2, self.y - 10),
                (self.x + 10, self.y),
                (self.x + self.width - 10, self.y)
            ])
            screen.blit(self.image, (self.x, self.y))
        elif self.explosion_index < len(self.explosion_frames):
            # Анимация взрыва
            screen.blit(self.explosion_frames[self.explosion_index], 
                       (self.x - 10, self.y - 10))
            self.explosion_counter += 1
            if self.explosion_counter >= 10:
                self.explosion_index += 1
                self.explosion_counter = 0
    
    def explode(self):
        """Запуск анимации взрыва"""
        self.exploding = True
    
    def reset(self, x, y):
        """Сброс состояния игрока"""
        self.x = x
        self.y = y
        self.exploding = False
        self.explosion_index = 0
        self.explosion_counter = 0
        self.rect = pygame.Rect(x, y, self.width, self.height)


class Bullet:
    """Класс пули"""
    
    def __init__(self, x, y):
        """Инициализация пули"""
        self.x = x
        self.y = y
        self.width = 5
        self.height = 15
        self.speed = 7
        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def update(self):
        """Обновление позиции пули"""
        self.y -= self.speed
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        """Отрисовка пули"""
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.width, self.height))


class Enemy:
    """Класс врага"""
    
    def __init__(self, x, y):
        """Инициализация врага"""
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.speed = 2
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.animation_frames = []
        self.current_frame = 0
        self.animation_counter = 0
        self.load_animation()
    
    def load_animation(self):
        """Загрузка анимации врага"""
        colors = [(255, 0, 0), (200, 0, 0), (150, 0, 0)]
        for color in colors:
            frame = pygame.Surface((self.width, self.height))
            frame.fill(color)
            # Рисуем глаза врага
            pygame.draw.circle(frame, (0, 0, 0), (10, 15), 5)
            pygame.draw.circle(frame, (0, 0, 0), (30, 15), 5)
            self.animation_frames.append(frame)
    
    def update(self):
        """Обновление позиции и анимации врага"""
        self.y += self.speed
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Обновление анимации
        self.animation_counter += 1
        if self.animation_counter >= 15:
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.animation_counter = 0
    
    def draw(self, screen):
        """Отрисовка врага"""
        screen.blit(self.animation_frames[self.current_frame], (self.x, self.y))


class GameState:
    """Класс для хранения состояния игры"""
    
    def __init__(self):
        """Инициализация состояния игры"""
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.load_high_score()
    
    def load_high_score(self):
        """Загрузка рекорда из файла"""
        if os.path.exists('highscore.json'):
            with open('highscore.json', 'r') as file:
                data = json.load(file)
                self.high_score = data.get('high_score', 0)
    
    def save_high_score(self):
        """Сохранение рекорда в файл"""
        data = {'high_score': self.high_score}
        with open('highscore.json', 'w') as file:
            json.dump(data, file)
    
    def update_high_score(self):
        """Обновление рекорда"""
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
    
    def increase_level(self):
        """Увеличение уровня"""
        self.level += 1
    
    def reset(self):
        """Сброс состояния игры"""
        self.score = 0
        self.level = 1


class Explosion:
    """Класс анимации взрыва"""
    
    def __init__(self, x, y):
        """Инициализация взрыва"""
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = 30
        self.growing = True
        self.color_index = 0
        self.colors = [(255, 255, 0), (255, 165, 0), (255, 0, 0)]
    
    def update(self):
        """Обновление анимации взрыва"""
        if self.growing:
            self.radius += 2
            if self.radius >= self.max_radius:
                self.growing = False
        else:
            self.radius -= 2
            self.color_index = (self.color_index + 1) % len(self.colors)
    
    def draw(self, screen):
        """Отрисовка взрыва"""
        pygame.draw.circle(screen, self.colors[self.color_index], 
                          (self.x, self.y), self.radius)
    
    def is_complete(self):
        """Проверка завершения анимации"""
        return self.radius <= 0 and not self.growing
