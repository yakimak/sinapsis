import pygame
import random
import math

class Silence:
    def __init__(self):
        self.wave_timer = 0
        self.wave_interval = 30000
        self.wave_active = False
        self.wave_progress = 0.0
        self.particles = []
        self.next_wave_time = 0
        self.reset()
        
    def reset(self):
        """Сброс состояния при загрузке нового уровня"""
        self.wave_timer = 0
        self.wave_active = False
        self.wave_progress = 0.0
        self.particles = []
        self.next_wave_time = self.wave_interval
        
    def update(self, connections, nodes, dt):
        self.wave_timer += dt
        
        if self.wave_timer >= self.next_wave_time and not self.wave_active:
            self.start_wave()
            self.wave_timer = 0
            # Случайный интервал между волнами (25-35 секунд)
            self.next_wave_time = random.randint(25000, 35000)
            
        if self.wave_active:
            self.wave_progress += 0.015
            self.update_particles(dt)
            
            if self.wave_progress >= 1.0:
                self.wave_active = False
                self.destroy_normal_connections(connections)
                self.wave_progress = 0.0
                
    def start_wave(self):
        self.wave_active = True
        self.wave_progress = 0.0
        self.create_wave_particles()
        
    def create_wave_particles(self):
        """Создает частицы для волны"""
        for i in range(50):
            self.particles.append({
                'x': random.randint(0, 900),
                'y': 700,
                'size': random.randint(3, 8),
                'vx': 0,  # Горизонтальная скорость
                'vy': -random.uniform(2, 5),  # Вертикальная скорость (вверх)
                'color': (150, 0, 0, 150),
                'life': 1.0
            })
            
    def update_particles(self, dt):
        """Обновляет частицы волны"""
        for particle in self.particles[:]:
            # Обновляем позицию с учетом скорости
            particle['x'] += particle.get('vx', 0)
            particle['y'] += particle.get('vy', 0)
            particle['life'] -= 0.02
            
            if particle['life'] <= 0 or particle['y'] < 0:
                self.particles.remove(particle)
                
    def destroy_normal_connections(self, connections):
        connections_to_remove = []
        for connection in connections:
            if connection.type == "normal":
                connections_to_remove.append(connection)
                # Эффект разрушения связи
                self.create_break_effect(connection)
                
        for connection in connections_to_remove:
            connections.remove(connection)
            
    def create_break_effect(self, connection):
        """Эффект разрыва связи"""
        x1, y1 = connection.node1.x, connection.node1.y
        x2, y2 = connection.node2.x, connection.node2.y
        
        for i in range(10):
            t = i / 10.0
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t
            
            self.particles.append({
                'x': x,
                'y': y,
                'size': random.randint(2, 4),
                'vx': random.uniform(-2, 2),  # Используем vx вместо speed_x
                'vy': random.uniform(-2, 2),  # Используем vy вместо speed_y
                'color': (255, 100, 100, 200),
                'life': 1.0
            })
                
    def draw(self, screen, width, height):
        # Полоса прогресса волны (красная)
        progress = min(1.0, self.wave_timer / self.next_wave_time)
        bar_width = int(width * progress)
        
        # Фон полосы
        pygame.draw.rect(screen, (50, 0, 0), (0, height - 15, width, 15))
        # Прогресс
        pygame.draw.rect(screen, (200, 0, 0), (0, height - 15, bar_width, 15))
        # Контур
        pygame.draw.rect(screen, (100, 100, 100), (0, height - 15, width, 15), 1)
        
        # Текст
        font = pygame.font.Font(None, 20)
        time_left = (self.next_wave_time - self.wave_timer) // 1000
        text = font.render(f"Волна через: {time_left}с", True, (255, 255, 255))
        screen.blit(text, (10, height - 30))
        
        # Анимация волны
        if self.wave_active:
            self.draw_wave(screen, width, height)
            
    def draw_wave(self, screen, width, height):
        """Рисует анимированную волну"""
        wave_height = int(height * self.wave_progress)
        
        if wave_height <= 0:
            return
            
        # Создаем поверхность для волны
        wave_surface = pygame.Surface((width, wave_height), pygame.SRCALPHA)
        
        # Градиентная заливка
        for y in range(wave_height):
            alpha = int(150 * (1 - y / wave_height))
            color = (100, 0, 0, alpha)
            pygame.draw.line(wave_surface, color, (0, wave_height - y), (width, wave_height - y))
            
        # Рисуем частицы
        for particle in self.particles:
            alpha = int(255 * particle['life'])
            color = (*particle['color'][:3], alpha)
            particle_size = int(particle['size'])
            pygame.draw.circle(wave_surface, color, 
                             (int(particle['x']), int(particle['y'] - (700 - wave_height))), 
                             particle_size)
            
        # Волнистая граница
        for x in range(0, width, 5):
            wave_offset = math.sin(x * 0.1 + pygame.time.get_ticks() * 0.01) * 10
            pygame.draw.circle(wave_surface, (200, 0, 0, 200), 
                             (x, int(wave_height + wave_offset)), 3)
            
        screen.blit(wave_surface, (0, height - wave_height))