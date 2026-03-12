# Sistema de Otimização de Rotas para Atendimento Especializado à Saúde da Mulher

## Descrição do Projeto

Este projeto implementa um sistema de simulação para **otimização de rotas de atendimento especializado voltados à saúde da mulher no Distrito Federal**.

O sistema utiliza como base o **Problema do Caixeiro Viajante (TSP - Traveling Salesman Problem)** e posteriormente evolui para um **Problema de Roteirização de Veículos (VRP)** com restrições específicas do contexto do Tech Challenge.

A aplicação simula atendimentos especializados em diferentes pontos do território do Distrito Federal utilizando um **mapa real como base visual**.

Os pontos de atendimento são gerados aleatoriamente dentro do mapa e representam situações como:

- Emergências obstétricas
- Casos de violência doméstica
- Entrega de medicamentos hormonais
- Atendimento pós-parto

O sistema também apresenta visualmente a **rota de atendimento em tempo real**, juntamente com uma lista detalhada das prioridades.

---

# Objetivo

Desenvolver um sistema que permita **simular e otimizar rotas de atendimento especializado à mulher**, considerando fatores como:

- prioridade de atendimento
- tipo de serviço
- janelas de horário
- demanda de suprimentos

O objetivo é demonstrar como **algoritmos de otimização podem apoiar sistemas de saúde pública**.

---

# Tecnologias Utilizadas

| Tecnologia | Função |
|--------|--------|
| Python | Linguagem principal |
| Pygame | Interface gráfica e visualização do mapa |
| Algoritmos Genéticos | Otimização das rotas |
| NumPy | Manipulação de dados numéricos |

---

# Estrutura do Projeto
pos_tech_ia2/
│
├── assets/
│ └── Mapa_DF.png
│
├── main.py
├── mapa_utils.py
├── pontos.py
├── renderer.py
│
├── requirements.txt
└── README.md


### Descrição dos arquivos

**main.py**

Arquivo principal do sistema.  
Responsável por:

- inicializar o Pygame
- carregar o mapa
- gerar pontos de atendimento
- executar o loop principal da aplicação

---

**pontos.py**

Define as estruturas de dados utilizadas no sistema.

Contém a classe principal:
ServicePoint

Essa classe representa um ponto de atendimento com atributos como:

- posição no mapa
- tipo de atendimento
- prioridade
- demanda
- janela de horário

---

**mapa_utils.py**

Responsável pela lógica relacionada ao mapa.

Funções principais:

- carregar e redimensionar o mapa
- identificar áreas válidas para criação de pontos
- gerar pontos de atendimento aleatórios
- definir janelas de atendimento

---

**renderer.py**

Responsável pela renderização gráfica.

Funções principais:

- desenhar o mapa
- desenhar os pontos de atendimento
- desenhar as rotas
- renderizar o painel lateral com a lista de atendimentos

---

**assets/Mapa_DF.png**

Imagem base do mapa do Distrito Federal utilizada para posicionamento dos pontos.

---

# Funcionamento do Sistema

## 1. Carregamento do mapa

O sistema carrega o mapa do Distrito Federal e o ajusta ao tamanho da janela da aplicação.
map_surface = load_and_scale_map()

---

## 2. Identificação de áreas válidas

O algoritmo percorre todos os pixels do mapa para identificar posições válidas onde um ponto pode ser criado.

Pixels considerados inválidos:

- áreas pretas (fora do mapa)
- regiões de água (lagos e rios)

---

## 3. Geração de pontos de atendimento

Os pontos são gerados aleatoriamente dentro das áreas válidas do mapa.

Cada ponto recebe os atributos relevantes:

- tipo de atendimento
- prioridade
- demanda de suprimentos
- janela de horário

Exemplo de ponto gerado:
Ponto 3
Tipo: Emergência obstétrica
Prioridade: 4
Janela de atendimento: 0h - 23h

---

## 4. Definição da rota inicial

A primeira rota é gerada utilizando ordenação baseada em prioridade:

1. maior prioridade primeiro
2. menor horário de atendimento
3. identificador do ponto

---

## 5. Visualização gráfica

O sistema apresenta:

- mapa do Distrito Federal
- pontos de atendimento coloridos por prioridade
- linhas conectando os pontos da rota
- painel lateral com a sequência de atendimento

---

# Legenda de Prioridades

| Prioridade | Tipo de Atendimento | Cor |
|------|------|------|
| 4 | Emergência obstétrica | Vermelho |
| 3 | Violência doméstica | Laranja |
| 2 | Medicamento hormonal | Azul |
| 1 | Pós-parto | Verde |

---

# Interface do Sistema

A interface é dividida em duas áreas:

### Área esquerda

Mapa do Distrito Federal com:

- pontos de atendimento
- rota visual

### Área direita

Painel com:

- legenda de prioridades
- lista da rota de atendimento
- informações do tipo de atendimento

---

# Como Executar o Projeto

## 1. Clonar ou baixar o projeto
git clone <repositorio>
cd pos_tech_ia2

---

## 2. Instalar dependências
pip install -r requirements.txt

---

## 3. Executar o sistema
python main.py

---

# Exemplo de Execução

Ao executar o sistema, será aberta uma janela contendo:

- mapa do DF
- pontos de atendimento
- rota visual
- lista de atendimento no painel lateral

---

Este projeto foi desenvolvido como parte do **Tech Challenge Fase 2**, com foco na aplicação de **otimização de rotas para atendimento especializado à mulher**, especificamente voltados ao atendimento e à segurança da mulher.

---

# Licença

Projeto desenvolvido para fins educacionais.