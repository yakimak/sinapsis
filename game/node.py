import pygame
import math
import time

class Node:
    def __init__(self, x, y, type="neutral"):
        self.x = x
        self.y = y
        self.radius = 20
        self.type = type
        self.connected_to = []
        self.selected = False
        self.pulse = 0.0
        self.animation_time = 0.0
        self.particles = []
        
    def update(self, dt):
        # Плавная пульсация для всех узлов
        self.pulse = (self.pulse + dt / 1000.0) % 1.0
        self.animation_time += dt / 1000.0
        
        # Обновляем частицы
        for particle in self.particles[:]:
            particle['life'] -= dt / 1000.0 * 2
            particle['x'] += particle.get('vx', 0) * dt / 16.0
            particle['y'] += particle.get('vy', 0) * dt / 16.0
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
    def draw(self, screen):
        # Вызываем специализированные методы отрисовки
        if self.type == "start":
            self.draw_neural_core(screen)
        elif self.type == "finish":
            self.draw_data_hub(screen)
        elif self.type == "virus":
            self.draw_corrupted_node(screen)
        elif self.type == "firewall":
            self.draw_shield_node(screen)
        elif self.type == "amplifier":
            self.draw_amplifier_node(screen)
        elif self.type == "decoy":
            self.draw_decoy_node(screen)
        elif self.type == "codex":
            self.draw_codex_node(screen)
        else:
            self.draw_neutral_node(screen)
        
        # Обводка для выделенного узла
        if self.selected:
            for i in range(2):
                radius = self.radius + 5 + i * 2
                alpha = 200 - i * 100
                s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 255, 0, alpha), (radius, radius), radius, 2)
                screen.blit(s, (self.x - radius, self.y - radius))
    
    def draw_neural_core(self, screen):
        """Ядро нейросети с анимацией импульсов"""
        base_color = (0, 255, 255)
        pulse = (math.sin(self.animation_time * 3) + 1) / 2
        
        # Внешние кольца с импульсами
        for i in range(8):
            angle = self.animation_time * 2 + i * math.pi / 4
            radius_offset = 25 + math.sin(self.animation_time * 3 + i) * 5
            x = self.x + math.cos(angle) * radius_offset
            y = self.y + math.sin(angle) * radius_offset
            
            # Частицы вокруг ядра
            alpha = int(100 + 155 * pulse)
            s = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(s, (*base_color, alpha), (3, 3), 3)
            screen.blit(s, (x - 3, y - 3))
        
        # Многослойное свечение
        for i in range(4, 0, -1):
            glow_radius = self.radius + i * 4
            alpha = int(50 + 100 * pulse / (i + 1))
            s = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*base_color, alpha), (glow_radius, glow_radius), glow_radius)
            screen.blit(s, (self.x - glow_radius, self.y - glow_radius))
        
        # Основное ядро
        core_radius = int(self.radius + 3 * pulse)
        pygame.draw.circle(screen, base_color, (self.x, self.y), core_radius)
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), core_radius, 2)
        
        # Внутренняя структура
        for i in range(3):
            angle = self.animation_time * 2 + i * 2 * math.pi / 3
            inner_x = self.x + math.cos(angle) * (core_radius * 0.5)
            inner_y = self.y + math.sin(angle) * (core_radius * 0.5)
            pygame.draw.circle(screen, (255, 255, 255), (int(inner_x), int(inner_y)), 3)
    
    def draw_data_hub(self, screen):
        """Хаб данных с вращающимися кольцами"""
        base_color = (0, 100, 255)
        
        # Вращающиеся кольца
        for ring in range(3):
            ring_radius = self.radius + 8 + ring * 6
            rotation = self.animation_time * (1 + ring * 0.5)
            
            # Рисуем кольцо с разрывами
            for i in range(8):
                angle1 = rotation + i * math.pi / 4
                angle2 = rotation + (i + 0.7) * math.pi / 4
                
                x1 = self.x + math.cos(angle1) * ring_radius
                y1 = self.y + math.sin(angle1) * ring_radius
                x2 = self.x + math.cos(angle2) * ring_radius
                y2 = self.y + math.sin(angle2) * ring_radius
                
                pygame.draw.line(screen, base_color, (x1, y1), (x2, y2), 2)
        
        # Центральный хаб
        pygame.draw.circle(screen, base_color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, (200, 200, 255), (self.x, self.y), self.radius - 3)
        
        # Свечение
        pulse = (math.sin(self.animation_time * 2) + 1) / 2
        for i in range(2):
            glow_radius = self.radius + 5 + i * 3
            alpha = int(80 + 100 * pulse)
            s = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*base_color, alpha), (glow_radius, glow_radius), glow_radius, 2)
            screen.blit(s, (self.x - glow_radius, self.y - glow_radius))
    
    def draw_corrupted_node(self, screen):
        """Искаженная геометрия для вирусов"""
        base_color = (255, 0, 0)
        distortion = math.sin(self.animation_time * 4) * 0.3
        
        # Искаженная форма
        points = []
        for i in range(8):
            angle = i * 2 * math.pi / 8 + self.animation_time
            radius_var = self.radius * (1 + distortion * math.sin(angle * 3))
            x = self.x + math.cos(angle) * radius_var
            y = self.y + math.sin(angle) * radius_var
            points.append((int(x), int(y)))
        
        # Рисуем искаженный многоугольник
        if len(points) >= 3:
            pygame.draw.polygon(screen, base_color, points)
        
        # Внутренние шипы
        for i in range(6):
            angle = self.animation_time * 2 + i * math.pi / 3
            spike_length = 8 + math.sin(self.animation_time * 5 + i) * 3
            x1 = self.x + math.cos(angle) * (self.radius - 5)
            y1 = self.y + math.sin(angle) * (self.radius - 5)
            x2 = self.x + math.cos(angle) * (self.radius + spike_length)
            y2 = self.y + math.sin(angle) * (self.radius + spike_length)
            pygame.draw.line(screen, (255, 150, 150), (x1, y1), (x2, y2), 2)
        
        # Пульсирующее свечение
        pulse = (math.sin(self.animation_time * 5) + 1) / 2
        for i in range(3):
            glow_radius = int(self.radius + 5 + i * 4 + pulse * 3)
            alpha = int(100 + 100 * pulse)
            s = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*base_color, alpha), (glow_radius, glow_radius), glow_radius, 2)
            screen.blit(s, (self.x - glow_radius, self.y - glow_radius))
    
    def draw_shield_node(self, screen):
        """Защитный узел с барьерами"""
        base_color = (100, 200, 255)
        
        # Вращающиеся защитные сегменты
        for i in range(6):
            angle = self.animation_time + i * math.pi / 3
            x1 = self.x + math.cos(angle) * self.radius
            y1 = self.y + math.sin(angle) * self.radius
            x2 = self.x + math.cos(angle) * (self.radius + 10)
            y2 = self.y + math.sin(angle) * (self.radius + 10)
            pygame.draw.line(screen, base_color, (x1, y1), (x2, y2), 3)
        
        # Центральный узел
        pygame.draw.circle(screen, base_color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, (200, 230, 255), (self.x, self.y), self.radius - 2)
        
        # Защитное кольцо
        for i in range(2):
            ring_radius = self.radius + 12 + i * 3
            alpha = 150 - i * 50
            s = pygame.Surface((ring_radius * 2, ring_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*base_color, alpha), (ring_radius, ring_radius), ring_radius, 2)
            screen.blit(s, (self.x - ring_radius, self.y - ring_radius))
    
    def draw_amplifier_node(self, screen):
        """Усилитель с волнами"""
        base_color = (255, 200, 0)
        
        # Расходящиеся волны
        for wave in range(3):
            wave_radius = self.radius + 5 + wave * 8 + math.sin(self.animation_time * 2) * 3
            alpha = int(150 / (wave + 1))
            s = pygame.Surface((int(wave_radius * 2), int(wave_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*base_color, alpha), (int(wave_radius), int(wave_radius)), int(wave_radius), 2)
            screen.blit(s, (self.x - wave_radius, self.y - wave_radius))
        
        # Центр
        pygame.draw.circle(screen, base_color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, (255, 255, 150), (self.x, self.y), self.radius - 2)
        
        # Внутренние линии
        for i in range(4):
            angle = self.animation_time + i * math.pi / 2
            x = self.x + math.cos(angle) * (self.radius * 0.6)
            y = self.y + math.sin(angle) * (self.radius * 0.6)
            pygame.draw.line(screen, (255, 255, 200), (self.x, self.y), (x, y), 2)
    
    def draw_decoy_node(self, screen):
        """Приманка с миганием"""
        base_color = (150, 150, 255)
        blink = (math.sin(self.animation_time * 4) + 1) / 2
        
        # Мигающий эффект
        alpha = int(100 + 155 * blink)
        s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*base_color, alpha), (self.radius, self.radius), self.radius)
        screen.blit(s, (self.x - self.radius, self.y - self.radius))
        
        # Пунктирная обводка
        for i in range(8):
            angle = i * math.pi / 4
            if i % 2 == 0:
                x = self.x + math.cos(angle) * (self.radius + 3)
                y = self.y + math.sin(angle) * (self.radius + 3)
                pygame.draw.circle(screen, base_color, (int(x), int(y)), 2)
    
    def draw_codex_node(self, screen):
        """Кодекс - узел, требующий активации"""
        base_color = (200, 100, 255)
        pulse = (math.sin(self.animation_time * 2) + 1) / 2
        
        # Вращающиеся символы
        for i in range(6):
            angle = self.animation_time * 1.5 + i * math.pi / 3
            x = self.x + math.cos(angle) * (self.radius + 5)
            y = self.y + math.sin(angle) * (self.radius + 5)
            pygame.draw.circle(screen, base_color, (int(x), int(y)), 2)
        
        # Центр
        pygame.draw.circle(screen, base_color, (self.x, self.y), self.radius)
        
        # Внутренний символ
        font = pygame.font.Font(None, 20)
        text = font.render("?", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)
    
    def draw_neutral_node(self, screen):
        """Обычный нейтральный узел"""
        base_color = (200, 200, 200)
        pulse = (math.sin(self.animation_time * 2) + 1) / 2
        
        # Легкое свечение
        if self.selected:
            for i in range(2):
                glow_radius = self.radius + 3 + i * 2
                alpha = int(80 + 80 * pulse)
                s = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*base_color, alpha), (glow_radius, glow_radius), glow_radius)
                screen.blit(s, (self.x - glow_radius, self.y - glow_radius))
        
        # Основной круг
        pygame.draw.circle(screen, base_color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.radius, 1)
    
    def is_clicked(self, pos):
        distance = ((self.x - pos[0]) ** 2 + (self.y - pos[1]) ** 2) ** 0.5
        return distance <= self.radius