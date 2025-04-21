import os
import neat
import pickle
import pygame
import time
import matplotlib.pyplot as plt
import numpy as np
from dino import DinoGame

def save_frame(screen, frame_count):
    """Salva o frame atual em um arquivo PNG"""
    # Cria a pasta frames se não existir
    frames_dir = os.path.join(os.path.dirname(__file__), 'frames')
    os.makedirs(frames_dir, exist_ok=True)
    
    # Cria o caminho completo do arquivo
    frame_path = os.path.join(frames_dir, f'frame_{frame_count:04d}.png')
    
    try:
        pygame.image.save(screen, frame_path)
    except pygame.error as e:
        print(f"Erro ao salvar frame: {e}")
        return False
    return True

def plot_fitness_history(stats):
    """
    Plota o gráfico da evolução do fitness ao longo das gerações.
    
    O gráfico mostra:
    - Fitness médio da população (linha azul)
    - Melhor fitness encontrado (linha laranja)
    - Fitness mínimo (linha verde)
    - Número de espécies (linha roxa)
    """
    # Obtém os dados do histórico
    generation = range(len(stats.most_fit_genomes))
    best_fitness = [c.fitness for c in stats.most_fit_genomes]
    avg_fitness = stats.get_fitness_mean()
    min_fitness = stats.get_fitness_min()
    num_species = [len(s) for s in stats.get_species_sizes()]
    
    # Cria o gráfico
    plt.figure(figsize=(12, 8))
    
    # Gráfico de fitness
    plt.subplot(2, 1, 1)
    plt.plot(generation, best_fitness, 'orange', label='Melhor Fitness')
    plt.plot(generation, avg_fitness, 'blue', label='Fitness Médio')
    plt.plot(generation, min_fitness, 'green', label='Fitness Mínimo')
    plt.title('Evolução do Fitness ao Longo das Gerações')
    plt.xlabel('Geração')
    plt.ylabel('Fitness')
    plt.grid(True)
    plt.legend()
    
    # Gráfico de espécies
    plt.subplot(2, 1, 2)
    plt.plot(generation, num_species, 'purple', label='Número de Espécies')
    plt.title('Evolução do Número de Espécies')
    plt.xlabel('Geração')
    plt.ylabel('Número de Espécies')
    plt.grid(True)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('fitness_evolution.png')
    plt.close()

def analyze_learning(stats):
    """
    Analisa o aprendizado das espécies e gera um relatório.
    """
    # Calcula métricas de aprendizado
    best_fitness = [c.fitness for c in stats.most_fit_genomes]
    avg_fitness = stats.get_fitness_mean()
    num_species = [len(s) for s in stats.get_species_sizes()]
    
    # Calcula taxa de melhoria
    improvement_rate = []
    for i in range(1, len(best_fitness)):
        improvement_rate.append((best_fitness[i] - best_fitness[i-1]) / best_fitness[i-1] * 100)
    
    # Gera relatório
    with open('learning_report.txt', 'w') as f:
        f.write("Relatório de Aprendizado\n")
        f.write("=======================\n\n")
        
        f.write(f"Melhor Fitness Final: {best_fitness[-1]:.2f}\n")
        f.write(f"Fitness Médio Final: {avg_fitness[-1]:.2f}\n")
        f.write(f"Número Final de Espécies: {num_species[-1]}\n\n")
        
        f.write("Taxa de Melhoria por Geração:\n")
        for i, rate in enumerate(improvement_rate):
            f.write(f"Geração {i+1}: {rate:.2f}%\n")
        
        f.write("\nAnálise:\n")
        if improvement_rate[-1] > 0:
            f.write("O aprendizado está progredindo positivamente.\n")
        else:
            f.write("O aprendizado pode estar estagnando.\n")
        
        if num_species[-1] > 1:
            f.write("Há diversidade genética sendo mantida.\n")
        else:
            f.write("A diversidade genética pode estar diminuindo.\n")

