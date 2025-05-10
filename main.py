import streamlit as st
from app.interfaces.llm_interface import ask_llm



st.set_page_config(page_title="Revisão Inteligente", page_icon="📚")
st.title("🧠 Alice MentorAI ,IA para Revisão de Concursos")

# Aplicar estilos de CSS à página (se houver)
try:
    with open("static/styles.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("Arquivo de estilo CSS não encontrado!")

    
st.markdown(
    """
    Digite seu resumo ou conteúdo de estudo.  
    A IA irá indicar o **melhor método de revisão**: flashcards, mapas mentais, questões, etc.
    """
)

# Seletor de tom
tone = st.selectbox(
    "🎯 Escolha o tom da resposta da IA:",
    ["Técnico", "Motivacional", "Divertido"]
)

# Inicializa histórico
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada do usuário
if prompt := st.chat_input("Digite seu conteúdo de estudo aqui..."):
    # Adiciona prompt do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Ajusta prompt com base no tom selecionado
    if tone == "Técnico":
        tone_prompt = (
            "Responda com uma análise objetiva e fundamentada em métodos de aprendizado eficazes para concursos."
        )
    elif tone == "Motivacional":
        tone_prompt = (
            "Responda com energia positiva, incentivando a pessoa e indicando métodos eficazes de revisão."
        )
    elif tone == "Divertido":
        tone_prompt = (
            "Responda com bom humor, mantendo a clareza, e recomende formas divertidas de revisar o conteúdo."
        )

    full_prompt = f"{tone_prompt}\n\nConteúdo:\n{prompt}"

    with st.chat_message("assistant"):
        with st.spinner("⚙️ Processando seu material com foco em métodos de revisão eficientes..."):
            response = ask_llm(full_prompt)
            st.markdown(f"**Alice MentorAI:** {response}")

    # Adiciona resposta da IA
    st.session_state.messages.append({"role": "assistant", "content": response})
