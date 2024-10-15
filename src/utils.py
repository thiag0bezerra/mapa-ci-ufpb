import httpx
from src.saci import Alocacao, Centro, Disciplina, Sala


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


def descarregar_conteudo(url: str) -> list[Alocacao]:
    """
    Baixa os dados do URL e retorna uma lista de objetos Alocacao.

    Args:
        url (str): URL de onde baixar os dados JSON.

    Returns:
        list[Disciplina]: Lista de objetos do tipo Alocacao.
    """
    dados_json = baixar_json(url)

    alocacoes: list[Alocacao] = []

    centro = Centro(
        id=dados_json["id"].strip(),
        centro=dados_json["centro"].strip(),
        date=dados_json["date"].strip(),
        description=dados_json["description"].strip(),
    )

    conteudo = dados_json["solution"]

    for solution in conteudo["solution"]:
        sala = Sala(
            id=solution["id"],
            bloco=solution["bloco"].strip(),
            nome=solution["nome"].strip(),
            capacidade=solution["capacidade"],
            tipo=solution["tipo"].strip(),
            acessivel=solution["acessivel"],
        )

        for item in solution["classes"]:
            # Verifica se 'preferencias' é None (null) e o substitui por uma lista vazia
            preferencias = (
                item["preferencias"] if item["preferencias"] is not None else []
            )

            # Cria uma instância de Disciplina para cada item do JSON
            disciplina = Disciplina(
                id=item["id"],
                codigo=item["codigo"].strip(),
                nome=item["nome"].strip(),
                turma=item["turma"].strip(),
                docente=item["docente"].strip(),
                departamento=item["departamento"].strip(),
                horario=item["horario"].strip(),
                alunos=item["alunos"],
                pcd=item["pcd"],
                preferencias=preferencias,
            )

            alocacoes.append(Alocacao(centro=centro, sala=sala, disciplina=disciplina))

    return alocacoes
