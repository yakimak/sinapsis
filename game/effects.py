import pygame
import random

class EffectManager:
    def __init__(self):
        self.particles = []
        
    def add_connection_effect(self, node1, node2, connection_type):
        """Добавляет эффект создания связи"""
        color = (0, 255, 0) if connection_type == "normal" else (0, 200, 255)
        
        # Создаем частицы вдоль линии
        points = self.calculate_line_points(node1.x, node1.y, node2.x, node2.y, 20)
        
        for point in points:
            self.particles.append({
                'x': point[0],
                'y': point[1],
                'color': color,
                'size': random.randint(2, 5),
                'life': 1.0,
                'max_life': 1.0,
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-1, 1)
            })
            
    def calculate_line_points(self, x1, y1, x2, y2, num_points):
        """Вычисляет точки вдоль линии"""
        points = []
        for i in range(num_points):
            t = i / (num_points - 1)
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t
            points.append((x, y))
        return points
        
    def update(self, dt):
        """Обновляет все эффекты"""
        for particle in self.particles[:]:
            particle['life'] -= dt / 1000.0
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['size'] *= 0.95
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
                
    def draw(self, screen):
        """Отрисовывает все эффекты"""
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / particle['max_life']))
            color = (*particle['color'][:3], alpha)
            
            surf = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (particle['size'], particle['size']), particle['size'])
            screen.blit(surf, (particle['x'] - particle['size'], particle['y'] - particle['size']))