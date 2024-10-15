"""Aplicação para exibição de mapas SVG de um prédio usando Streamlit."""

import streamlit as st
from streamlit_calendar import calendar
from src.utils import descarregar_conteudo
from datetime import datetime, timezone, timedelta
from src.saci import desestruturar_horario

url = "https://sa.ci.ufpb.br/api/db/public/paas?centro=ci"

alocacoes = descarregar_conteudo(url)


def gerar_horarios(dados: dict) -> dict[int, list[str]]:
    """
    Gera um dicionário com datas e horários formatados com base nos dias, turnos e horários informados.

    Args:
        dados (dict): Dicionário contendo as chaves 'dias', 'turno' e 'horarios'.

    Returns:
        dict[int, list[str]]: Dicionário onde a chave é o número do dia e o valor é uma lista de strings com datas e horários formatados.
    """
    # Mapeamento dos turnos para suas letras e horários de início
    turnos_horarios = {
        "E": [0, 1, 2, 3, 4, 5],  # Madrugada
        "M": [6, 7, 8, 9, 10, 11],  # Manhã
        "T": [12, 13, 14, 15, 16, 17],  # Tarde
        "N": [18, 19, 20, 21, 22, 23],  # Noite
    }

    dias_semana = obter_datas_desta_semana()  # Obtém as datas desta semana
    resultado = {}

    for dia in dados["dias"]:
        # Verifica se o dia está nas datas da semana (entre 1 e 7)
        if str(dia) in dias_semana:
            data = dias_semana[str(dia)]
            horarios = []
            # Pega os horários baseados no turno e nos horários fornecidos
            for h in dados["horarios"]:
                hora_inicio = turnos_horarios[dados["turno"]][
                    h - 1
                ]  # Ajusta para base 0
                horarios.append(f"{data}{dados['turno']}{hora_inicio:02d}:00:00")

            resultado[dia] = horarios

    return resultado


def obter_datas_desta_semana() -> dict[str, str]:
    """
    Retorna um dicionário com as datas da semana atual, onde a chave é o índice do dia
    começando com "1" para domingo, e o valor é a data no formato 'yyyy-mm-dd'.
    """
    hoje = datetime.now()
    # Calcula a diferença em dias até o domingo (início da semana)
    inicio_semana = hoje - timedelta(
        days=hoje.weekday() + 1 if hoje.weekday() != 6 else 0
    )
    datas_semana = {}

    for i in range(7):  # Itera pelos 7 dias da semana
        dia_semana = inicio_semana + timedelta(days=i)
        datas_semana[str(i + 1)] = dia_semana.strftime("%Y-%m-%d")

    return datas_semana


def obter_data_hoje() -> str:
    """
    Retorna a data atual no formato 'yyyy-mm-dd' no fuso horário UTC-3.

    Returns:
        str: Data atual no formato 'yyyy-mm-dd'.
    """
    # Definir o fuso horário UTC-3
    fuso_horario_utc3 = timezone(timedelta(hours=-3))

    # Obter a data e hora atual no fuso horário UTC-3
    data_atual_utc3 = datetime.now(fuso_horario_utc3)

    # Retornar apenas a data no formato 'yyyy-mm-dd'
    return data_atual_utc3.strftime("%Y-%m-%d")


# Função para carregar o mapa SVG com base no andar selecionado
def load_map(level: str) -> str:
    """Carrega o arquivo SVG correspondente ao andar selecionado."""
    # Mapeando a escolha do usuário para o arquivo SVG correto
    arquivos_svg = {
        "Subsolo": "assets/processado/subsolo.svg",
        "Térreo": "assets/processado/terreo.svg",
        "Primeiro Andar": "assets/processado/primeiro_andar.svg",
        "Segundo Andar": "assets/processado/segundo_andar.svg",
        "Terceiro Andar": "assets/processado/terceiro_andar.svg",
    }

    caminho_arquivo = arquivos_svg.get(level, None)
    if caminho_arquivo is None:
        return f"O mapa SVG do {level} não foi encontrado."

    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo_svg:
            return arquivo_svg.read()
    except FileNotFoundError:
        return f"O mapa SVG do {level} não foi encontrado."


