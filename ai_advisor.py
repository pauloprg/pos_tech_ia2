# -*- coding: utf-8 -*-
from groq import Groq
import os

# Use somente variável de ambiente
API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("API_KEY") or ""

client = None
if isinstance(API_KEY, str) and API_KEY.startswith("gsk_"):
    client = Groq(api_key=API_KEY)

historico_conversa = []


def _contar_criticos(rotas):
    total = 0
    for rota in rotas:
        for atendimento in rota.get("atendimentos", []):
            if atendimento.get("prioridade") == 4:
                total += 1
    return total


def _somar_paradas(rotas):
    total = 0
    for rota in rotas:
        total += len(rota.get("atendimentos", []))
    return total


def _formatar_rotas_para_prompt(rotas):
    blocos = []

    for idx_rota, rota in enumerate(rotas, start=1):
        cabecalho = f"""
ROTA {idx_rota}
Veículo: {rota.get("veiculo", "N/A")}
Tipo do veículo: {rota.get("tipo", "N/A")}
Distância estimada: {rota.get("distancia_km", 0)} km
Quantidade de paradas: {rota.get("paradas", 0)}
Carga total: {rota.get("carga", 0)}
"""
        atendimentos_txt = []

        for idx_at, atendimento in enumerate(rota.get("atendimentos", []), start=1):
            atendimentos_txt.append(
                f"""
Parada {idx_at}:
- Código: {atendimento.get("codigo", "N/A")}
- Tipo: {atendimento.get("tipo", "N/A")}
- Prioridade: {atendimento.get("prioridade", "N/A")}
"""
            )

        bloco = cabecalho + "\n".join(atendimentos_txt)
        blocos.append(bloco)

    return "\n\n".join(blocos)


def gerar_roteiro_inteligente(rotas):
    if not client:
        return "Configure a variável de ambiente GROQ_API_KEY para ativar a análise de rota."

    if not rotas:
        return "Nenhuma rota disponível para análise."

    corpo = _formatar_rotas_para_prompt(rotas)
    total_atendimentos = _somar_paradas(rotas)
    total_criticos = _contar_criticos(rotas)
    total_distancia = sum(float(rota.get("distancia_km", 0) or 0) for rota in rotas)

    prompt = f"""
Você é um coordenador logístico especialista em operações de saúde pública voltadas à saúde da mulher.

Analise as rotas abaixo e transforme em um roteiro operacional claro, prático e objetivo para a equipe de campo.

Contexto:
- O sistema trabalha com múltiplos veículos
- Existem atendimentos com prioridades diferentes
- Prioridade 4 = Emergência obstétrica
- Prioridade 3 = Violência doméstica
- Prioridade 2 = Medicamento hormonal
- Prioridade 1 = Pós-parto

Regras:
- Seja direto, claro e profissional
- Organize por veículo
- Destaque atendimentos críticos
- Aponte riscos operacionais
- Indique quais rotas exigem mais atenção
- Não invente dados que não estejam informados

Inclua obrigatoriamente:
1. Resumo executivo geral
2. Sequência operacional por veículo
3. Destaque de atendimentos críticos
4. Alertas logísticos relevantes
5. Resumo final com:
   - total de atendimentos
   - total de atendimentos críticos
   - total estimado de distância

Totais calculados:
- Total de atendimentos: {total_atendimentos}
- Total de críticos: {total_criticos}
- Distância total estimada: {round(total_distancia, 2)} km

DADOS DAS ROTAS:
{corpo}
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erro IA: {e}"


def inicializar_chat(rotas):
    global historico_conversa

    if not rotas:
        historico_conversa = [
            {
                "role": "system",
                "content": "Você é um assistente logístico. Não há rotas disponíveis no momento."
            }
        ]
        return

    linhas = []
    for idx_rota, rota in enumerate(rotas, start=1):
        linhas.append(
            f"Rota {idx_rota} | Veículo: {rota.get('veiculo', 'N/A')} | Tipo: {rota.get('tipo', 'N/A')} | Distância: {rota.get('distancia_km', 0)} km"
        )

        for idx_at, atendimento in enumerate(rota.get("atendimentos", []), start=1):
            linhas.append(
                f"  - Parada {idx_at}: {atendimento.get('codigo', 'N/A')} | {atendimento.get('tipo', 'N/A')} | prioridade {atendimento.get('prioridade', 'N/A')}"
            )

    resumo = "\n".join(linhas)

    historico_conversa = [
        {
            "role": "system",
            "content": f"""
Você é um assistente logístico inteligente especializado em operações de saúde da mulher.

REGRAS FIXAS DE PRIORIDADE:
- 4 = prioridade MAIS ALTA (Emergência obstétrica)
- 3 = alta (Violência doméstica)
- 2 = média (Medicamento hormonal)
- 1 = baixa (Pós-parto)

Você tem acesso às rotas abaixo:

{resumo}

Você deve:
- responder perguntas em linguagem natural
- identificar a rota mais crítica
- dizer qual veículo atende casos mais sensíveis
- contar quantos atendimentos existem por prioridade
- explicar qual é o próximo atendimento crítico
- resumir a operação por veículo

Exemplos:
- "Qual rota está com mais atendimentos críticos?"
- "Qual veículo atende emergência obstétrica?"
- "Quantos casos de violência doméstica existem?"
- "Qual a prioridade mais alta?"
- "Qual o próximo atendimento prioritário?"

Responda sempre de forma objetiva, útil e operacional.
"""
        }
    ]


def enviar_mensagem_chat(mensagem_usuario):
    global historico_conversa

    if not client:
        return "Erro: IA não configurada."

    historico_conversa.append({
        "role": "user",
        "content": mensagem_usuario
    })

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=historico_conversa,
            temperature=0.4
        )

        resposta = completion.choices[0].message.content

        historico_conversa.append({
            "role": "assistant",
            "content": resposta
        })

        return resposta

    except Exception as e:
        return f"Falha na resposta: {e}"