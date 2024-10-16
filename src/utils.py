"""
Este módulo contém funções utilitárias para baixar e processar dados JSON do sistema UFPB,
especificamente para o JSON disponível em https://sa.ci.ufpb.br/api/db/public/paas?centro=ci.
As funções incluem download de conteúdo, manipulação de horários e geração de tabelas Markdown.
"""

import httpx
from src.saci import Alocacao, Centro, Disciplina, Sala


def baixar_json(url: str) -> dict:
    """
    Baixa e retorna o conteúdo JSON de um URL.

    Args:
        url (str): URL para onde será feita a requisição.

    Returns:
        dict: O conteúdo JSON obtido do URL como um dicionário. Retorna um dicionário vazio em caso de erro.
    """
    try:
        # Faz a requisição ao URL e retorna o conteúdo como JSON
        resposta = httpx.get(url)
        resposta.raise_for_status()  # Verifica se a requisição foi bem-sucedida
        return resposta.json()
    except httpx.HTTPStatusError as e:
        print(f"Erro ao baixar o conteúdo: {e}")
        return {}  # Retorna dicionário vazio em caso de erro


def descarregar_conteudo(url: str) -> list[Alocacao]:
    """
    Baixa os dados do URL e retorna uma lista de objetos do tipo Alocacao.

    Args:
        url (str): URL de onde os dados JSON serão baixados.

    Returns:
        list[Alocacao]: Lista de objetos do tipo Alocacao, representando as alocações de disciplinas.
    """
    # Baixa o conteúdo JSON
    dados_json = baixar_json(url)

    alocacoes: list[Alocacao] = []

    # Criação da instância de Centro
    centro = Centro(
        id=dados_json["id"].strip(),
        centro=dados_json["centro"].strip(),
        date=dados_json["date"].strip(),
        description=dados_json["description"].strip(),
    )

    conteudo = dados_json["solution"]

    # Itera sobre cada "solution" no JSON, que contém as salas e disciplinas
    for solution in conteudo["solution"]:
        # Criação da instância de Sala
        sala = Sala(
            id=solution["id"],
            bloco=solution["bloco"].strip(),
            nome=solution["nome"].strip(),
            capacidade=solution["capacidade"],
            tipo=solution["tipo"].strip(),
            acessivel=solution["acessivel"],
        )

        # Itera sobre cada item de classe (disciplina) na solução
        for item in solution["classes"]:
            # Tratamento de caso onde "preferencias" pode ser None (null no JSON)
            preferencias = (
                item["preferencias"] if item["preferencias"] is not None else []
            )

            # Criação da instância de Disciplina
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

            # Adiciona uma nova alocação à lista de alocações
            alocacoes.append(Alocacao(centro=centro, sala=sala, disciplina=disciplina))

    return alocacoes


def desestruturar_horario(elemento: str) -> dict:
    """
    Desestrutura uma string no formato de dias, turno e horários.

    Args:
        elemento (str): String no formato '35T45' ou similar.

    Returns:
        dict: Um dicionário com chaves 'dias', 'turno' e 'horarios'.
    """
    dias = []
    turno = ""
    horarios = []

    # Itera sobre cada caractere da string
    for char in elemento:
        if char.isdigit():
            if not turno:
                dias.append(int(char))  # Adiciona aos dias enquanto não tiver turno
            else:
                horarios.append(
                    int(char)
                )  # Adiciona aos horários quando turno já identificado
        elif char.isalpha():
            turno = char  # Identifica o turno (manhã, tarde, noite, etc.)

    return {"dias": dias, "turno": turno, "horarios": horarios}


def criar_tabela_markdown(colunas: list[str], linhas: list[list[str]]) -> str:
    """
    Cria uma tabela em formato Markdown.

    Args:
        colunas (list[str]): Lista com os nomes das colunas.
        linhas (list[list[str]]): Lista de listas com os valores de cada linha.

    Returns:
        str: Tabela formatada em Markdown.
    """
    # Cabeçalho da tabela
    header = "| " + " | ".join(colunas) + " |"
    # Linha divisória baseada no tamanho das colunas
    separador = "| " + " | ".join(["-" * len(coluna) for coluna in colunas]) + " |"

    # Formata as linhas da tabela
    linhas_formatadas = ["| " + " | ".join(map(str, linha)) + " |" for linha in linhas]

    # Junta o cabeçalho, separador e linhas em uma única string
    return "\n".join([header, separador] + linhas_formatadas)
