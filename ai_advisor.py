# -*- coding: utf-8 -*-
from groq import Groq
import os

# Tenta pegar a chave de diferentes fontes de ambiente
API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("API_KEY") or ""

client = None
if isinstance(API_KEY, str) and API_KEY.startswith("gsk_"):
    client = Groq(api_key=API_KEY)

historico_conversa = []

def gerar_roteiro_inteligente(rota_final):
    if not client:
        return "Configure sua API KEY da Groq para ativar a análise de rota."

    roteiro = []
    for i, p in enumerate(rota_final):
        roteiro.append(
            f"""
Parada {i+1}:
- Código: {p.codigo}
- Tipo: {p.tipo_atendimento}
- Prioridade: {p.prioridade}
- Tempo estimado atendimento: {p.tempo_atendimento}h
- Janela: {p.tempo_inicio}h às {p.tempo_fim}h
- Quantidade: {p.quantidade}
- Refrigeração: {"Sim" if p.temperatura_controlada else "Não"}
- Protocolo especial: {"Sim" if p.protocolo_especial else "Não"}
"""
        )

    corpo = "\n".join(roteiro)

    prompt = f"""
Você é um coordenador logístico especialista em operações de saúde pública.

Transforme a lista de paradas abaixo em um roteiro operacional claro e prático para a equipe de campo.

Regras:
- Seja direto, objetivo e organizado
- Use linguagem simples e profissional
- Destaque atendimentos críticos (prioridade 4)
- Estruture como um roteiro de execução

Inclua obrigatoriamente:

1. Sequência das visitas (passo a passo)
2. Tipo de atendimento em cada parada
3. Informações relevantes (tempo, cuidados, restrições)
4. Alertas importantes (ex: prioridade alta, protocolo especial)
5. Resumo final com:
   - total de atendimentos
   - quantos são críticos
   - tempo estimado total

DADOS DA ROTA:
{corpo}
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erro IA: {e}"
    

def inicializar_chat(rota_final):
    global historico_conversa

    dados = []
    for i, p in enumerate(rota_final):
        dados.append(
            f"{i+1}: {p.codigo} | {p.tipo_atendimento} | prioridade {p.prioridade}"
        )

    resumo = "\n".join(dados)

    historico_conversa = [
        {
            "role": "system",
            "content": f"""
Você é um assistente logístico inteligente.

Você tem acesso à rota abaixo:

{resumo}

Você deve:
- Responder perguntas em linguagem natural
- Identificar prioridades
- Saber qual é o próximo atendimento
- Contar tipos de ocorrências
- Sugerir decisões operacionais

Exemplos de perguntas que você deve responder:
- "Qual o próximo atendimento prioritário?"
- "Quantas emergências temos hoje?"
- "Qual parada exige mais atenção?"
- "Qual o tempo total estimado?"

Responda sempre de forma objetiva e útil para a equipe.
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
            temperature=0.4  # mais consistente
        )

        resposta = completion.choices[0].message.content

        historico_conversa.append({
            "role": "assistant",
            "content": resposta
        })

        return resposta

    except Exception as e:
        return f"Falha na resposta: {e}"