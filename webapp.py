"""Aplicação para exibição de mapas SVG de um prédio usando Streamlit."""

import streamlit as st

# Título da aplicação
st.title("Mapas do Prédio")

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
st.markdown(f"<div>{svg_conteudo}</div>", unsafe_allow_html=True)
