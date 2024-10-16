"""
Aplicação para exibição de mapas SVG de um prédio usando Streamlit.

Este aplicativo permite que os usuários visualizem mapas interativos de diferentes andares de um prédio.
Os usuários podem selecionar um andar, visualizar o mapa correspondente e clicar em salas para obter
informações detalhadas sobre as disciplinas alocadas nessas salas.

Os dados são obtidos da API da UFPB e processados para exibição no aplicativo.
"""

import streamlit as st
from st_click_detector import click_detector
from src.utils import (
    descarregar_conteudo,
    desestruturar_horario,
    criar_tabela_markdown,
)
from datetime import datetime
from src.saci import Alocacao
from src.svg.mapa import load_map

# URL da API para obter as alocações de disciplinas
url = "https://sa.ci.ufpb.br/api/db/public/paas?centro=ci"

# Baixa e processa os dados das alocações a partir da URL fornecida
alocacoes: list[Alocacao] = descarregar_conteudo(url)

# Configuração inicial da página Streamlit
st.set_page_config(
    page_title="Mapas do Prédio",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="auto",
)

# Lista de andares disponíveis para seleção pelo usuário
andares: list[str] = [
    "Subsolo",
    "Térreo",
    "Primeiro Andar",
    "Segundo Andar",
    "Terceiro Andar",
]

# Caixa de seleção para o usuário escolher o andar que deseja visualizar
andar_selecionado: str = st.selectbox("Selecione o andar", andares)

# Exibe o título do mapa correspondente ao andar selecionado
st.subheader(f"Mapa do {andar_selecionado}")

# Carrega o conteúdo SVG do mapa do andar selecionado
svg_conteudo: str = load_map(andar_selecionado)

# Detecta cliques no mapa SVG
clicked: str = click_detector(svg_conteudo)

################
# Filtra as alocações de disciplinas por andar

# Dicionário que mapeia os andares aos seus prefixos correspondentes nas salas
prefixos_andar: dict[str, str] = {
    "Subsolo": "sb",
    "Térreo": "t",
    "Primeiro Andar": "1",
    "Segundo Andar": "2",
    "Terceiro Andar": "3",
}

# Obtém o prefixo correspondente ao andar selecionado
prefixo: str = prefixos_andar.get(andar_selecionado, "")

# Filtra as alocações para incluir apenas aquelas do andar selecionado
if prefixo:
    alocacoes = [
        alocacao
        for alocacao in alocacoes
        if alocacao.sala.nome.lower().startswith(prefixo)
    ]

################


