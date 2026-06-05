import streamlit as st

st.set_page_config(page_title="Revisão Inteligente", page_icon="📚")
import random
import time
from app.interfaces.llm_interface import ask_llm
import streamlit_cookies_manager as cookie_manager
from PyPDF2 import PdfReader
import docx


# Configuração da página

st.title("🧠 Alice Revisa, IA para Revisão de Concursos")



# Inicialização do estado da sessão
if "progress" not in st.session_state:
    st.session_state.progress = 0
if "cookie_initialized" not in st.session_state:
    st.session_state.cookie_initialized = False
if "user_name" not in st.session_state:
    st.session_state.user_name = "Usuário"
if "long_term_goals" not in st.session_state:
    st.session_state.long_term_goals = []
if "daily_goal" not in st.session_state:
    st.session_state.daily_goal = 1

# ➕ Adicione aqui
if "messages" not in st.session_state:
    st.session_state.messages = []

if "interactions" not in st.session_state:
    st.session_state.interactions = 0


# Inicialização do Cookie Manager
cookies = cookie_manager.CookieManager()

def load_progress():
    if not cookies.ready():
        return st.session_state.progress
    try:
        progress_str = cookies.get("progress")
        if progress_str is not None:
            return int(progress_str)
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar cookies: {str(e)}")
    return st.session_state.progress

def save_progress(progress_value):
    if cookies.ready():
        try:
            cookies["progress"] = str(progress_value)
            cookies.save()
        except Exception as e:
            st.warning(f"⚠️ Erro ao salvar cookies: {str(e)}"

if not cookies.ready():
    if not st.session_state.cookie_initialized:
        st.warning('⚠️ Aguardando inicialização dos cookies...')
        time.sleep(1)
        st.session_state.cookie_initialized = True
        st.rerun()
    progress = st.session_state.progress
else:
    progress = load_progress()

# Estilo
try:
    with open("static/styles.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("Arquivo de estilo CSS não encontrado!")

# Dica de estudo
study_tips = [
    "💡 Faça revisões espaçadas: reveja o conteúdo em 1, 7 e 30 dias.",
    "📚 Divida grandes resumos em partes menores e revise aos poucos.",
    "🧠 Ensine o conteúdo para alguém fictício (Técnica de Feynman).",
    "🎧 Grave resumos em áudio e escute no transporte.",
    "📝 Use flashcards com perguntas objetivas e respostas curtas.",
    "🎯 Revise os erros mais frequentes para fixar melhor.",
    "📅 Use a técnica Pomodoro para manter foco e descansar.",
    "📌 Ao revisar, tente lembrar antes de reler.",
    "🤔 Faça perguntas sobre o conteúdo: o quê? como? por quê?"
]
st.sidebar.markdown("### 💡 Dica de Estudo")
st.sidebar.info(random.choice(study_tips))

# Progresso
st.sidebar.markdown("### 📈 Progresso de Estudo")
st.sidebar.progress(progress / 100)
st.sidebar.write(f"{progress}% concluído")




# Upload de arquivos
st.markdown("### 📂 Envie seu resumo para sugestão automática")
uploaded_file = st.file_uploader("Escolha um arquivo (.pdf, .txt, .docx)", type=["pdf", "txt", "docx"])
extracted_text = ""

if uploaded_file:
    file_type = uploaded_file.name.split('.')[-1]
    if file_type == "pdf":
        reader = PdfReader(uploaded_file)
        extracted_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif file_type == "txt":
        extracted_text = uploaded_file.read().decode("utf-8")
    elif file_type == "docx":
        doc = docx.Document(uploaded_file)
        extracted_text = "\n".join([para.text for para in doc.paragraphs])
    
    st.markdown("#### 📝 Conteúdo Extraído:")
    st.text_area("Conteúdo extraído do arquivo:", extracted_text, height=200)

    if len(extracted_text.split()) > 200:
        st.info("🔍 Conteúdo longo detectado. Gerando resumo antes de sugerir método de revisão...")
        with st.spinner("Resumindo conteúdo..."):
            summary_prompt = f"Resuma o seguinte conteúdo de forma objetiva e clara para fins de revisão de concursos:\n\n{extracted_text}"
            extracted_text = ask_llm(summary_prompt)
        st.success("✅ Resumo gerado automaticamente:")
        st.text_area("Resumo:", extracted_text, height=200)

st.markdown("""
Digite seu resumo ou conteúdo de estudo.  
A IA irá indicar o **melhor método de revisão**: flashcards, mapas mentais, questões, etc.
""")

tone = st.selectbox("🎯 Escolha o tom da resposta da IA:", ["Técnico", "Motivacional", "Divertido"])

# Histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input manual ou de upload
prompt = st.chat_input("Digite seu conteúdo de estudo aqui...") or (extracted_text if extracted_text else "")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    tone_prompt = {
        "Técnico": "Responda com uma análise objetiva e fundamentada em métodos de aprendizado eficazes para concursos.",
        "Motivacional": "Responda com energia positiva, incentivando a pessoa e indicando métodos eficazes de revisão.",
        "Divertido": "Responda com bom humor, mantendo a clareza, e recomende formas divertidas de revisar o conteúdo."
    }[tone]

    full_prompt = f"{tone_prompt}\n\nConteúdo:\n{prompt}"

    with st.chat_message("assistant"):
        with st.spinner("⚙️ Processando seu material com foco em métodos de revisão eficientes..."):
            response = ask_llm(full_prompt)
            st.markdown(f"**Alice Revisa:** {response}")

    # Feedback adaptativo
    feedback_prompt = f"""
    Usuário está revisando conteúdos para concursos.
    O progresso de estudo é de {progress}%. 
    As interações até agora são {st.session_state.interactions}.
    Forneça um feedback adaptativo com base no progresso e nas interações.
    """
    feedback_response = ask_llm(feedback_prompt)
    st.markdown(f"**Feedback da IA:** {feedback_response}")

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.interactions += 1
    progress = min(st.session_state.interactions * 10, 100)

    if progress == 100:
        st.success("🎉 Parabéns! Você completou a revisão! 🎉")
        st.session_state.interactions = 0
        progress = 0

    save_progress(progress)

