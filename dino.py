import pygame
import random
import numpy as np

class DinoGame:
    def __init__(self, num_dinos=10):
        if not pygame.get_init():
            pygame.init()
            
        # Configurações da tela
        self.width = 800
        self.height = 300
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Dino Game - NEAT Evolution")
        
        # Cores
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        
        # Constantes físicas
        self.gravity = 0.8  # Força da gravidade
        self.dino_height = 40  # Altura normal do dino
        self.dino_crouch_height = 20  # Altura quando agachado
        
        # Configurações da visualização da rede
        self.network_panel_width = 300
        self.network_panel_height = 200
        self.network_panel_x = self.width - self.network_panel_width - 10
        self.network_panel_y = 10
        self.node_radius = 15
        self.connection_width = 2
        
        # Configurações dos dinos
        self.num_dinos = num_dinos
        self.dinos = []
        self.reset_dinos()
        
        # Configurações dos obstáculos
        self.obstacles = []
        self.base_obstacle_speed = 5
        self.obstacle_speed = self.base_obstacle_speed
        self.min_obstacle_frequency = 800
        self.max_obstacle_frequency = 2000
        self.last_obstacle = 0
        self.last_score_check = 0
        
        # Estado do jogo
        self.score = 0
        self.game_over = False
        self.clock = pygame.time.Clock()
        
    def reset_dinos(self):
        """Reseta todos os dinossauros para o estado inicial"""
        self.dinos = []
        for i in range(self.num_dinos):
            self.dinos.append({
                'x': 50,
                'y': self.height - 50,
                'width': 40,
                'height': self.dino_height,
                'jump': False,
                'jump_vel': 0,
                'crouch': False,
                'alive': True,
                'fitness': 0,
                'color': self.GREEN if i == 0 else self.BLACK
            })
        
    def reset(self):
        """Reseta o estado do jogo para o início"""
        self.reset_dinos()
        self.obstacles = []
        self.score = 0
        self.game_over = False
        return self.get_state()
        
    def get_state(self):
        """Retorna o estado atual do jogo normalizado para o agente"""
        if not self.obstacles:
            return [self.dinos[0]['y'] / self.height,  # Posição vertical normalizada
                    1.0,  # Distância máxima normalizada
                    0.0,  # Altura normalizada
                    0.0]  # Posição vertical do obstáculo normalizada
        
        closest_obstacle = self._get_closest_obstacle()
        distance = (closest_obstacle[0] - self.dinos[0]['x']) / self.width
        height = closest_obstacle[2] / self.height
        obstacle_y = closest_obstacle[1] / self.height  # Posição vertical do obstáculo normalizada
        
        return [self.dinos[0]['y'] / self.height,
                min(1.0, max(0.0, distance)),  # Limita entre 0 e 1
                height,
                obstacle_y]  # Adiciona a posição vertical do obstáculo
                
    def _get_closest_obstacle(self):
        """Retorna o obstáculo mais próximo do dino"""
        return min(self.obstacles, key=lambda x: x[0])
        
    def _handle_actions(self, dino, action):
        """Gerencia as ações de um dinossauro específico"""
        # Ação 0: Nada
        # Ação 1: Pular
        # Ação 2: Agachar
        
        # Reset do estado de agachar
        if dino['crouch'] and action != 2:
            dino['crouch'] = False
            dino['height'] = self.dino_height
            
        # Aplicar ações
        if action == 1 and not dino['jump'] and not dino['crouch']:
            dino['jump'] = True
            dino['jump_vel'] = -15
        elif action == 2 and not dino['jump']:
            dino['crouch'] = True
            dino['height'] = self.dino_crouch_height
            
        # Aplicar gravidade se estiver pulando
        if dino['jump']:
            dino['y'] += dino['jump_vel']
            dino['jump_vel'] += self.gravity
            if dino['y'] >= self.height - 50:
                dino['y'] = self.height - 50
                dino['jump'] = False
                dino['jump_vel'] = 0
                
    def _generate_obstacle(self):
        """Gera um novo obstáculo se for o momento adequado"""
        current_time = pygame.time.get_ticks()
        # Randomiza o tempo entre obstáculos
        obstacle_frequency = random.randint(self.min_obstacle_frequency, self.max_obstacle_frequency)
        
        if current_time - self.last_obstacle > obstacle_frequency:
            # Aumenta a chance de obstáculos flutuantes
            if self.score >= 20 and random.random() < 0.6:  # 60% de chance de obstáculo flutuante
                height = random.choice([20, 40])
                # Varia a altura do obstáculo flutuante
                y_pos = random.randint(self.height - 200, self.height - 100)
                self.obstacles.append([self.width, y_pos, height])
            else:
                height = random.choice([20, 40])
                self.obstacles.append([self.width, self.height - height - 10, height])
            self.last_obstacle = current_time
            
    def _update_obstacles(self):
        """Atualiza a posição dos obstáculos e remove os que saíram da tela"""
        for obstacle in self.obstacles[:]:
            obstacle[0] -= self.obstacle_speed
            if obstacle[0] < -50:
                self.obstacles.remove(obstacle)
                self.score += 1
                
                # Aumenta a velocidade em 10% a cada 5 pontos
                if self.score - self.last_score_check >= 5:
                    self.obstacle_speed = self.base_obstacle_speed * (1.1 ** (self.score // 5))
                    self.last_score_check = self.score
        
    def _check_collision(self, dino):
        """Verifica se um dinossauro específico colidiu com algum obstáculo"""
        dino_rect = pygame.Rect(dino['x'], dino['y'], dino['width'], dino['height'])
        for obstacle in self.obstacles:
            obstacle_rect = pygame.Rect(obstacle[0], obstacle[1], 20, obstacle[2])
            if dino_rect.colliderect(obstacle_rect):
                return True
        return False
        
    def _calculate_reward(self, dino, action):
        """Calcula a recompensa para um dinossauro específico"""
        reward = 0.1  # Recompensa base por sobreviver
        
        if self.obstacles:
            closest_obstacle = self._get_closest_obstacle()
            
            # Recompensa por ações corretas
            if closest_obstacle[1] < self.height - 100:  # Obstáculo flutuante
                if action == 1 and 50 < (closest_obstacle[0] - dino['x']) < 100:
                    reward += 1.0  # Recompensa por pular
            else:  # Obstáculo no chão
                if action == 2 and 50 < (closest_obstacle[0] - dino['x']) < 100:
                    reward += 0.8  # Recompensa por agachar
                    
        # Penalidade por colisão
        if self._check_collision(dino):
            reward -= 2.0
            
        return reward
        
    def step(self, actions):
        """Executa um passo do jogo para todos os dinossauros vivos"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None, True
                
        for i, dino in enumerate(self.dinos):
            if dino['alive']:
                self._handle_actions(dino, actions[i])
                if self._check_collision(dino):
                    dino['alive'] = False
                    dino['color'] = self.RED
                else:
                    dino['fitness'] += self._calculate_reward(dino, actions[i])
                    
        self._generate_obstacle()
        self._update_obstacles()
        
        if all(not dino['alive'] for dino in self.dinos):
            self.game_over = True
            return self.get_state(), -10, True
            
        return self.get_state(), 0.1, False
        
    def _draw_dino(self, dino):
        """Desenha um dinossauro específico na tela"""
        if dino['crouch']:
            # Desenha o dino agachado
            pygame.draw.rect(self.screen, dino['color'], 
                           (dino['x'], dino['y'] + (self.dino_height - self.dino_crouch_height), 
                            dino['width'], self.dino_crouch_height))
        else:
            # Desenha o dino em pé
            pygame.draw.rect(self.screen, dino['color'], 
                           (dino['x'], dino['y'], dino['width'], dino['height']))
                        
    def _draw_obstacles(self):
        """Desenha os obstáculos na tela"""
        for obstacle in self.obstacles:
            pygame.draw.rect(self.screen, self.BLACK,
                           (obstacle[0], obstacle[1], 20, obstacle[2]))
                           
    def _draw_score(self):
        """Desenha a pontuação na tela"""
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, self.BLACK)
        self.screen.blit(score_text, (10, 10))
        
        # Mostra o número de dinos vivos
        alive_count = sum(1 for dino in self.dinos if dino['alive'])
        alive_text = font.render(f'Dinos Vivos: {alive_count}', True, self.BLACK)
        self.screen.blit(alive_text, (10, 40))
        
    def _draw_network(self, net, state, action):
        """Desenha a rede neural em tempo real"""
        # Desenha o painel de fundo
        pygame.draw.rect(self.screen, self.WHITE, 
                        (self.network_panel_x, self.network_panel_y,
                         self.network_panel_width, self.network_panel_height))
        pygame.draw.rect(self.screen, self.BLACK, 
                        (self.network_panel_x, self.network_panel_y,
                         self.network_panel_width, self.network_panel_height), 2)
        
        # Calcula as posições dos nós
        input_nodes = 4
        output_nodes = 3
        hidden_nodes = len(net.node_evals) - input_nodes - output_nodes
        
        # Espaçamento entre nós
        input_spacing = self.network_panel_height / (input_nodes + 1)
        output_spacing = self.network_panel_height / (output_nodes + 1)
        hidden_spacing = self.network_panel_height / (hidden_nodes + 1) if hidden_nodes > 0 else 0
        
        # Desenha os nós de entrada
        input_x = self.network_panel_x + 50
        for i in range(input_nodes):
            y = self.network_panel_y + input_spacing * (i + 1)
            # Cor baseada no valor da entrada
            value = state[i]
            color = (int(255 * (1 - value)), int(255 * value), 0)
            pygame.draw.circle(self.screen, color, (input_x, int(y)), self.node_radius)
            
            # Rótulo da entrada
            font = pygame.font.Font(None, 20)
            labels = ["Y Dino", "Dist", "Alt", "Y Obs"]
            text = font.render(labels[i], True, self.BLACK)
            self.screen.blit(text, (input_x - 30, int(y) - 10))
            
        # Desenha os nós de saída
        output_x = self.network_panel_x + self.network_panel_width - 50
        for i in range(output_nodes):
            y = self.network_panel_y + output_spacing * (i + 1)
            # Cor baseada na ação escolhida
            color = self.GREEN if i == action else self.BLUE
            pygame.draw.circle(self.screen, color, (output_x, int(y)), self.node_radius)
            
            # Rótulo da saída
            font = pygame.font.Font(None, 20)
            labels = ["Nada", "Pular", "Agachar"]
            text = font.render(labels[i], True, self.BLACK)
            self.screen.blit(text, (output_x + 20, int(y) - 10))
            
        # Desenha os nós ocultos e conexões
        if hidden_nodes > 0:
            hidden_x = (input_x + output_x) // 2
            for i, (node_id, activation_function, aggregation_function, bias, response, links) in enumerate(net.node_evals):
                if i >= input_nodes and i < input_nodes + hidden_nodes:
                    y = self.network_panel_y + hidden_spacing * (i - input_nodes + 1)
                    pygame.draw.circle(self.screen, self.YELLOW, (hidden_x, int(y)), self.node_radius)
                    
                    # Desenha conexões
                    for in_node_id, weight in links:
                        if in_node_id is not None:
                            # Cor da conexão baseada no peso
                            color = (min(255, int(255 * abs(weight))), 
                                    min(255, int(255 * (1 - abs(weight)))), 0)
                            
                            # Desenha a linha da conexão
                            start_x = input_x if in_node_id < input_nodes else hidden_x
                            start_y = self.network_panel_y + input_spacing * (in_node_id + 1)
                            end_x = hidden_x if i < input_nodes + hidden_nodes else output_x
                            end_y = y
                            
                            pygame.draw.line(self.screen, color, 
                                           (start_x, int(start_y)), 
                                           (end_x, int(end_y)), 
                                           self.connection_width)
        
    def render(self, net=None, state=None, action=None):
        """Renderiza o estado atual do jogo e a rede neural"""
        try:
            self.screen.fill(self.WHITE)
            
            # Desenha todos os dinos
            for dino in self.dinos:
                if dino['alive']:
                    self._draw_dino(dino)
                    
            self._draw_obstacles()
            self._draw_score()
            
            # Desenha a rede neural se fornecida
            if net is not None and state is not None and action is not None:
                self._draw_network(net, state, action)
            
            pygame.display.flip()
            self.clock.tick(60)
        except pygame.error:
            return
        
    def close(self):
        """Fecha o jogo e limpa os recursos"""
        if pygame.get_init():
            pygame.quit() 