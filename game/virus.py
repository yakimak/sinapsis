import pygame
import random
import math

class Virus:
    def __init__(self, node):
        self.node = node
        self.type = "advanced"
        self.timer = 0
        self.spread_interval = random.randint(4000, 8000)
        self.health = 3
        self.attack_timer = 0
        self.attack_interval = 10000
        self.movement_timer = 0
        self.movement_interval = 15000
        self.evolution_timer = 0
        self.evolution_stage = 1
        self.particles = []
        
    def update(self, nodes, connections, dt):
        self.timer += dt
        self.attack_timer += dt
        self.movement_timer += dt
        self.evolution_timer += dt
        
        # Эволюция каждые 45 секунд
        if self.evolution_timer >= 45000:
            self.evolve()
            self.evolution_timer = 0
            
        # Распространение
        if self.timer >= self.spread_interval:
            self.timer = 0
            self.try_spread(nodes, connections)
            
        # Атака на связи
        if self.attack_timer >= self.attack_interval:
            self.attack_timer = 0
            self.attack_connections(connections)
            
        # Движение
        if self.movement_timer >= self.movement_interval:
            self.movement_timer = 0
            self.try_move(nodes, connections)
            
        self.update_particles(dt)
            
    def evolve(self):
        """Вирус эволюционирует и становится сильнее"""
        self.evolution_stage += 1
        self.health = min(5, self.health + 1)
        self.spread_interval = max(2000, self.spread_interval - 1000)
        
        # Эффект эволюции
        self.create_evolution_effect()
        
    def create_evolution_effect(self):
        for i in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            self.particles.append({
                'x': self.node.x,
                'y': self.node.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'color': (255, 50, 50),
                'size': random.randint(3, 6),
                'life': 1.0
            })
            
    def try_spread(self, nodes, connections):
        """Умное распространение - предпочитает узлы ближе к старту"""
        neighbors = []
        start_node = next((n for n in nodes if n.type == "start"), None)
        
        for node in nodes:
            # Вирусы не могут распространяться через firewall узлы
            if node.type == "firewall":
                continue
            
            if node.type == "neutral":
                # Проверяем соединение
                for connection in connections:
                    if connection.is_expired():
                        continue
                    if (connection.node1 == self.node and connection.node2 == node) or \
                       (connection.node2 == self.node and connection.node1 == node):
                        # Проверяем, не защищен ли узел firewall
                        is_protected = False
                        for other_node in nodes:
                            if other_node.type == "firewall":
                                # Проверяем, есть ли связь между firewall и целевым узлом
                                for conn in connections:
                                    if conn.is_expired():
                                        continue
                                    if ((conn.node1 == other_node and conn.node2 == node) or \
                                        (conn.node2 == other_node and conn.node1 == node)):
                                        is_protected = True
                                        break
                                if is_protected:
                                    break
                        
                        if not is_protected:
                            # Оцениваем приоритет (ближе к старту = выше приоритет)
                            priority = 0
                            if start_node:
                                distance_to_start = ((node.x - start_node.x) ** 2 + (node.y - start_node.y) ** 2) ** 0.5
                                priority = 1.0 / (distance_to_start + 1)
                            
                            neighbors.append((node, priority))
                        break
        
        if neighbors:
            # Выбираем узел с учетом приоритета
            total_priority = sum(priority for _, priority in neighbors)
            rand_val = random.uniform(0, total_priority)
            current = 0
            
            for node, priority in neighbors:
                current += priority
                if rand_val <= current:
                    self.infect_node(node)
                    return True
                    
        return False
        
    def infect_node(self, target_node):
        """Заражение узла с эффектом"""
        target_node.type = "virus"
        self.create_infection_effect(target_node)
        
    def create_infection_effect(self, target_node):
        """Эффект заражения узла"""
        for i in range(15):
            t = i / 15.0
            x = self.node.x + (target_node.x - self.node.x) * t
            y = self.node.y + (target_node.y - self.node.y) * t
            
            self.particles.append({
                'x': x,
                'y': y,
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-0.5, 0.5),
                'color': (255, 0, 0),
                'size': random.randint(2, 4),
                'life': 1.0
            })
        
    def attack_connections(self, connections):
        """Атака на соседние связи"""
        target_connections = []
        
        for connection in connections:
            if connection.is_expired():
                continue
            if connection.node1 == self.node or connection.node2 == self.node:
                # Не атакуем усиленные связи и firewall связи
                if connection.type in ["enhanced", "firewall"]:
                    continue
                # Предпочитаем обычные связи
                priority = 2 if connection.type == "normal" else 1
                target_connections.extend([connection] * priority)
                
        if target_connections:
            target = random.choice(target_connections)
            if target in connections:  # Проверяем, что связь еще существует
                connections.remove(target)
                self.create_attack_effect(target)
            
    def create_attack_effect(self, connection):
        """Эффект атаки на связь"""
        x1, y1 = connection.node1.x, connection.node1.y
        x2, y2 = connection.node2.x, connection.node2.y
        
        for i in range(10):
            t = random.uniform(0, 1)
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t
            
            self.particles.append({
                'x': x,
                'y': y,
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-2, 2),
                'color': (255, 100, 100),
                'size': random.randint(2, 5),
                'life': 1.0
            })
            
    def try_move(self, nodes, connections):
        """Попытка переместиться на соседний узел"""
        neighbors = []
        
        for node in nodes:
            # Вирусы не могут перемещаться на firewall узлы
            if node.type == "firewall":
                continue
            if node.type == "neutral":
                for connection in connections:
                    if connection.is_expired():
                        continue
                    if (connection.node1 == self.node and connection.node2 == node) or \
                       (connection.node2 == self.node and connection.node1 == node):
                        neighbors.append(node)
                        break
                        
        if neighbors:
            new_node = random.choice(neighbors)
            old_node = self.node
            
            # Перемещаем вирус
            self.node.type = "neutral"
            new_node.type = "virus"
            self.node = new_node
            
            self.create_movement_effect(old_node, new_node)
            
    def create_movement_effect(self, old_node, new_node):
        """Эффект перемещения вируса"""
        for i in range(20):
            t = i / 20.0
            x = old_node.x + (new_node.x - old_node.x) * t
            y = old_node.y + (new_node.y - old_node.y) * t
            
            self.particles.append({
                'x': x,
                'y': y,
                'vx': 0,
                'vy': 0,
                'color': (255, 150, 150),
                'size': random.randint(2, 4),
                'life': 0.5
            })
            
    def update_particles(self, dt):
        for particle in self.particles[:]:
            # Используем get для безопасного доступа к ключам
            particle['x'] += particle.get('vx', 0)
            particle['y'] += particle.get('vy', 0)
            particle['life'] -= 0.02
        
            if particle['life'] <= 0:
                self.particles.remove(particle)
                
    def take_damage(self):
        """Вирус получает урон"""
        self.health -= 1
        if self.health <= 0:
            return True  # Вирус уничтожен
        return False
        
    def draw(self, screen):
        # Пульсация в зависимости от стадии эволюции
        pulse_speed = 0.002 * self.evolution_stage
        pulse = (math.sin(pygame.time.get_ticks() * pulse_speed) + 1) / 2
        
        base_radius = 20 + 5 * self.evolution_stage
        radius = int(base_radius + 5 * pulse)  # Преобразуем в integer
        
        # Основной круг
        color_intensity = 100 + int(155 * pulse)
        pygame.draw.circle(screen, (255, color_intensity - 100, color_intensity - 100), 
                         (self.node.x, self.node.y), radius)
        
        # Внешнее кольцо
        ring_color = (255, 100, 100, 150)
        for i in range(3):
            ring_radius = radius + 5 + i * 3
            alpha = 100 - i * 30
            s = pygame.Surface((ring_radius * 2, ring_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*ring_color[:3], alpha), (ring_radius, ring_radius), ring_radius, 2)
            screen.blit(s, (self.node.x - ring_radius, self.node.y - ring_radius))
        
        # Частицы
        for particle in self.particles:
            alpha = int(255 * particle['life'])
            color = (*particle['color'], alpha)
            particle_size = int(particle['size'])
            s = pygame.Surface((particle_size * 2, particle_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (particle_size, particle_size), particle_size)
            screen.blit(s, (particle['x'] - particle_size, particle['y'] - particle_size))
        
        # Индикатор эволюции
        for i in range(self.evolution_stage):
            angle = 2 * math.pi * i / self.evolution_stage
            spike_x = self.node.x + math.cos(angle) * (radius + 5)
            spike_y = self.node.y + math.sin(angle) * (radius + 5)
            pygame.draw.circle(screen, (255, 255, 0), (int(spike_x), int(spike_y)), 3)
            
        # Индикатор здоровья
        for i in range(self.health):
            pygame.draw.circle(screen, (255, 255, 255), 
                             (self.node.x - 15 + i * 8, self.node.y - radius - 10), 3)