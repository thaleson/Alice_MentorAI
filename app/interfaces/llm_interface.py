import requests
from app.utils.env_loader import load_env

config = load_env()

def ask_llm(user_input: str):
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }

    # Instruções claras para evitar alucinações
    system_prompt = (
        "Você é um especialista em métodos de estudo para concursos públicos. "
        "Dado um conteúdo (resumo ou tema), sua função é indicar o MELHOR método de revisão entre: "
        "flashcards, mapa mental, resumo ativo, questões ou outro. "
        "Justifique a escolha de forma breve, objetiva e confiável. "
        "NUNCA invente informações. Se o conteúdo estiver vago, peça mais detalhes."
    )

    payload = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.3,
        "max_tokens": 700,
        "top_p": 0.9
    }

    response = requests.post(config["model_url"], headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Erro na requisição: {response.status_code} - {response.text}"
