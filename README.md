# 🚑 VRP para Saúde da Mulher com Algoritmos Genéticos + IA

Este projeto implementa uma solução avançada de **roteirização de veículos (VRP - Vehicle Routing Problem)** aplicada ao contexto de **saúde da mulher**, utilizando **Algoritmos Genéticos** e integração com **Modelos de Linguagem (LLMs)** para apoio operacional.

---

## 🎯 Objetivo

O sistema simula a distribuição de atendimentos domiciliares e medicamentos especializados, considerando:

- Emergências obstétricas  
- Casos de violência doméstica  
- Medicamentos hormonais (cadeia fria)  
- Atendimento pós-parto  

A solução busca **otimizar rotas respeitando restrições reais**, priorizando **eficiência logística e criticidade clínica**.

---

## 🧠 Principais Tecnologias

- 🧬 Algoritmos Genéticos (customizados para VRP)
- 🗺️ Pygame (visualização interativa)
- 🤖 LLM (Groq / LLaMA 3) para análise de rotas
- 🐍 Python 3.11+

---

## 🏗️ Arquitetura do Projeto

pos_tech_ia2/
│
├── main.py                 # Execução principal + UI
├── vrp_genetic.py          # Algoritmo Genético (núcleo)
├── pontos.py               # Modelagem (ServicePoint, Vehicle, Depot)
├── mapa_utils.py           # Geração de dados e frota
├── renderer.py             # Interface gráfica
├── ai_advisor.py           # Integração com LLM
└── dataset/                # Dados sintéticos (coordenadas)

---

## ⚙️ Modelagem do Problema

### 📍 Pontos de Atendimento (`ServicePoint`)

Cada ponto contém:

- Tipo de atendimento
- Prioridade (1 a 4)
- Quantidade de carga
- Janela de tempo
- Necessidade de refrigeração
- Protocolo especial
- Tipos de veículos permitidos

---

### 🚚 Veículos (`Vehicle`)

Cada veículo possui:

- Velocidade (km/h)
- Custo por km
- Capacidade de carga
- Número máximo de paradas
- Distância máxima
- Tipos de atendimento suportados
- Suporte a refrigeração
- Suporte a protocolos especiais

---

### 🧩 Frota Heterogênea

Exemplos:

- 🏍️ Moto → rápida, baixa capacidade  
- 🚐 Van refrigerada → alta capacidade, cadeia fria  
- 🚑 Ambulância → foco em emergências  
- 🚁 Drone → baixo custo, carga limitada  

---

## 🧬 Algoritmo Genético

### 🧬 Codificação

- Cada indivíduo é uma **sequência de pontos**
- Representa uma **ordem global de atendimento**

---

### 🔄 Decodificação (VRP)

A sequência é convertida em múltiplas rotas:

- Distribuição entre veículos
- Validação de restrições
- Tentativa de alocação inteligente

---

### 🎯 Função de Fitness

Minimiza:

- Distância total
- Custo operacional

Penaliza:

- Atendimento não realizado  
- Incompatibilidade veículo-atendimento  
- Excesso de carga  
- Excesso de distância  
- Excesso de paradas  
- Violação de janela de tempo  
- Falha em cadeia fria  
- Falha em protocolo especial  

---

### 🔁 Operadores Genéticos

- Seleção por torneio  
- Crossover por ordem (Order Crossover)  
- Mutação:
  - troca
  - inversão
  - inserção  

---

## 📊 Interface do Sistema

A aplicação apresenta:

- 🗺️ Mapa com rotas desenhadas
- 📋 Lista de atendimentos ordenados
- 📉 Gráfico de evolução do fitness
- 🤖 Chat com IA para análise da solução

---

## 🤖 Integração com IA (LLM)

O sistema utiliza **Groq (LLaMA 3)** para:

- Gerar briefing operacional
- Responder perguntas sobre a rota
- Destacar riscos e prioridades
- Apoiar tomada de decisão

### Exemplo de perguntas:

- "Qual o atendimento mais crítico?"
- "Quantas emergências existem?"
- "Qual rota exige mais atenção?"

---

## ⚖️ Impacto Social e Ética

- Uso de **dados sintéticos** (sem exposição real)
- Priorização de atendimentos críticos
- Consideração de contextos sensíveis (violência, pós-parto)
- IA usada como **suporte à decisão**, não substituição

---

## 🚀 Como Executar

### 1. Clone o repositório

```bash
git clone https://github.com/pauloprg/pos_tech_ia2.git
cd pos_tech_ia2
git checkout mapa_octaviano
```

---

### 2. Instale dependências

```bash
pip install pygame numpy groq
```

---

### 3. Configure a API da Groq

```bash
export GROQ_API_KEY="sua_chave_aqui"
```

ou no Windows:

```bash
set GROQ_API_KEY=sua_chave_aqui
```

---

### 4. Execute o projeto

```bash
python main.py
```

---

## 🎥 Demonstração

O sistema inclui:

- Evolução visual das rotas
- Painel de decisão
- Análise por IA

---

## 💡 Diferenciais do Projeto

- VRP com restrições reais (não apenas TSP)
- Frota heterogênea
- Decodificação inteligente de cromossomos
- Integração com IA para interpretação da solução
- Aplicação com impacto social relevante

---

## 📌 Possíveis Evoluções

- Integração com dados reais (SIG / APIs)
- Otimização multiobjetivo
- Interface web
- Aprendizado adaptativo de penalidades
- Simulação em tempo real

---

## 📄 Licença

Uso acadêmico e educacional.
