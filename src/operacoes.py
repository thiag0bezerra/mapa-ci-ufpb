from typing import Optional
from .saci import Alocacao


def filtrar(
    alocacoes: list[Alocacao],
    docente: Optional[str] = None,
    departamento: Optional[str] = None,
    horario: Optional[str] = None,
    min_alunos: Optional[int] = None,
    max_alunos: Optional[int] = None,
    ordenar_por: Optional[str] = None,
) -> list[Alocacao]:
    """
    Filtra e ordena uma lista de alocações com base nsos critérios fornecidos.

    Args:
        alocações (list[Alocacao]): Lista de disciplinas a serem filtradas.
        docente (Optional[str]): Nome do docente a filtrar.
        departamento (Optional[str]): Departamento a filtrar.
        horario (Optional[str]): Horário a filtrar.
        min_alunos (Optional[int]): Número mínimo de alunos.
        max_alunos (Optional[int]): Número máximo de alunos.
        ordenar_por (Optional[str]): Campo pelo qual as disciplinas devem ser ordenadas. Ex.: 'alunos'.

    Returns:
        list[Alocacao]: Lista de alocações filtradas e ordenadas.
    """

    # Filtrando as disciplinas de acordo com os parâmetros fornecidos
    alocacoes_filtradas = alocacoes

    if docente:
        alocacoes_filtradas = [
            aloc for aloc in alocacoes_filtradas if aloc.disciplina.docente == docente
        ]
    if departamento:
        alocacoes_filtradas = [
            aloc
            for aloc in alocacoes_filtradas
            if aloc.disciplina.departamento == departamento
        ]
    if horario:
        alocacoes_filtradas = [
            aloc for aloc in alocacoes_filtradas if aloc.disciplina.horario == horario
        ]
    if min_alunos:
        alocacoes_filtradas = [
            aloc for aloc in alocacoes_filtradas if aloc.disciplina.alunos >= min_alunos
        ]
    if max_alunos:
        alocacoes_filtradas = [
            aloc for aloc in alocacoes_filtradas if aloc.disciplina.alunos <= max_alunos
        ]

    # Ordenando as disciplinas se o campo 'ordenar_por' for fornecido
    if ordenar_por:
        alocacoes_filtradas = sorted(
            alocacoes_filtradas, key=lambda disc: getattr(disc, ordenar_por)
        )

    return alocacoes_filtradas


def ordenar(
    alocacoes: list[Alocacao], ordenar_por: str, crescente: bool
) -> list[Alocacao]:
    # Dividimos a string ordenar_por caso precise acessar atributos internos (ex: "sala.capacidade")
    def chave(alocacao: Alocacao):
        atributos = ordenar_por.split(".")
        valor = alocacao
        for atributo in atributos:
            valor = getattr(valor, atributo)
        return valor

    return sorted(
        alocacoes,
        key=chave,
        reverse=(not crescente),
    )
