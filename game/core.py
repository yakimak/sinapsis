import pygame
import random
import math
from .node import Node
from .connection import Connection
from .levels import get_level
from .silence import Silence
from .virus import Virus
from .agent import Agent

# Константы
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
GAME_AREA_WIDTH = 900
PANEL_WIDTH = 300
FPS = 60

class GameState:
    PLAYING = "playing"
    WIN = "win"
    LOSE = "lose"

class LevelManager:
    def __init__(self, agent):
        self.agent = agent
        self.current_level = 1
        self.nodes = []
        self.connections = []
        self.viruses = []
        self.player_energy = 0
        self.level_config = None
        
    def load_level(self, level_num):
        try:
            self.level_config = get_level(level_num)
            self.current_level = level_num
        except Exception as e:
            print(f"Ошибка загрузки уровня {level_num}: {e}")
            self.level_config = get_level(1)
            self.current_level = 1
            
        self.nodes = []
        for node_data in self.level_config["nodes"]:
            self.nodes.append(Node(**node_data))
            
        self.player_energy = self.level_config["start_energy"]
        self.connections = []
        self.viruses = []
        
        # Инициализируем вирусы
        for node in self.nodes:
            if node.type == "virus":
                self.viruses.append(Virus(node))
                
        return self.level_config

class UIManager:
    def __init__(self, screen, font, title_font):
        self.screen = screen
        self.font = font
        self.title_font = title_font
        self.small_font = pygame.font.Font(None, 18)
        self.medium_font = pygame.font.Font(None, 22)
        self.large_font = pygame.font.Font(None, 28)
        self.scroll_offset = 0
        self.max_scroll = 0
        
    def _draw_separator(self, x, y):
        """Рисует разделительную линию"""
        pygame.draw.line(self.screen, (50, 50, 70), (x + 10, y), (x + 290, y), 1)
        
    def _draw_scrollable_description(self, panel_x, start_y, description):
        """Рисует описание уровня с возможностью прокрутки"""
        max_height = 150
        line_height = 16
        max_lines = max_height // line_height
        
        lines = description.split('\n')
        visible_lines = lines
        
        # Если текст слишком длинный, обрезаем
        if len(lines) > max_lines:
            visible_lines = lines[:max_lines]
            visible_lines.append("... (используйте колесо мыши для прокрутки)")
        
        y_offset = start_y
        for line in visible_lines:
            if y_offset > 650:  # Не выходим за пределы экрана
                break
            desc_text = self.small_font.render(line, True, (200, 200, 200))
            self.screen.blit(desc_text, (panel_x + 10, y_offset))
            y_offset += line_height
            
        return len(visible_lines) * line_height
        
    def _draw_stats(self, panel_x, y_offset, game_data):
        """Рисует статистику игры"""
        start_y = y_offset
        
        # Агент с эффектом
        agent_text = self.medium_font.render(">>> АГЕНТ 22 <<<", True, (0, 255, 255))
        self.screen.blit(agent_text, (panel_x + 10, y_offset))
        
        # Индикатор активности
        pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500.0
        indicator_color = (0, int(255 * pulse), 255)
        pygame.draw.circle(self.screen, indicator_color, (panel_x + 280, y_offset + 10), 5)
        y_offset += 30
        
        # Энергия с прогресс-баром
        energy_color = (255, 255, 255) if game_data["player_energy"] > 40 else (255, 200, 0) if game_data["player_energy"] > 20 else (255, 100, 100)
        energy_text = self.medium_font.render(f"ЭНЕРГИЯ: {game_data['player_energy']}", True, energy_color)
        self.screen.blit(energy_text, (panel_x + 10, y_offset))
        y_offset += 25
        
        # Прогресс-бар энергии
        max_energy = 150  # Примерное максимальное значение
        energy_ratio = min(1.0, game_data["player_energy"] / max_energy)
        bar_width = int(280 * energy_ratio)
        pygame.draw.rect(self.screen, (50, 50, 50), (panel_x + 10, y_offset, 280, 12))
        pygame.draw.rect(self.screen, energy_color, (panel_x + 10, y_offset, bar_width, 12))
        pygame.draw.rect(self.screen, (100, 100, 100), (panel_x + 10, y_offset, 280, 12), 1)
        y_offset += 20
        
        # Уровень
        level_text = self.medium_font.render(f"СЛОЙ: {game_data['current_level']}/10", True, (255, 255, 255))
        self.screen.blit(level_text, (panel_x + 10, y_offset))
        y_offset += 25
        
        # Таймер уровня
        if game_data["level_time"] > 0:
            time_color = (255, 255, 255) if game_data["time_left"] > 30 else (255, 200, 0) if game_data["time_left"] > 10 else (255, 100, 100)
            time_text = self.medium_font.render(f"ВРЕМЯ: {int(game_data['time_left'])}с", True, time_color)
            self.screen.blit(time_text, (panel_x + 10, y_offset))
            y_offset += 25
            
            # Прогресс-бар времени
            time_progress = max(0, game_data["time_left"] / game_data["level_time"])
            pygame.draw.rect(self.screen, (50, 0, 0), (panel_x + 10, y_offset, 280, 12))
            pygame.draw.rect(self.screen, time_color, (panel_x + 10, y_offset, 280 * time_progress, 12))
            pygame.draw.rect(self.screen, (100, 100, 100), (panel_x + 10, y_offset, 280, 12), 1)
            y_offset += 25
            
        return y_offset - start_y
        
    def _draw_abilities(self, panel_x, y_offset, game_data):
        """Рисует информацию о способностях"""
        start_y = y_offset
        
        abilities_text = self.medium_font.render("Способности:", True, (100, 255, 100))
        self.screen.blit(abilities_text, (panel_x + 10, y_offset))
        y_offset += 25
        
        if game_data["agent"].abilities["enhanced_connections"]:
            ability_text = self.small_font.render("✓ УСИЛЕННЫЕ СВЯЗИ [E]", True, (100, 255, 100))
            self.screen.blit(ability_text, (panel_x + 10, y_offset))
            y_offset += 20
            
            # Статус режима с эффектом
            if game_data["enhanced_mode"]:
                pulse = abs(pygame.time.get_ticks() % 500 - 250) / 250.0
                mode_color = (int(0 + 200 * pulse), 200, 255)
                mode_text = self.small_font.render(">>> РЕЖИМ: УСИЛЕННЫЕ <<<", True, mode_color)
            else:
                mode_text = self.small_font.render("РЕЖИМ: ОБЫЧНЫЕ", True, (0, 255, 0))
            self.screen.blit(mode_text, (panel_x + 10, y_offset))
            y_offset += 25
        
        if game_data["agent"].abilities["antivirus"]:
            antivirus_text = self.small_font.render("✓ АНТИВИРУС [Клик по вирусу]", True, (255, 100, 100))
            self.screen.blit(antivirus_text, (panel_x + 10, y_offset))
            y_offset += 20
            
            cost_text = self.small_font.render("Стоимость: 50 энергии", True, (200, 200, 200))
            self.screen.blit(cost_text, (panel_x + 10, y_offset))
            y_offset += 20
            
            isolation_text = self.small_font.render("Или изолируйте вирус", True, (150, 200, 255))
            self.screen.blit(isolation_text, (panel_x + 10, y_offset))
            y_offset += 25
            
        return y_offset - start_y
        
    def _draw_legend(self, panel_x, y_offset):
        """Рисует легенду цветов узлов"""
        start_y = y_offset
        
        legend_text = self.medium_font.render("ЛЕГЕНДА:", True, (255, 255, 255))
        self.screen.blit(legend_text, (panel_x + 10, y_offset))
        y_offset += 25
        
        colors = [
            ("🟢 Зеленый", "Старт"),
            ("🔵 Синий", "Финиш"), 
            ("⚪ Серый", "Нейтральный"),
            ("🔴 Красный", "Вирус (клик для уничтожения)"),
            ("🛡️ Голубой", "Firewall"),
            ("⚡ Желтый", "Amplifier"),
            ("💜 Фиолетовый", "Decoy"),
            ("❓ Фиолетовый", "Codex")
        ]
        
        for color_name, description in colors:
            color_text = self.small_font.render(f"{color_name}: {description}", True, (200, 200, 200))
            self.screen.blit(color_text, (panel_x + 10, y_offset))
            y_offset += 18
            
        return y_offset - start_y
        
    def _draw_costs(self, panel_x, y_offset):
        """Рисует стоимость связей"""
        start_y = y_offset
        
        cost_text = self.medium_font.render("СТОИМОСТЬ СВЯЗЕЙ:", True, (255, 255, 255))
        self.screen.blit(cost_text, (panel_x + 10, y_offset))
        y_offset += 25
        
        costs = [
            ("🔗 Обычная связь", "20 энергии"),
            ("💎 Усиленная связь", "40 энергии"),
            ("⏱️ Временная связь", "15 энергии")
        ]
        
        for connection_type, cost in costs:
            cost_text = self.small_font.render(f"{connection_type}: {cost}", True, (200, 200, 200))
            self.screen.blit(cost_text, (panel_x + 10, y_offset))
            y_offset += 18
            
        return y_offset - start_y
        
    def _draw_controls(self, panel_x):
        """Рисует управление внизу панели"""
        controls = [
            "УПРАВЛЕНИЕ:",
            "ЛКМ - создать связь",
            "ЛКМ по вирусу - уничтожить",
            "E - усиленные связи", 
            "R - перезапуск",
            "N - следующий уровень"
        ]
        
        y_start = SCREEN_HEIGHT - len(controls) * 20 - 10
        for i, control in enumerate(controls):
            color = (0, 255, 255) if i == 0 else (150, 200, 255)
            control_text = self.small_font.render(control, True, color)
            self.screen.blit(control_text, (panel_x + 10, y_start + i * 18))
    
    def _draw_scan_lines(self, panel_x):
        """Рисует сканирующие линии в киберпространственном стиле"""
        import math
        scan_y = int((pygame.time.get_ticks() / 50) % SCREEN_HEIGHT)
        s = pygame.Surface((PANEL_WIDTH, 2), pygame.SRCALPHA)
        s.fill((0, 255, 255, 100))
        self.screen.blit(s, (panel_x, scan_y))
    
    def _draw_terminal_grid(self, panel_x):
        """Рисует сетку в терминальном стиле"""
        grid_color = (0, 50, 50)
        for y in range(0, SCREEN_HEIGHT, 20):
            pygame.draw.line(self.screen, grid_color, (panel_x, y), (panel_x + PANEL_WIDTH, y), 1)
        for x in range(panel_x, SCREEN_WIDTH, 30):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, SCREEN_HEIGHT), 1)
        
    def draw_panel(self, game_data):
        """Отрисовывает правую панель UI в киберпространственном стиле"""
        panel_x = GAME_AREA_WIDTH
        y_offset = 20
        
        # Фон панели с градиентом
        pygame.draw.rect(self.screen, (10, 10, 25), (panel_x, 0, PANEL_WIDTH, SCREEN_HEIGHT))
        
        # Сканирующие линии
        self._draw_scan_lines(panel_x)
        
        # Граница с эффектом свечения
        for i in range(3):
            alpha = 100 - i * 30
            s = pygame.Surface((2, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 255, 255, alpha))
            self.screen.blit(s, (panel_x + i, 0))
        
        # Терминальный стиль - сетка
        self._draw_terminal_grid(panel_x)
        
        # Название уровня
        title_text = self.large_font.render(game_data["level_name"], True, (255, 255, 255))
        self.screen.blit(title_text, (panel_x + 10, y_offset))
        y_offset += 40
        
        # Описание уровня
        desc_height = self._draw_scrollable_description(panel_x, y_offset, game_data["level_description"])
        y_offset += desc_height + 20
        
        # Разделитель
        self._draw_separator(panel_x, y_offset)
        y_offset += 20
        
        # Статистика
        stats_height = self._draw_stats(panel_x, y_offset, game_data)
        y_offset += stats_height + 10
        
        # Разделитель
        self._draw_separator(panel_x, y_offset)
        y_offset += 20
        
        # Способности
        abilities_height = self._draw_abilities(panel_x, y_offset, game_data)
        y_offset += abilities_height + 10
        
        # Разделитель
        self._draw_separator(panel_x, y_offset)
        y_offset += 20
        
        # Легенда
        legend_height = self._draw_legend(panel_x, y_offset)
        y_offset += legend_height + 10
        
        # Разделитель
        self._draw_separator(panel_x, y_offset)
        y_offset += 20
        
        # Стоимость связей
        costs_height = self._draw_costs(panel_x, y_offset)
        y_offset += costs_height
        
        # Управление (всегда внизу)
        self._draw_controls(panel_x)
        
    def draw_game_state_message(self, game_state, time_left, stars=0):
        """Отрисовывает сообщения о победе/поражении"""
        overlay = pygame.Surface((GAME_AREA_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        if game_state == GameState.WIN:
            win_text = self.large_font.render("СЛОЙ СТАБИЛИЗИРОВАН!", True, (0, 255, 0))
            text_rect = win_text.get_rect(center=(GAME_AREA_WIDTH//2, SCREEN_HEIGHT//2 - 80))
            self.screen.blit(win_text, text_rect)
            
            # Рисуем звезды
            stars_text = self.medium_font.render(f"ЗВЕЗД ЗАРАБОТАНО: {stars}/5", True, (255, 215, 0))
            stars_rect = stars_text.get_rect(center=(GAME_AREA_WIDTH//2, SCREEN_HEIGHT//2 - 30))
            self.screen.blit(stars_text, stars_rect)
            
            # Визуальные звезды
            star_size = 30
            star_spacing = 50
            start_x = GAME_AREA_WIDTH//2 - (star_spacing * 2)
            for i in range(5):
                x = start_x + i * star_spacing
                y = SCREEN_HEIGHT//2 + 10
                if i < stars:
                    # Золотая звезда
                    self._draw_star(self.screen, x, y, star_size, (255, 215, 0))
                else:
                    # Серая звезда
                    self._draw_star(self.screen, x, y, star_size, (100, 100, 100))
            
            next_text = self.medium_font.render("Нажмите N для следующего уровня", True, (200, 255, 200))
            next_rect = next_text.get_rect(center=(GAME_AREA_WIDTH//2, SCREEN_HEIGHT//2 + 60))
            self.screen.blit(next_text, next_rect)
            
        elif game_state == GameState.LOSE:
            if time_left <= 0:
                lose_text = self.large_font.render("ВРЕМЯ ВЫШЛО!", True, (255, 0, 0))
            else:
                lose_text = self.large_font.render("СИСТЕМА ЗАРАЖЕНА!", True, (255, 0, 0))
                
            restart_text = self.medium_font.render("Нажмите R для перезапуска", True, (255, 200, 200))
            
            text_rect = lose_text.get_rect(center=(GAME_AREA_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            restart_rect = restart_text.get_rect(center=(GAME_AREA_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            
            self.screen.blit(lose_text, text_rect)
            self.screen.blit(restart_text, restart_rect)
    
    def _draw_star(self, screen, x, y, size, color):
        """Рисует звезду"""
        import math
        points = []
        outer_radius = size // 2
        inner_radius = size // 4
        for i in range(10):
            angle = i * math.pi / 5 - math.pi / 2
            if i % 2 == 0:
                radius = outer_radius
            else:
                radius = inner_radius
            px = x + math.cos(angle) * radius
            py = y + math.sin(angle) * radius
            points.append((px, py))
        pygame.draw.polygon(screen, color, points)

class ConnectionManager:
    def __init__(self):
        self.connections = []
        
    def connection_exists(self, node1, node2):
        for conn in self.connections:
            if (conn.node1 == node1 and conn.node2 == node2) or (conn.node1 == node2 and conn.node2 == node1):
                return True
        return False
        
    def create_connection(self, node1, node2, connection_type, agent, player_energy, max_length=250, duration=None):
        """Создает соединение и возвращает новую энергию"""
        # Проверяем расстояние
        distance = ((node1.x - node2.x) ** 2 + (node1.y - node2.y) ** 2) ** 0.5
        if distance > max_length:  # Используем переданный параметр
            return player_energy, "Слишком длинная связь! Макс: {}px".format(max_length)
            
        # Запрещаем прямое соединение старта и финиша
        if (node1.type == "start" and node2.type == "finish") or (node1.type == "finish" and node2.type == "start"):
            return player_energy, "Нельзя соединять старт и финиш напрямую!"
        
        # Специальные правила для новых типов узлов
        if node1.type == "firewall" or node2.type == "firewall":
            # Firewall блокирует вирусы, но стоит дороже
            if connection_type == "normal":
                connection_type = "firewall"
        
        # Amplifier снижает стоимость связей на 30%
        cost_multiplier = 1.0
        if node1.type == "amplifier" or node2.type == "amplifier":
            cost_multiplier = 0.7
            
        cost = int(agent.get_connection_cost(connection_type) * cost_multiplier)
        
        if player_energy >= cost and not self.connection_exists(node1, node2):
            self.connections.append(Connection(node1, node2, connection_type, duration))
            return player_energy - cost, "Связь создана!"
        
        return player_energy, "Недостаточно энергии или связь уже существует"
    
    def update_connections(self, dt):
        """Обновляет все связи (анимации, временные связи)"""
        connections_to_remove = []
        for connection in self.connections:
            connection.update(dt)
            if connection.is_expired():
                connections_to_remove.append(connection)
        
        for conn in connections_to_remove:
            self.connections.remove(conn)
    
    def check_connection(self, start, finish):
        """Проверяет существование пути от start до finish"""
        visited = set()
        return self._dfs_connection(start, finish, visited)
    
    def find_all_paths(self, start, finish):
        """Находит все возможные пути от start до finish"""
        paths = []
        visited = set()
        self._dfs_all_paths(start, finish, visited, [], paths)
        return paths
    
    def _dfs_all_paths(self, current, finish, visited, path, all_paths):
        if current == finish:
            all_paths.append(path[:])
            return
        
        if current.type == "virus" or current in visited:
            return
        
        visited.add(current)
        path.append(current)
        
        for connection in self.connections:
            if connection.is_expired():
                continue
            node1, node2 = connection.node1, connection.node2
            if node1 == current and node2 not in visited:
                self._dfs_all_paths(node2, finish, visited, path, all_paths)
            elif node2 == current and node1 not in visited:
                self._dfs_all_paths(node1, finish, visited, path, all_paths)
        
        path.pop()
        visited.remove(current)
        
    def _dfs_connection(self, current, finish, visited):
        if current == finish:
            return True
            
        if current.type == "virus" or current in visited:
            return False
            
        visited.add(current)
        
        for connection in self.connections:
            if connection.is_expired():
                continue
            node1, node2 = connection.node1, connection.node2
            if node1 == current and node2 not in visited:
                if self._dfs_connection(node2, finish, visited):
                    return True
            elif node2 == current and node1 not in visited:
                if self._dfs_connection(node1, finish, visited):
                    return True
                    
        return False

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Синапсис - Агент 22")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        
        # Инициализация систем
        self.agent = Agent()
        self.silence = Silence()
        self.level_manager = LevelManager(self.agent)
        self.connection_manager = ConnectionManager()
        self.ui_manager = UIManager(self.screen, self.font, self.title_font)
        
        self.enhanced_mode = False
        self.selected_node = None
        self.hover_node = None
        self.game_state = GameState.PLAYING
        self.stars_earned = 0
        self.destruction_effects = []  # Эффекты уничтожения вирусов
        
        # Таймер уровня
        self.level_time = 0
        self.time_left = 0
        self.level_start_time = 0
        
        self.load_level(1)
        
    def load_level(self, level_num):
        level_config = self.level_manager.load_level(level_num)
        self.connection_manager.connections = self.level_manager.connections
        self.player_energy = self.level_manager.player_energy
        
        # Настройка уровня
        self.level_name = level_config.get("name", f"Уровень {level_num}")
        self.level_description = level_config.get("description", "")
        
        # Настройка времени уровня
        self.level_time = level_config.get("time_limit", 0)
        self.time_left = self.level_time
        self.level_start_time = pygame.time.get_ticks()
        
        # Настройка волн Тишины
        if level_config.get("waves", False):
            self.silence.speed = level_config.get("silence_speed", 0.001)
            self.silence.wave_interval = level_config.get("wave_interval", 30000)
        else:
            self.silence.speed = 0
            
        # Разблокировка способностей в зависимости от уровня
        if level_num >= 4:
            self.agent.unlock_ability("enhanced_connections")
        if level_num >= 6:
            self.agent.unlock_ability("antivirus")
            
        self.selected_node = None
        self.hover_node = None
        self.game_state = GameState.PLAYING
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.MOUSEBUTTONDOWN and self.game_state == GameState.PLAYING:
                if event.pos[0] < GAME_AREA_WIDTH:
                    self.handle_click(event.pos)
                    
            if event.type == pygame.MOUSEMOTION:
                self.handle_hover(event.pos)
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.load_level(self.level_manager.current_level)
                elif event.key == pygame.K_n and self.game_state == GameState.WIN:
                    self.current_level = min(10, self.level_manager.current_level + 1)
                    self.load_level(self.current_level)
                elif event.key == pygame.K_e and self.agent.can_use_enhanced_connections():
                    self.enhanced_mode = not self.enhanced_mode
        
        return True

    def handle_hover(self, pos):
        """Обработка наведения мыши на узлы"""
        if pos[0] < GAME_AREA_WIDTH:
            self.hover_node = None
            for node in self.level_manager.nodes:
                if node.is_clicked(pos):
                    self.hover_node = node
                    break

    def handle_click(self, pos):
        """Обработка кликов по узлам"""
        for node in self.level_manager.nodes:
            if node.is_clicked(pos):
                # Попытка уничтожить вирус при клике
                if node.type == "virus":
                    if self.destroy_virus(node):
                        # Вирус уничтожен, сбрасываем выделение
                        if self.selected_node:
                            self.selected_node.selected = False
                            self.selected_node = None
                    return
                    
                if self.selected_node is None:
                    self.selected_node = node
                    node.selected = True
                else:
                    if node != self.selected_node:
                        self.create_connection(self.selected_node, node)
                    self.selected_node.selected = False
                    self.selected_node = None
                break

    def create_connection(self, node1, node2):
        """Создание соединения между узлами"""
        if node1.type == "virus" or node2.type == "virus":
            return
        
        # Определяем тип связи
        # Если уровень поддерживает временные связи, используем их по умолчанию
        if self.level_manager.level_config.get("temporary_connections", False):
            connection_type = "temporary"
            duration = self.level_manager.level_config.get("temporary_duration", 10.0)
        else:
            connection_type = "enhanced" if self.enhanced_mode else "normal"
            duration = None
        
        # Получаем максимальную длину соединения для текущего уровня
        max_length = self.level_manager.level_config.get("max_connection_length", 250)
    
        new_energy, message = self.connection_manager.create_connection(
            node1, node2, connection_type, self.agent, self.player_energy, max_length, duration
        )   
        
        if new_energy != self.player_energy:  # Если соединение создано
            self.player_energy = new_energy

    def destroy_virus(self, virus_node):
        """Игрок может уничтожить вирус"""
        # Способ 1: Изоляция (все связи разорваны)
        if self.is_isolated(virus_node):
            # Удаляем вирус из списка вирусов
            virus_to_remove = None
            for virus in self.level_manager.viruses:
                if virus.node == virus_node:
                    virus_to_remove = virus
                    break
            
            if virus_to_remove:
                self.level_manager.viruses.remove(virus_to_remove)
            
            # Меняем тип узла на нейтральный
            virus_node.type = "neutral"
            
            # Визуальный эффект уничтожения
            self.create_virus_destruction_effect(virus_node)
            return True
        
        # Способ 2: Антивирусная атака (дорогая способность)
        if self.agent.can_use_antivirus() and self.player_energy >= 50:
            # Удаляем вирус из списка вирусов
            virus_to_remove = None
            for virus in self.level_manager.viruses:
                if virus.node == virus_node:
                    virus_to_remove = virus
                    break
            
            if virus_to_remove:
                self.level_manager.viruses.remove(virus_to_remove)
            
            virus_node.type = "neutral"
            self.player_energy -= 50
            
            # Визуальный эффект уничтожения
            self.create_virus_destruction_effect(virus_node)
            return True
        
        return False
    
    def is_isolated(self, node):
        """Проверяет изолирован ли узел от основной сети"""
        # Узел изолирован если не соединен со стартом через активные связи
        start_node = next((n for n in self.level_manager.nodes if n.type == "start"), None)
        if start_node:
            # Проверяем изоляцию: нет активных связей с другими узлами
            has_connections = False
            for connection in self.connection_manager.connections:
                if connection.is_expired():
                    continue
                if (connection.node1 == node and connection.node2 != node) or \
                   (connection.node2 == node and connection.node1 != node):
                    has_connections = True
                    break
            
            # Если есть связи, проверяем, соединен ли со стартом
            if has_connections:
                return not self.connection_manager.check_connection(start_node, node)
            else:
                # Нет связей вообще - изолирован
                return True
        return True
    
    def create_virus_destruction_effect(self, node):
        """Создает визуальный эффект уничтожения вируса"""
        import random
        import math
        
        # Создаем частицы для эффекта уничтожения
        for i in range(30):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.destruction_effects.append({
                'x': node.x,
                'y': node.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'color': (255, 200, 0),
                'size': random.randint(3, 6),
                'life': 1.0,
                'max_life': 1.0
            })
    
    def check_victory(self):
        """Проверка условий победы"""
        start_node = next((n for n in self.level_manager.nodes if n.type == "start"), None)
        finish_node = next((n for n in self.level_manager.nodes if n.type == "finish"), None)
        
        if not start_node or not finish_node:
            return False
        
        return self.connection_manager.check_connection(start_node, finish_node)
    
    def calculate_stars(self):
        """Вычисляет количество звезд за уровень"""
        stars = 0
        level_config = self.level_manager.level_config
        
        # Звезда 1: Основная победа
        if self.check_victory():
            stars += 1
        
        # Звезда 2: Время (если есть лимит)
        if level_config.get("time_limit", 0) > 0:
            time_bonus = level_config.get("time_bonus", 0.7)  # 70% времени осталось
            if self.time_left / self.level_time >= time_bonus:
                stars += 1
        
        # Звезда 3: Энергия
        energy_bonus = level_config.get("energy_bonus", 0.3)  # 30% энергии осталось
        if self.player_energy / self.level_manager.player_energy >= energy_bonus:
            stars += 1
        
        # Звезда 4: Количество связей
        max_connections = level_config.get("max_connections", None)
        if max_connections and len(self.connection_manager.connections) <= max_connections:
            stars += 1
        
        # Звезда 5: Резервный путь
        start_node = next((n for n in self.level_manager.nodes if n.type == "start"), None)
        finish_node = next((n for n in self.level_manager.nodes if n.type == "finish"), None)
        if start_node and finish_node:
            paths = self.connection_manager.find_all_paths(start_node, finish_node)
            if len(paths) >= 2:  # Есть резервный путь
                stars += 1
        
        return min(stars, 5)  # Максимум 5 звезд

    def update(self):
        dt = self.clock.get_time()
        
        if self.game_state == GameState.PLAYING:
            # Обновляем таймер уровня
            if self.level_time > 0:
                self.time_left -= dt / 1000.0
                if self.time_left <= 0:
                    self.game_state = GameState.LOSE
                    return
            
            # Обновляем узлы
            for node in self.level_manager.nodes:
                node.update(dt)
            
            # Обновляем связи (анимации, временные связи)
            self.connection_manager.update_connections(dt)
            
            # Обновляем эффекты уничтожения
            for effect in self.destruction_effects[:]:
                effect['life'] -= dt / 1000.0 * 2
                effect['x'] += effect['vx'] * dt / 16.0
                effect['y'] += effect['vy'] * dt / 16.0
                effect['size'] *= 0.98
                if effect['life'] <= 0:
                    self.destruction_effects.remove(effect)
            
            # Обновляем системы
            self.silence.update(self.connection_manager.connections, self.level_manager.nodes, dt)
            
            # Обновляем вирусы (только активные)
            for virus in self.level_manager.viruses[:]:
                # Проверяем, что вирус еще существует
                if virus.node.type != "virus":
                    self.level_manager.viruses.remove(virus)
                    continue
                virus.update(self.level_manager.nodes, self.connection_manager.connections, dt)
            
            # Проверяем поражение от вирусов
            start_node = next((n for n in self.level_manager.nodes if n.type == "start"), None)
            if start_node and start_node.type == "virus":
                self.game_state = GameState.LOSE
            
            # Проверяем победу
            if self.check_victory():
                self.game_state = GameState.WIN
                self.stars_earned = self.calculate_stars()

    def draw(self):
        # Очищаем экран
        self.screen.fill((10, 10, 30))
        
        # Рисуем игровую область
        game_surface = pygame.Surface((GAME_AREA_WIDTH, SCREEN_HEIGHT))
        game_surface.fill((10, 10, 30))
        
        # Рисуем Тишину
        self.silence.draw(game_surface, GAME_AREA_WIDTH, SCREEN_HEIGHT)
        
        # Рисуем связи
        for connection in self.connection_manager.connections:
            connection.draw(game_surface)
        
        # Рисуем потенциальную связь при наведении
        if self.selected_node and self.hover_node and self.hover_node != self.selected_node:
            if self.hover_node.type != "virus":
                cost = self.agent.get_connection_cost("enhanced" if self.enhanced_mode else "normal")
                can_afford = self.player_energy >= cost
                color = (0, 255, 0) if can_afford else (255, 100, 100)
                alpha = 150 if can_afford else 80
                
                # Создаем поверхность с альфа-каналом
                preview_surface = pygame.Surface((GAME_AREA_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pygame.draw.line(preview_surface, (*color, alpha), 
                               (self.selected_node.x, self.selected_node.y),
                               (self.hover_node.x, self.hover_node.y), 3)
                game_surface.blit(preview_surface, (0, 0))
        
        # Рисуем узлы
        for node in self.level_manager.nodes:
            node.draw(game_surface)
        
        # Рисуем вирусы
        for virus in self.level_manager.viruses:
            virus.draw(game_surface)
        
        # Рисуем эффекты уничтожения
        for effect in self.destruction_effects:
            alpha = int(255 * (effect['life'] / effect['max_life']))
            color = (*effect['color'][:3], alpha)
            size = int(effect['size'])
            s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (size, size), size)
            game_surface.blit(s, (effect['x'] - size, effect['y'] - size))
        
        # Отображаем игровую поверхность
        self.screen.blit(game_surface, (0, 0))
        
        # Рисуем UI
        game_data = {
            "level_name": self.level_name,
            "level_description": self.level_description,
            "player_energy": self.player_energy,
            "current_level": self.level_manager.current_level,
            "level_time": self.level_time,
            "time_left": self.time_left,
            "agent": self.agent,
            "enhanced_mode": self.enhanced_mode
        }
        self.ui_manager.draw_panel(game_data)
        
        # Сообщения о состоянии игры
        if self.game_state != GameState.PLAYING:
            stars = getattr(self, 'stars_earned', 0)
            self.ui_manager.draw_game_state_message(self.game_state, self.time_left, stars)

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()