st.set_page_config(
    page_title="Mapas do Prédio",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="auto",
)


# Opções de andares disponíveis na combobox
andares = [
    "Subsolo",
    "Térreo",
    "Primeiro Andar",
    "Segundo Andar",
    "Terceiro Andar",
]

# Combobox para selecionar o andar
andar_selecionado = st.selectbox("Selecione o andar", andares)


# Exibindo o mapa correspondente ao andar selecionado
st.subheader(f"Mapa do {andar_selecionado}")
svg_conteudo = load_map(andar_selecionado)

# Exibindo o conteúdo SVG na tela
st.markdown(f"<div>{svg_conteudo}</div>", unsafe_allow_html=True)


################
# Filtro por andar

if andar_selecionado == "Subsolo":
    alocacoes = [
        alocacao
        for alocacao in alocacoes
        if alocacao.sala.nome.lower().startswith("sb")
    ]


elif andar_selecionado == "Térreo":
    alocacoes = [
        alocacao for alocacao in alocacoes if alocacao.sala.nome.lower().startswith("t")
    ]

elif andar_selecionado == "Primeiro Andar":
    alocacoes = [
        alocacao for alocacao in alocacoes if alocacao.sala.nome.lower().startswith("1")
    ]

elif andar_selecionado == "Segundo Andar":
    alocacoes = [
        alocacao for alocacao in alocacoes if alocacao.sala.nome.lower().startswith("2")
    ]

elif andar_selecionado == "Terceiro Andar":
    alocacoes = [
        alocacao for alocacao in alocacoes if alocacao.sala.nome.lower().startswith("3")
    ]

################


opcoes = sorted(
    list(set([f"{alocacao.sala.bloco} {alocacao.sala.nome}" for alocacao in alocacoes]))
)


if len(opcoes) > 0:
    mode = st.selectbox(
        "Calendar Mode:",
        ()  # TODO: outros componentes
        + tuple(opcoes),
    )

    alocacoes = [
        alocacao
        for alocacao in alocacoes
        if mode == f"{alocacao.sala.bloco} {alocacao.sala.nome}"
    ]

    week = obter_datas_desta_semana()

    events = []

    for alocacao in alocacoes:
        horarios_desestruturados = desestruturar_horario(alocacao.disciplina.horario)
        horarios = gerar_horarios(horarios_desestruturados)
        for dia, formatted_date_time in horarios.items():
            evento = {
                "title": alocacao.disciplina.nome,
                "start": formatted_date_time[0],
                "end": formatted_date_time[-1],
                "resourceId": alocacao.disciplina.codigo,
            }
            events.append(evento)

    sunday_yyyy_mm_dd = week["1"]  # domingo
    today_yyyy_mm_dd = obter_data_hoje()

    calendar_resources = [
        {"id": alocacao.disciplina.codigo, "title": alocacao.disciplina.nome}
        for alocacao in alocacoes
    ]

    calendar_options = {
        "editable": "false",
        "navLinks": "false",
        "resources": calendar_resources,
        "selectable": "false",
    }

    if "resource" in mode: # TODO: implementar outras visualizações
        pass
    else:
        # sala individual
        for identificador in list(
            set(
                [
                    f"{alocacao.sala.bloco} {alocacao.sala.nome}"
                    for alocacao in alocacoes
                ]
            )
        ):
            if mode == identificador:
                calendar_options = {
                    **calendar_options,
                    "headerToolbar": {
                        "left": "",
                        "center": "",
                        "right": "",
                    },
                    "initialDate": today_yyyy_mm_dd,
                    "initialView": "listWeek",
                }

    state = calendar(
        events=st.session_state.get("events", events),
        options=calendar_options,
        custom_css="""
        .fc-event-past {
            opacity: 0.8;
        }
        .fc-event-time {
            font-style: italic;
        }
        .fc-event-title {
            font-weight: 700;
        }
        .fc-toolbar-title {
            font-size: 2rem;
        }
        """,
        key=mode,
    )
