# -*- coding: utf-8 -*-
from groq import Groq
import os

# Configure via variável de ambiente (evita chave hardcoded no código)
# Aceita `GROQ_API_KEY` (preferido) ou `API_KEY` (fallback).
API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("API_KEY") or ""

client = None
if isinstance(API_KEY, str) and API_KEY.startswith("gsk_"):
    client = Groq(api_key=API_KEY)

historico_conversa = []

def gerar_briefing_vibrante(rota_final):
    """Gera o texto inicial para o Popup."""
    if not client:
        return "Configure sua API KEY da Groq no arquivo ai_advisor.py para ativar a IA."

    itinerario = [f"{i+1}º: {p.codigo} - Prioridade: {p.prioridade}" for i, p in enumerate(rota_final)]
    corpo = "\n".join(itinerario)
    
    prompt = f"""
    Você é o coordenador de logística do programa Saúde da Mulher na Ceilândia. 
    A enfermeira Maitê percorrerá esta rota otimizada:
    {corpo}
    
    Gere um briefing curto, profissional e motivador. 
    Use parágrafos claros e pontuação correta. Máximo 100 palavras.
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Rota otimizada! (Falha na conexão com a IA: {e})"

def inicializar_chat(rota_final):
    """Prepara o contexto para o chat interativo."""
    global historico_conversa
    itinerario = [f"{i+1}º: {p.codigo}" for i, p in enumerate(rota_final)]
    resumo = "\n".join(itinerario)
    
    historico_conversa = [{
        "role": "system",
        "content": f"Você é o assistente da Saúde da Mulher em Ceilândia. Rota atual: {resumo}. Responda dúvidas logísticas de forma curta e gentil."
    }]

def enviar_mensagem_chat(mensagem_usuario):
    """Processa as perguntas do usuário e retorna a resposta da Llama."""
    global historico_conversa
    if not client: return "Chave API não configurada."
    
    historico_conversa.append({"role": "user", "content": mensagem_usuario})
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=historico_conversa,
            temperature=0.7
        )
        resposta = completion.choices[0].message.content
        historico_conversa.append({"role": "assistant", "content": resposta})
        return resposta
    except Exception as e:
        return f"Erro ao processar resposta: {e}"