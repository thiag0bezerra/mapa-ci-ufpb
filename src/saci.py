"""
Este módulo contém as representações de dados para o sistema da UFPB, especificamente para
o JSON presente em https://sa.ci.ufpb.br/api/db/public/paas?centro=ci. Ele faz uso de
pydantic para validação e manipulação dos dados, facilitando a detecção de erros durante
o processamento do JSON. Os dados são populados pela função `descarregar_conteudo` no
arquivo `src/utils.py`.
"""

from pydantic import BaseModel
from typing import Any, List


class Centro(BaseModel):
    """
    Representa o centro acadêmico.

    Atributos:
        id (str): Identificador único do centro.
        centro (str): Nome do centro.
        date (str): Data de criação ou atualização do centro.
        description (str): Descrição do centro.
    """

    id: str
    centro: str
    date: str
    description: str


class Disciplina(BaseModel):
    """
    Representa uma disciplina ofertada.

    Atributos:
        id (int): Identificador único da disciplina.
        codigo (str): Código da disciplina.
        nome (str): Nome da disciplina.
        turma (str): Identificação da turma.
        docente (str): Nome do professor responsável.
        departamento (str): Departamento ao qual a disciplina pertence.
        horario (str): Horário em que a disciplina é ofertada.
        alunos (int): Número de alunos matriculados.
        pcd (int): Número de alunos com necessidades especiais (PcD).
        preferencias (List[Any]): Preferências relacionadas à disciplina (podem incluir equipamentos,
                                  condições especiais de sala, entre outros).
    """

    id: int
    codigo: str
    nome: str
    turma: str
    docente: str
    departamento: str
    horario: str
    alunos: int
    pcd: int
    preferencias: List[Any]  # Tipo mais específico para listas, facilitando a leitura


class Sala(BaseModel):
    """
    Representa uma sala de aula.

    Atributos:
        id (int): Identificador único da sala.
        bloco (str): Bloco ao qual a sala pertence.
        nome (str): Nome ou número da sala.
        capacidade (int): Capacidade total de alunos.
        tipo (str): Tipo de sala (laboratório, sala comum, etc.).
        acessivel (bool): Indica se a sala é acessível para pessoas com deficiência.
    """

    id: int
    bloco: str
    nome: str
    capacidade: int
    tipo: str
    acessivel: bool


class Alocacao(BaseModel):
    """
    Representa a alocação de uma disciplina em uma sala em um determinado centro.

    Atributos:
        centro (Centro): Instância da classe `Centro`, representando o centro acadêmico.
        sala (Sala): Instância da classe `Sala`, representando a sala onde a disciplina é ofertada.
        disciplina (Disciplina): Instância da classe `Disciplina`, representando a disciplina ofertada.
    """

    centro: Centro
    sala: Sala
    disciplina: Disciplina
