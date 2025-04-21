# Dino Game com NEAT

Este projeto implementa um agente de inteligência artificial usando o algoritmo NEAT (NeuroEvolution of Augmenting Topologies) para jogar o clássico jogo do Dino do Chrome.

## 🦖 Sobre o Projeto

O projeto utiliza o algoritmo NEAT para evoluir redes neurais que controlam um dinossauro virtual, ensinando-o a pular e agachar para evitar obstáculos. A implementação inclui:

- Ambiente de jogo personalizado usando Pygame
- Visualização em tempo real da rede neural
- Sistema de pontuação e dificuldade progressiva
- Múltiplos dinossauros evoluindo simultaneamente

## 🚀 Requisitos

- Python 3.x
- Pygame
- NEAT-Python

## 📦 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/DinoChrome.git
cd DinoChrome
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 🎮 Como Jogar

1. Execute o script principal:
```bash
python dino_neat/dino.py
```

2. O jogo iniciará automaticamente com múltiplos dinossauros evoluindo simultaneamente.

## 🧠 Funcionalidades

- **Evolução Neural**: Os dinossauros aprendem através de gerações sucessivas
- **Visualização da Rede**: Painel lateral mostrando a rede neural em tempo real
- **Obstáculos Dinâmicos**: Diferentes tipos de obstáculos com alturas variadas
- **Sistema de Pontuação**: Pontuação baseada na sobrevivência e ações corretas
- **Dificuldade Progressiva**: Velocidade aumenta conforme a pontuação

## 📊 Estado do Jogo

O estado do jogo é representado por 4 entradas para a rede neural:
1. Posição vertical do dinossauro
2. Distância até o obstáculo mais próximo
3. Altura do obstáculo
4. Posição vertical do obstáculo

## 🎯 Ações

A rede neural pode escolher entre 3 ações:
1. Nada
2. Pular
3. Agachar

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias
- Enviar pull requests

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes. 