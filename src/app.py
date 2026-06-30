"""
app.py

Aplicação principal do Nomad: assistente de educação financeira pessoal.

Roda com:
    streamlit run app.py

Pré-requisitos:
    - Ollama instalado e rodando (https://ollama.com)
    - Um modelo baixado, ex: `ollama pull llama3`
    - Dependências do requirements.txt instaladas
"""

import streamlit as st
import ollama

from knowledge_base import KnowledgeBase
from financas import calcular_saldo, montar_resumo_cliente, CATEGORIAS_PADRAO

MODEL_NAME = "llama3"  # troque pelo modelo que você baixou no Ollama

SYSTEM_PROMPT = """Você é Nomad, um agente de educação financeira pessoal especializado em ajudar
iniciantes a organizar sua renda mensal e dar os primeiros passos rumo a uma
reserva e a investimentos.

Seu objetivo é, a partir da renda e dos gastos fixos informados pelo usuário
(aluguel, alimentação, remédios, seguro-saúde, lazer, contas), calcular o saldo
disponível no mês e orientar como distribuí-lo entre reserva de emergência,
gastos essenciais e investimentos, de acordo com o perfil de risco do usuário
(conservador, moderado ou agressivo). O objetivo central é sempre garantir que
sobre algum valor no mês para guardar ou investir.

PERSONALIDADE E TOM:
- Educativo, acessível e informal — nunca técnico ou intimidador
- Sempre educado e sem julgamentos em relação aos gastos do usuário
- Explica conceitos financeiros de forma simples, usando analogias do dia a dia,
  parábolas (ex: "O Homem Mais Rico da Babilônia") ou comparações práticas
  sempre que ajudar na compreensão

REGRAS:
1. Sempre baseie suas respostas nos dados fornecidos pelo próprio usuário
   e no contexto da base de conhecimento fornecido abaixo. Nunca invente
   números ou fatos financeiros.
2. Nunca recomende investimentos específicos. Você pode comparar opções que
   o próprio usuário trouxer, mas a decisão final é sempre dele.
3. Nunca acesse, solicite ou compartilhe dados bancários sensíveis.
4. Se o assunto envolver declaração de Imposto de Renda, oriente o usuário a
   procurar um contador para esclarecimentos especializados.
5. Se não souber algo ou a pergunta estiver fora do escopo de finanças
   pessoais, admita a limitação de forma educada e redirecione a conversa.
6. Nunca substitua a orientação de um profissional certificado.
"""


@st.cache_resource(
    show_spinner="Carregando base de conhecimento (pode levar um tempo na primeira vez)..."
)
def carregar_base_conhecimento():
    return KnowledgeBase()


def montar_prompt_completo(pergunta_usuario: str, resumo_cliente: str, kb: KnowledgeBase) -> list:
    """Monta a lista de mensagens enviada ao LLM, incluindo system prompt,
    dados do cliente e contexto recuperado via RAG."""

    contexto_rag = kb.build_context(pergunta_usuario, top_k=2)

    system_completo = f"""{SYSTEM_PROMPT}

{resumo_cliente}

Trechos relevantes da base de conhecimento de finanças pessoais:
{contexto_rag}
"""

    return [
        {"role": "system", "content": system_completo},
        {"role": "user", "content": pergunta_usuario},
    ]


def main():
    """Função principal que renderiza a interface do Streamlit."""
    st.set_page_config(page_title="Nomad - Assistente Financeiro", page_icon="💰")
    st.title("💰 Nomad")
    st.caption("Seu assistente de educação financeira pessoal")

    # --- Sidebar: dados do cliente ---
    with st.sidebar:
        st.header("Seus dados financeiros")

        renda = st.number_input("Renda mensal (R$)", min_value=0.0, step=100.0, value=3000.0)

        st.subheader("Gastos fixos")
        gastos = {}
        for categoria in CATEGORIAS_PADRAO:
            gastos[categoria] = st.number_input(
                categoria, min_value=0.0, step=50.0, value=0.0, key=f"gasto_{categoria}"
            )

        perfil = st.selectbox(
            "Perfil de risco", ["Conservador", "Moderado", "Agressivo"]
        )

        saldo = calcular_saldo(renda, gastos)
        st.metric("Saldo disponível no mês", f"R$ {saldo:,.2f}")

    # --- Base de conhecimento (RAG) ---
    kb = carregar_base_conhecimento()

    # --- Histórico de chat ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # --- Input do usuário ---
    if pergunta := st.chat_input("Digite sua mensagem..."):
        st.session_state.messages.append({"role": "user", "content": pergunta})
        with st.chat_message("user"):
            st.write(pergunta)

        resumo_cliente = montar_resumo_cliente(renda, gastos, perfil)
        mensagens_llm = montar_prompt_completo(pergunta, resumo_cliente, kb)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                resposta = ollama.chat(model=MODEL_NAME, messages=mensagens_llm)
                texto_resposta = resposta["message"]["content"]
            st.write(texto_resposta)

        st.session_state.messages.append({"role": "assistant", "content": texto_resposta})


if __name__ == "__main__":
    main()
