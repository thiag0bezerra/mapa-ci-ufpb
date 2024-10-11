import httpx


def baixar_json(url: str) -> dict:
    """Baixa e retorna o conteúdo JSON de um URL."""
    try:
        # Faz a requisição ao URL
        resposta = httpx.get(url)
        # Checa se a requisição foi bem-sucedida (código 200)
        resposta.raise_for_status()
        # Retorna o conteúdo JSON como um dicionário
        return resposta.json()
    except httpx.HTTPStatusError as e:
        print(f"Erro ao baixar o conteúdo: {e}")
        return {}
