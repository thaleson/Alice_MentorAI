import requests
from app.utils.env_loader import load_env

config = load_env()

def ask_llm(user_input: str):
    api_key = config.get("api_key")
    model_url = config.get("model_url")

    if not api_key:
        return "Erro: API_WEB não foi configurada nos Secrets do Streamlit."

    if not model_url:
        return "Erro: URL_MODEL não foi configurada nos Secrets do Streamlit."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "Você é um especialista em métodos de estudo para concursos públicos. "
        "Dado um conteúdo, indique o melhor método de revisão entre flashcards, "
        "mapa mental, resumo ativo, questões ou outro. "
        "Justifique de forma breve e objetiva. "
        "Se o conteúdo estiver vago, peça mais detalhes."
    )

    payload = {
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.3,
        "max_tokens": 700,
        "top_p": 0.9
    }

    try:
        response = requests.post(
            model_url,
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]

        return f"Erro na requisição: {response.status_code} - {response.text}"

    except Exception as e:
        return f"Erro ao conectar com o modelo: {str(e)}"