def eval_genomes(genomes, config):
    """
    Função de avaliação dos genomas (redes neurais) da população.
    
    Esta função é chamada para cada geração do algoritmo NEAT e é responsável por:
    1. Criar uma instância do jogo com múltiplos dinossauros
    2. Avaliar cada genoma individualmente
    3. Atribuir uma pontuação de fitness baseada no desempenho
    
    Parâmetros:
    - genomes: Lista de tuplas (genome_id, genome) contendo os genomas a serem avaliados
    - config: Configuração do NEAT contendo parâmetros da rede neural
    """
    game = DinoGame(num_dinos=len(genomes))
    frame_count = 0
    
    # Cria as redes neurais para cada genoma
    nets = []
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0
    
    # Reseta o jogo para o estado inicial
    state = game.reset()
    done = False
    
    # Loop principal do jogo
    while not done:
        # Obtém as ações de todos os dinossauros vivos
        actions = []
        for i, (genome_id, genome) in enumerate(genomes):
            if game.dinos[i]['alive']:
                output = nets[i].activate(state)
                # Escolhe a ação com maior probabilidade
                action = output.index(max(output))
                actions.append(action)
            else:
                actions.append(0)  # Ação neutra para dinos mortos
        
        # Executa um passo do jogo
        state, reward, done = game.step(actions)
        
        # Atualiza o fitness dos genomas
        for i, (genome_id, genome) in enumerate(genomes):
            if game.dinos[i]['alive']:
                genome.fitness = game.dinos[i]['fitness']
        
        # Renderiza o jogo e a rede neural do primeiro dino vivo
        for i, dino in enumerate(game.dinos):
            if dino['alive']:
                game.render(nets[i], state, actions[i])
                break
        else:
            game.render()
            
        # Salva o frame
        if not save_frame(game.screen, frame_count):
            print(f"Erro ao salvar frame {frame_count}")
        frame_count += 1
        
        # Adiciona um pequeno delay para visualização
        pygame.time.delay(10)
        
    # Fecha o jogo após avaliar todos os genomas
    game.close()

def run_neat(config_file):
    """
    Função principal que executa o algoritmo NEAT.
    
    Esta função é responsável por:
    1. Carregar a configuração do NEAT
    2. Criar a população inicial
    3. Configurar os reportes de progresso
    4. Executar o algoritmo por um número de gerações
    5. Salvar o melhor genoma encontrado
    
    O processo de treinamento funciona da seguinte forma:
    1. Cria uma população inicial de genomas aleatórios
    2. Para cada geração:
       - Avalia todos os genomas usando eval_genomes
       - Seleciona os melhores genomas para reprodução
       - Cria uma nova geração através de mutação e crossover
       - Repete o processo até atingir o critério de parada
    """
    # Carrega a configuração do NEAT
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)

    # Cria a população inicial
    p = neat.Population(config)
    
    # Adiciona reportes para monitorar o progresso
    p.add_reporter(neat.StdOutReporter(True))  # Mostra progresso no console
    stats = neat.StatisticsReporter()  # Coleta estatísticas do treinamento
    p.add_reporter(stats)

    # Executa o algoritmo NEAT por 50 gerações
    # O algoritmo irá:
    # 1. Avaliar cada genoma
    # 2. Selecionar os melhores
    # 3. Criar uma nova geração
    # 4. Repetir até atingir 50 gerações ou o critério de parada
    winner = p.run(eval_genomes, 50)

    # Salva o melhor genoma encontrado
    with open('best_genome.pkl', 'wb') as f:
        pickle.dump(winner, f)
        
    # Plota o gráfico da evolução do fitness
    plot_fitness_history(stats)
    
    # Analisa o aprendizado
    analyze_learning(stats)

def create_video():
    """
    Cria um vídeo a partir dos frames salvos usando ffmpeg.
    O vídeo será salvo como 'training.mp4' com 30 FPS.
    """
    import subprocess
    
    # Obtém o caminho da pasta frames
    frames_dir = os.path.join(os.path.dirname(__file__), 'frames')
    
    # Comando ffmpeg para criar o vídeo
    cmd = [
        'ffmpeg',
        '-framerate', '30',  # 30 FPS
        '-i', os.path.join(frames_dir, 'frame_%04d.png'),  # Padrão dos arquivos de frame
        '-c:v', 'libx264',  # Codec de vídeo
        '-pix_fmt', 'yuv420p',  # Formato de pixel
        '-y',  # Sobrescrever arquivo se existir
        os.path.join(os.path.dirname(__file__), 'training.mp4')  # Nome do arquivo de saída
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("Vídeo criado com sucesso: training.mp4")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao criar vídeo: {e}")
    except FileNotFoundError:
        print("ffmpeg não encontrado. Por favor, instale o ffmpeg e adicione ao PATH.")

if __name__ == '__main__':
    """
    Ponto de entrada do programa.
    
    Inicializa o Pygame e executa o treinamento NEAT.
    O treinamento irá:
    1. Criar uma população inicial de redes neurais
    2. Treinar por 50 gerações
    3. Salvar o melhor agente encontrado
    4. Criar um vídeo do treinamento
    5. Gerar gráfico da evolução do fitness
    """
    pygame.init()
    run_neat(os.path.join(os.path.dirname(__file__), 'neat-config.txt'))
    create_video()
    pygame.quit()