@st.dialog("Bloco CI", width="large")
def visualizar_disciplina(alocacoes: list[Alocacao]) -> None:
    """
    Exibe informações detalhadas sobre as alocações de disciplinas em uma sala específica.

    Args:
        alocacoes (list[Alocacao]): Lista de alocações para a sala selecionada.
    """
    # Obtém a primeira alocação para extrair informações da sala
    alocacao = alocacoes[0]

    # Extrai informações da sala
    nome: str = f"{alocacao.sala.bloco} {alocacao.sala.nome}"
    acessivel: str = "✅ Sim" if alocacao.sala.acessivel else "❌ Não"
    capacidade: str = f"{alocacao.sala.capacidade} pessoas"
    tipo: str = alocacao.sala.tipo

    # Exibe as informações da sala em formato de tabela Markdown
    st.markdown("## Informações:")
    st.markdown(
        criar_tabela_markdown(
            ["Nome", "Acessível", "Capacidade", "Tipo", "Disciplinas"],
            [[nome, acessivel, capacidade, tipo, str(len(alocacoes))]],
        )
    )

    # Exibe o título para a seção de disciplinas
    st.markdown("## Disciplinas:")

    # Opções de visualização disponíveis para o usuário
    mode: str = st.selectbox(
        "Visualização",
        ("Geral", "Hoje", "Por dia"),
    )

    # Obtém o dia atual da semana no formato desejado (1 para Domingo, ..., 7 para Sábado)
    weekday_python: int = datetime.today().weekday()  # 0 é segunda, 6 é domingo
    weekday_mapping: dict[int, int] = {
        6: 1,  # Domingo
        0: 2,  # Segunda-feira
        1: 3,  # Terça-feira
        2: 4,  # Quarta-feira
        3: 5,  # Quinta-feira
        4: 6,  # Sexta-feira
        5: 7,  # Sábado
    }
    hoje: int = weekday_mapping[weekday_python]

    # Dicionário que mapeia os números dos dias para os nomes dos dias da semana
    semana: dict[int, str] = {
        1: "Domingo",
        2: "Segunda-feira",
        3: "Terça-feira",
        4: "Quarta-feira",
        5: "Quinta-feira",
        6: "Sexta-feira",
        7: "Sábado",
    }

    linhas: list[list[str]] = []  # Lista de linhas para a tabela de disciplinas
    dias: list[int] = []  # Lista de dias em que a disciplina ocorre
    horarios_desestruturados: dict = {}  # Dicionário com informações desestruturadas do horário
    if mode == "Por dia":
        # Exibe as disciplinas separadas por dia da semana
        for dia_numero, dia_nome in semana.items():
            for alocacao in alocacoes:
                # Desestrutura o horário para obter os dias em que a disciplina ocorre
                horarios_desestruturados = desestruturar_horario(
                    alocacao.disciplina.horario
                )
                dias = horarios_desestruturados["dias"]

                # Verifica se a disciplina ocorre no dia atual da iteração
                if dia_numero in dias:
                    linhas.append(
                        [
                            alocacao.disciplina.codigo,
                            alocacao.disciplina.horario,
                            alocacao.disciplina.turma,
                            alocacao.disciplina.nome,
                            alocacao.disciplina.docente,
                            str(alocacao.disciplina.alunos),
                        ]
                    )
            if linhas:
                # Exibe as disciplinas para o dia atual se houverem
                st.markdown(f"### {dia_nome}")
                st.markdown(
                    criar_tabela_markdown(
                        [
                            "Código",
                            "Horário",
                            "Turma",
                            "Disciplina",
                            "Docente",
                            "Alunos",
                        ],
                        linhas,
                    )
                )
    else:
        # Exibe todas as disciplinas ou apenas as de hoje, dependendo da opção selecionada
        for alocacao in alocacoes:
            if mode == "Geral":
                # Adiciona todas as disciplinas à lista
                linhas.append(
                    [
                        alocacao.disciplina.codigo,
                        alocacao.disciplina.horario,
                        alocacao.disciplina.turma,
                        alocacao.disciplina.nome,
                        alocacao.disciplina.docente,
                        str(alocacao.disciplina.alunos),
                    ]
                )
            elif mode == "Hoje":
                # Desestrutura o horário para obter os dias em que a disciplina ocorre
                horarios_desestruturados = desestruturar_horario(
                    alocacao.disciplina.horario
                )
                dias = horarios_desestruturados["dias"]

                # Verifica se a disciplina ocorre no dia atual
                if hoje in dias:
                    linhas.append(
                        [
                            alocacao.disciplina.codigo,
                            alocacao.disciplina.horario,
                            alocacao.disciplina.turma,
                            alocacao.disciplina.nome,
                            alocacao.disciplina.docente,
                            str(alocacao.disciplina.alunos),
                        ]
                    )

        # Exibe as disciplinas filtradas
        st.markdown(
            criar_tabela_markdown(
                ["Código", "Horário", "Turma", "Disciplina", "Docente", "Alunos"],
                linhas,
            )
        )

    # Exibe instruções sobre como interpretar o horário das disciplinas
    st.markdown("""
    ---
    ## Como interpretar o horário das disciplinas:

    ### 1. Identificação dos dias da semana:
    - **2** = Segunda-feira
    - **3** = Terça-feira
    - **4** = Quarta-feira
    - **5** = Quinta-feira
    - **6** = Sexta-feira
    - **7** = Sábado

    ### 2. Identificação do turno:
    - **M** = Manhã
    - **T** = Tarde
    - **N** = Noite

    ### 3. Exemplo de horários:
    - **Exemplo 1: 2M2345**
        - Segunda-feira (**2**) no turno da manhã (**M**), nas aulas 2, 3, 4 e 5.

    | Aulas | Manhã          | Tarde         | Noite         |
    |-------|----------------|---------------|---------------|
    | 1     | 07:00 - 08:00  | 13:00 - 14:00 | 19:00 - 20:00 |
    | 2     | 08:00 - 09:00  | 14:00 - 15:00 | 20:00 - 21:00 |
    | 3     | 09:00 - 10:00  | 15:00 - 16:00 | 21:00 - 22:00 |
    | 4     | 10:00 - 11:00  | 16:00 - 17:00 | 22:00 - 23:00 |
    | 5     | 11:00 - 12:00  | 17:00 - 18:00 | -             |
    | 6     | 12:00 - 13:00  | 18:00 - 19:00 | -             |

    """)


# Verifica se o usuário clicou em algum elemento do mapa
if clicked and clicked != "":
    print(f"{datetime.now()} clicou em {clicked}")
    alocacoes_da_sala: list[Alocacao] = []
    # Procura por alocações cuja sala corresponda ao elemento clicado
    for alocacao in alocacoes:
        if alocacao.sala.nome.lower() in clicked.lower():
            alocacoes_da_sala.append(alocacao)
    # Se houver alocações para a sala clicada, exibe o diálogo com as informações
    if alocacoes_da_sala:
        visualizar_disciplina(alocacoes_da_sala)
