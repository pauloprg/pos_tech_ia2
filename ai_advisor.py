# -*- coding: utf-8 -*-
from groq import Groq
import os

# Tenta pegar a chave de diferentes fontes de ambiente
API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("API_KEY") or ""

client = None
if isinstance(API_KEY, str) and API_KEY.startswith("gsk_"):
    client = Groq(api_key=API_KEY)

historico_conversa = []

def gerar_briefing_vibrante(rota_final):
    """Gera o texto inicial para o Popup com base nos dados reais da rota."""
    if not client:
        return "Configure sua API KEY da Groq para ativar a análise de rota."

    # MONTAGEM DO ITINERÁRIO REAL PARA A IA
    itinerario = [
        f"{i+1}º: {p.codigo} | Atendimento: {p.tipo_atendimento} | Prioridade: {p.prioridade}" 
        for i, p in enumerate(rota_final)
    ]
    corpo = "\n".join(itinerario)
    
    prompt = f"""
    Você é o coordenador de logística do programa Saúde da Mulher na Ceilândia. 
    A enfermeira Maitê percorrerá esta rota otimizada:
    
    {corpo}
    
    Com base nos tipos de atendimento e prioridades acima, gere um briefing curto (máx 100 palavras).
    Destaque os casos de Prioridade 4 (Críticos). Seja profissional e encorajador.
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Rota otimizada com sucesso! (Erro de conexão IA: {e})"

def inicializar_chat(rota_final):
    """Contextualiza o chat com os dados reais de atendimento."""
    global historico_conversa
    itinerario = [f"{p.codigo}: {p.tipo_atendimento}" for p in rota_final]
    resumo = ", ".join(itinerario)
    
    historico_conversa = [{
        "role": "system",
        "content": f"Você é o assistente logístico. A rota da Maitê possui estes atendimentos: {resumo}. Responda dúvidas sobre a ordem e o tipo de serviço de cada ponto."
    }]

def enviar_mensagem_chat(mensagem_usuario):
    global historico_conversa
    if not client: return "Erro: IA não configurada."
    
    historico_conversa.append({"role": "user", "content": mensagem_usuario})
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=historico_conversa
        )
        resposta = completion.choices[0].message.content
        historico_conversa.append({"role": "assistant", "content": resposta})
        return resposta
    except Exception as e:
        return f"Falha na resposta: {e}"