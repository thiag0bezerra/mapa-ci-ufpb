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
