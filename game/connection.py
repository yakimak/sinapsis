import pygame
import math
import time
import random

class Connection:
    def __init__(self, node1, node2, connection_type="normal", duration=None):
        self.node1 = node1
        self.node2 = node2
        self.type = connection_type
        self.color = self.get_color()
        self.width = 3 if connection_type == "normal" else 5
        self.distance = self.calculate_distance()
        self.created_time = time.time()
        self.duration = duration  # Для временных связей
        self.animation_time = 0.0
        self.particles = []
        
    def calculate_distance(self):
        return ((self.node1.x - self.node2.x) ** 2 + (self.node1.y - self.node2.y) ** 2) ** 0.5
        
    def is_too_long(self):
        # Максимальная длина связи - 250 пикселей
        return self.distance > 250
    
    def is_expired(self):
        """Проверяет, истекла ли временная связь"""
        if self.duration is None:
            return False
        return time.time() - self.created_time > self.duration
    
    def get_time_remaining(self):
        """Возвращает оставшееся время для временной связи"""
        if self.duration is None:
            return None
        return max(0, self.duration - (time.time() - self.created_time))
        
    def get_color(self):
        colors = {
            "normal": (0, 255, 0),
            "enhanced": (0, 200, 255),
            "temporary": (255, 200, 0),
            "firewall": (100, 200, 255),
            "invalid": (255, 0, 0)  # Для слишком длинных связей
        }
        return colors.get(self.type, (0, 255, 0))
    
    def update(self, dt):
        """Обновляет анимацию связи"""
        self.animation_time += dt / 1000.0
        
        # Обновляем частицы
        for particle in self.particles[:]:
            particle['life'] -= dt / 1000.0 * 3
            particle['x'] += particle.get('vx', 0) * dt / 16.0
            particle['y'] += particle.get('vy', 0) * dt / 16.0
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
        # Создаем новые частицы для активных связей
        if self.type in ["enhanced", "normal"] and len(self.particles) < 5:
            self.create_particle()

    def create_particle(self):
        """Создает частицу, движущуюся по связи"""
        t = random.uniform(0, 1) if hasattr(self, '_last_t') else 0
        self._last_t = (t + 0.1) % 1.0
        
        x = self.node1.x + (self.node2.x - self.node1.x) * t
        y = self.node1.y + (self.node2.y - self.node1.y) * t
        
        # Направление движения
        dx = self.node2.x - self.node1.x
        dy = self.node2.y - self.node1.y
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            vx = (dx / length) * 2
            vy = (dy / length) * 2
        else:
            vx, vy = 0, 0
        
        self.particles.append({
            'x': x,
            'y': y,
            'vx': vx,
            'vy': vy,
            'color': self.color,
            'size': 3,
            'life': 1.0
        })

    def draw(self, screen):
        # Для временных связей показываем предупреждение
        if self.type == "temporary":
            time_left = self.get_time_remaining()
            if time_left is not None and time_left < 3:
                # Мигание при скором истечении
                blink = (math.sin(self.animation_time * 10) + 1) / 2
                alpha = int(100 + 155 * blink)
                color = (*self.color, alpha)
            else:
                color = self.color
        else:
            color = self.color
        
        # Основная линия с градиентом для усиленных связей
        if self.type == "enhanced":
            self.draw_enhanced_connection(screen)
        elif self.type == "temporary":
            self.draw_temporary_connection(screen)
        else:
            self.draw_normal_connection(screen)
        
        # Рисуем частицы
        for particle in self.particles:
            alpha = int(255 * particle['life'])
            p_color = (*particle['color'][:3], alpha)
            s = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, p_color, (particle['size'], particle['size']), particle['size'])
            screen.blit(s, (particle['x'] - particle['size'], particle['y'] - particle['size']))
    
    def draw_normal_connection(self, screen):
        """Обычная связь с легким свечением"""
        # Свечение
        for i in range(2):
            glow_width = self.width + 2 + i * 2
            alpha = 50 - i * 20
            s = pygame.Surface((900, 700), pygame.SRCALPHA)
            pygame.draw.line(s, (*self.color, alpha), 
                           (self.node1.x, self.node1.y), 
                           (self.node2.x, self.node2.y), 
                           int(glow_width))
            screen.blit(s, (0, 0))
        
        # Основная линия
        pygame.draw.line(screen, self.color, 
                        (self.node1.x, self.node1.y), 
                        (self.node2.x, self.node2.y), 
                        self.width)
    
    def draw_enhanced_connection(self, screen):
        """Усиленная связь с импульсами"""
        # Импульсы, движущиеся по связи
        pulse_pos = (self.animation_time * 0.5) % 1.0
        pulse_x = self.node1.x + (self.node2.x - self.node1.x) * pulse_pos
        pulse_y = self.node1.y + (self.node2.y - self.node1.y) * pulse_pos
        
        # Рисуем импульс
        for i in range(3):
            radius = 5 + i * 3
            alpha = int(200 / (i + 1))
            s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (radius, radius), radius)
            screen.blit(s, (pulse_x - radius, pulse_y - radius))
        
        # Основная линия с градиентом
        self.draw_gradient_line(screen, self.node1, self.node2, self.color, self.width)
    
    def draw_temporary_connection(self, screen):
        """Временная связь с таймером"""
        time_left = self.get_time_remaining()
        
        # Пунктирная линия
        self.draw_dashed_line(screen, self.node1, self.node2, self.color, self.width)
        
        # Индикатор времени в середине связи
        if time_left is not None:
            mid_x = (self.node1.x + self.node2.x) / 2
            mid_y = (self.node1.y + self.node2.y) / 2
            
            # Фон для текста
            font = pygame.font.Font(None, 16)
            time_text = f"{int(time_left)}s"
            text_surf = font.render(time_text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(mid_x, mid_y))
            
            # Фон
            bg_rect = text_rect.inflate(8, 4)
            s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            s.fill((0, 0, 0, 200))
            screen.blit(s, bg_rect)
            screen.blit(text_surf, text_rect)
    
    def draw_dashed_line(self, screen, node1, node2, color, width):
        """Рисует пунктирную линию"""
        dx = node2.x - node1.x
        dy = node2.y - node1.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            return
        
        dash_length = 10
        gap_length = 5
        num_dashes = int(distance / (dash_length + gap_length))
        
        unit_x = dx / distance
        unit_y = dy / distance
        
        for i in range(num_dashes):
            start_t = i * (dash_length + gap_length) / distance
            end_t = (i * (dash_length + gap_length) + dash_length) / distance
            
            start_x = node1.x + dx * start_t
            start_y = node1.y + dy * start_t
            end_x = node1.x + dx * end_t
            end_y = node1.y + dy * end_t
            
            pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), width)
    
    def draw_gradient_line(self, screen, node1, node2, color, width):
        """Рисует линию с градиентом"""
        # Упрощенная версия - просто яркая линия
        pygame.draw.line(screen, color, 
                        (node1.x, node1.y), 
                        (node2.x, node2.y), 
                        width)
        
        # Добавляем свечение
        for i in range(2):
            glow_width = width + 2 + i
            alpha = 80 - i * 30
            s = pygame.Surface((900, 700), pygame.SRCALPHA)
            pygame.draw.line(s, (*color, alpha), 
                           (node1.x, node1.y), 
                           (node2.x, node2.y), 
                           int(glow_width))
            screen.blit(s, (0, 0))