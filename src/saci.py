from pydantic import BaseModel


class Centro(BaseModel):
    id: str
    centro: str
    date: str
    description: str


class Disciplina(BaseModel):
    id: int
    codigo: str
    nome: str
    turma: str
    docente: str
    departamento: str
    horario: str
    alunos: int
    pcd: int
    preferencias: list


class Sala(BaseModel):
    id: int
    bloco: str
    nome: str
    capacidade: int
    tipo: str
    acessivel: bool


class Alocacao(BaseModel):
    centro: Centro
    sala: Sala
    disciplina: Disciplina


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

    for char in elemento:
        if char.isdigit():
            # Se o turno ainda não foi identificado, estamos lidando com os dias
            if not turno:
                dias.append(int(char))
            # Caso contrário, já estamos lidando com os horários
            else:
                horarios.append(int(char))
        elif char.isalpha():
            turno = char

    return {"dias": dias, "turno": turno, "horarios": horarios}


def ordenar_horarios(elementos: list[str]) -> list:
    """
    Ordena uma lista de strings no formato de dias, turno e horários.

    Args:
        elementos (list): Lista de strings para ordenar.

    Returns:
        list: Lista ordenada de strings.
    """
    ordem_dias = {
        1: "Domingo",
        2: "Segunda",
        3: "Terça",
        4: "Quarta",
        5: "Quinta",
        6: "Sexta",
        7: "Sábado",
    }
    ordem_turnos = {
        "M": 1,
        "T": 2,
        "N": 3,
        "E": 4,
    }  # Manhã (M), Tarde (T), Noite (N), Especial (E)

    def chave_ordenacao(elemento: str):
        desestruturado = desestruturar_horario(elemento)
        # Ordena pelos primeiros dias da semana, depois pelo turno e depois pelos horários
        return (
            min(
                desestruturado["dias"]
            ),  # Usamos o menor dia para representar a sequência
            ordem_turnos[desestruturado["turno"]],  # Usamos a ordem definida dos turnos
            min(
                desestruturado["horarios"]
            ),  # Usamos o menor horário para garantir a ordem
        )

    return sorted(elementos, key=chave_ordenacao)
