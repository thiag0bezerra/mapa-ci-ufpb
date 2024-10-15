from src.utils import baixar_json
from src.saci import Sala, Centro, Alocacao, Disciplina
from src.saci import (
    desestruturar_horario,
)
from src.operacoes import filtrar, ordenar
from rich.console import Console
from rich.table import Table
import re
from rich.tree import Tree
from rich import print
import pandas as pd


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


console = Console()


def exibir_hierarquia(alocacoes: list[Alocacao]) -> None:
    """
    Exibe a hierarquia de alocações em formato de árvore no padrão:
    Centro > Sala > Horário (ordenado) > Disciplinas.

    Args:
        alocacoes (list[Alocacao]): Lista de objetos Alocacao.
    """

    # Organiza as alocações por centro
    centros_agrupados = {}
    for alocacao in alocacoes:
        if alocacao.centro.centro not in centros_agrupados:
            centros_agrupados[alocacao.centro.centro] = {}
        identificador_sala = f"{alocacao.sala.bloco} {alocacao.sala.nome}"
        if identificador_sala not in centros_agrupados[alocacao.centro.centro]:
            centros_agrupados[alocacao.centro.centro][identificador_sala] = []
        centros_agrupados[alocacao.centro.centro][identificador_sala].append(
            alocacao.disciplina
        )

    # Cria a árvore
    tree = Tree(":office: Alocações por Centro, Sala, Horário e Disciplina")

    # Preenche a árvore com as alocações
    for centro_nome, salas in centros_agrupados.items():
        centro_branch = tree.add(f":cityscape: [bold magenta]{centro_nome}[/]")

        for identificador_sala, disciplinas in salas.items():
            sala_branch = centro_branch.add(
                f":door: [bold green]{identificador_sala}[/]"
            )

            for dia in list(range(1, 7 + 1)):
                dia_branch = None
                for turno in ["M", "T", "N", "E"]:
                    turno_branch = None
                    for horario in range(1, 6 + 1):
                        # Adiciona as disciplinas associadas ao horário
                        for disciplina in disciplinas:
                            hr = desestruturar_horario(disciplina.horario)
                            if (
                                dia in hr["dias"]
                                and turno == hr["turno"]
                                and horario in hr["horarios"]
                            ):
                                if dia_branch is None:
                                    # converter digito para dia da semana em portugues
                                    dias_semana = {
                                        1: "Domingo",
                                        2: "Segunda-feira",
                                        3: "Terça-feira",
                                        4: "Quarta-feira",
                                        5: "Quinta-feira",
                                        6: "Sexta-feira",
                                        7: "Sábado",
                                    }

                                    dia_branch = sala_branch.add(
                                        f":calendar: [cyan]{dias_semana[dia]}[/]"
                                    )
                                if turno_branch is None:
                                    # converter para strings Manhã, Tarde, Noite e Especial
                                    turnos = {
                                        "M": "Manhã",
                                        "T": "Tarde",
                                        "N": "Noite",
                                        "E": "Especial",
                                    }
                                    turno_branch = dia_branch.add(
                                        f":sunrise: [yellow]{turnos[turno]}[/]"
                                    )
                                # converter horario para a hora dos turno M, T, N e E
                                turnos = {
                                    "M": "6",
                                    "T": "12",
                                    "N": "18",
                                    "E": "0",
                                }
                                turno_branch.add(
                                    f":books: [yellow]{(int(turnos[turno]) + horario):02}:00 {disciplina.nome}[/] - Turma: {disciplina.turma} - Docente: {disciplina.docente}"
                                )

    # Exibe a árvore
    print(tree)


def tabela(alocacoes: list[Alocacao]) -> None:
    centro = alocacoes[0].centro

    table = Table(
        "Código",
        "Horário",
        "Turma",
        "Sala",
        "Disciplina",
        "Docente",
        "Alunos",
        title=f"Disciplinas do CI - {centro.date}",
        show_lines=True,
    )
    for alocacao in alocacoes:
        disciplina = alocacao.disciplina
        sala = alocacao.sala
        identificador_sala = f"{sala.bloco} {sala.nome}"

        row = [
            disciplina.codigo,
            disciplina.horario,
            f"{disciplina.turma:02}"
            if disciplina.turma.isdigit()
            else disciplina.turma,
            identificador_sala,
            disciplina.nome,
            disciplina.docente,
            f"{disciplina.alunos:02}",
        ]

        padrao = r"\d+/\d+"
        if "undefined" in row:
            # A string 'undefined' está presente em row
            table.add_row(*[str(item) for item in row], style="red")
        elif bool(re.search(padrao, identificador_sala)):
            # Existe uma possível data no identificador da sala
            table.add_row(*[str(item) for item in row], style="yellow")
        else:
            table.add_row(*[str(item) for item in row])
    console.print(table)


def alocacao_para_dataframe(alocacoes: list[Alocacao]) -> pd.DataFrame:
    """Converte uma lista de objetos Alocacao para um DataFrame do pandas.

    Args:
        alocacoes: Lista de objetos do tipo Alocacao.

    Returns:
        DataFrame contendo as informações extraídas das alocações.
    """
    # Cria uma lista de dicionários, onde cada dicionário representa uma alocação
    dados = []

    for alocacao in alocacoes:
        dados.append(
            {
                "centro_id": alocacao.centro.id,
                "centro_nome": alocacao.centro.centro,
                "centro_date": alocacao.centro.date,
                "centro_description": alocacao.centro.description,
                "sala_id": alocacao.sala.id,
                "sala_bloco": alocacao.sala.bloco,
                "sala_nome": alocacao.sala.nome,
                "sala_capacidade": alocacao.sala.capacidade,
                "sala_tipo": alocacao.sala.tipo,
                "sala_acessivel": alocacao.sala.acessivel,
                "disciplina_id": alocacao.disciplina.id,
                "disciplina_codigo": alocacao.disciplina.codigo,
                "disciplina_nome": alocacao.disciplina.nome,
                "disciplina_turma": alocacao.disciplina.turma,
                "disciplina_docente": alocacao.disciplina.docente,
                "disciplina_departamento": alocacao.disciplina.departamento,
                "disciplina_horario": alocacao.disciplina.horario,
                "disciplina_alunos": alocacao.disciplina.alunos,
                "disciplina_pcd": alocacao.disciplina.pcd,
                "disciplina_preferencias": alocacao.disciplina.preferencias,
            }
        )

    # Cria o DataFrame a partir da lista de dicionários
    df = pd.DataFrame(dados)

    return df


if __name__ == "__main__":
    url = "https://sa.ci.ufpb.br/api/db/public/paas?centro=ci"

    alocacoes = descarregar_conteudo(url)
    # Filtrando disciplinas do departamento "CI-DCC" com mais de 30 alunos
    resultado = filtrar(alocacoes)
    resultado_ordernado = ordenar(
        resultado, ordenar_por="disciplina.nome", crescente=True
    )
    tabela(resultado_ordernado)
    exibir_hierarquia(resultado_ordernado)

    df = alocacao_para_dataframe(alocacoes)
    print(df)
    df.to_csv("alocacoes.csv", index=False)
