"""Aplicação para exibição de mapas SVG de um prédio usando Streamlit."""

import streamlit as st

from streamlit_calendar import calendar

import pandas as pd

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


# Função para carregar o mapa SVG com base no andar selecionado
def carregar_mapa_svg(andar: str) -> str:
    """Carrega o arquivo SVG correspondente ao andar selecionado."""
    # Mapeando a escolha do usuário para o arquivo SVG correto
    print(f"Carregando mapa do {andar}...")
    arquivos_svg = {
        "Subsolo": "assets/processado/subsolo.svg",
        "Térreo": "assets/processado/terreo.svg",
        "Primeiro Andar": "assets/processado/primeiro_andar.svg",
        "Segundo Andar": "assets/processado/segundo_andar.svg",
        "Terceiro Andar": "assets/processado/terceiro_andar.svg",
    }

    caminho_arquivo = arquivos_svg.get(andar, None)
    if caminho_arquivo is None:
        return f"O mapa SVG do {andar} não foi encontrado."

    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo_svg:
            return arquivo_svg.read()
    except FileNotFoundError:
        return f"O mapa SVG do {andar} não foi encontrado."


# Exibindo o mapa correspondente ao andar selecionado
st.subheader(f"Mapa do {andar_selecionado}")

svg_conteudo = carregar_mapa_svg(andar_selecionado)
# Exibindo o conteúdo SVG na tela
st.markdown(
    f"""<div style="display: inline-block; width: 100%;">{svg_conteudo}</div>""",
    unsafe_allow_html=True,
)


################


mode = st.selectbox(
    "Calendar Mode:",
    (
        "daygrid",
        "resource-daygrid",
        "resource-timegrid",
        "list",
    ),
)

events = [
    {
        "title": "Event 7",
        "color": "#FF4B4B",
        "start": "2023-07-01T08:30:00",
        "end": "2023-07-01T10:30:00",
        "resourceId": "a",
    },
    {
        "title": "Event 8",
        "color": "#3D9DF3",
        "start": "2023-07-01T07:30:00",
        "end": "2023-07-01T10:30:00",
        "resourceId": "b",
    },
    {
        "title": "Event 9",
        "color": "#3DD56D",
        "start": "2023-07-02T10:40:00",
        "end": "2023-07-02T12:30:00",
        "resourceId": "c",
    },
    {
        "title": "Event 10",
        "color": "#FF4B4B",
        "start": "2023-07-15T08:30:00",
        "end": "2023-07-15T10:30:00",
        "resourceId": "d",
    },
    {
        "title": "Event 11",
        "color": "#3DD56D",
        "start": "2023-07-15T07:30:00",
        "end": "2023-07-15T10:30:00",
        "resourceId": "e",
    },
    {
        "title": "Event 12",
        "color": "#3D9DF3",
        "start": "2023-07-21T10:40:00",
        "end": "2023-07-21T12:30:00",
        "resourceId": "f",
    },
    {
        "title": "Event 13",
        "color": "#FF4B4B",
        "start": "2023-07-17T08:30:00",
        "end": "2023-07-17T10:30:00",
        "resourceId": "a",
    },
    {
        "title": "Event 14",
        "color": "#3D9DF3",
        "start": "2023-07-17T09:30:00",
        "end": "2023-07-17T11:30:00",
        "resourceId": "b",
    },
    {
        "title": "Event 15",
        "color": "#3DD56D",
        "start": "2023-07-17T10:30:00",
        "end": "2023-07-17T12:30:00",
        "resourceId": "c",
    },
    {
        "title": "Event 16",
        "color": "#FF6C6C",
        "start": "2023-07-17T13:30:00",
        "end": "2023-07-17T14:30:00",
        "resourceId": "d",
    },
    {
        "title": "Event 17",
        "color": "#FFBD45",
        "start": "2023-07-17T15:30:00",
        "end": "2023-07-17T16:30:00",
        "resourceId": "e",
    },
]
calendar_resources = [
    {"id": "a", "building": "Building A", "title": "Room A"},
    {"id": "b", "building": "Building A", "title": "Room B"},
    {"id": "c", "building": "Building B", "title": "Room C"},
    {"id": "d", "building": "Building B", "title": "Room D"},
    {"id": "e", "building": "Building C", "title": "Room E"},
    {"id": "f", "building": "Building C", "title": "Room F"},
]

calendar_options = {
    "editable": "true",
    "navLinks": "true",
    "resources": calendar_resources,
    "selectable": "true",
}

if "resource" in mode:
    if mode == "resource-daygrid":
        calendar_options = {
            **calendar_options,
            "initialDate": "2023-07-01",
            "initialView": "resourceDayGridDay",
            "resourceGroupField": "building",
        }
    elif mode == "resource-timegrid":
        calendar_options = {
            **calendar_options,
            "initialDate": "2023-07-01",
            "initialView": "resourceTimeGridDay",
            "resourceGroupField": "building",
        }
else:
    if mode == "daygrid":
        calendar_options = {
            **calendar_options,
            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "dayGridDay,dayGridWeek,dayGridMonth",
            },
            "initialDate": "2023-07-01",
            "initialView": "dayGridMonth",
        }
    elif mode == "list":
        calendar_options = {
            **calendar_options,
            "initialDate": "2023-07-01",
            "initialView": "listMonth",
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
