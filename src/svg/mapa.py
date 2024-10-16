"""
Este módulo é responsável por gerar mapas SVG interativos para diferentes andares,
utilizando dados de arquivos JSON correspondentes. Ele inclui funções para carregar
ícones, calcular transformações, renderizar textos e construir o conteúdo SVG final.
"""

from dataclasses import dataclass
from typing import Tuple
import json
import os
import xml.etree.ElementTree as ET


@dataclass
class RetanguloSchema:
    """
    Representa o esquema de um retângulo no mapa SVG, contendo informações
    de estilo e identificação para interação.
    """

    title: str
    description: str
    id: str
    color: str
    colorOnHover: str
    d: str


@dataclass
class PathSchema:
    """
    Representa o esquema de um caminho (path) SVG, incluindo atributos de estilo,
    identificação e informações adicionais para renderização.
    """

    fill: str
    d: str
    id: str
    type: str
    title: str
    description: str
    fillOpacity: str
    fillRule: str
    stroke: str
    strokeWidth: str
    strokeLinecap: str
    strokeLinejoin: str


def create_text(
    text: str,
    x: float,
    y: float,
    font_family: str = "Arial",
    font_size: str = "14",
    fill: str = "black",
    text_anchor: str = "middle",
    alignment_baseline: str = "central",
    font_weight: str = "bold",
) -> str:
    """
    Cria um elemento de texto SVG com os parâmetros especificados.

    Args:
        text (str): O conteúdo do texto a ser exibido.
        x (float): A posição x do texto.
        y (float): A posição y do texto.
        font_family (str, opcional): A família de fontes a ser usada. Padrão é 'Arial'.
        font_size (str, opcional): O tamanho da fonte. Padrão é '14'.
        fill (str, opcional): A cor do texto. Padrão é 'black'.
        text_anchor (str, opcional): A ancoragem do texto. Padrão é 'middle'.
        alignment_baseline (str, opcional): A linha de base de alinhamento do texto. Padrão é 'central'.
        font_weight (str, opcional): O peso da fonte. Padrão é 'bold'.

    Returns:
        str: Uma string contendo o elemento <text> em SVG.
    """
    return (
        f'<text x="{x}" y="{y}" font-family="{font_family}" font-size="{font_size}" '
        f'fill="{fill}" text-anchor="{text_anchor}" alignment-baseline="{alignment_baseline}" '
        f'font-weight="{font_weight}">{text}</text>'
    )


def parse_svg_path(d: str) -> Tuple[float, float, float, float]:
    """
    Analisa uma string de caminho SVG e calcula a bounding box (caixa delimitadora).

    Args:
        d (str): String contendo o atributo 'd' de um elemento SVG <path>.

    Returns:
        Tuple[float, float, float, float]: Uma tupla contendo (min_x, max_x, min_y, max_y) da bounding box.
    """
    # Remove caracteres não numéricos, substituindo-os por espaços, e separa em uma lista de floats
    coords = list(
        map(
            float,
            filter(
                None,
                "".join(
                    c if c.isdigit() or c == "." or c == "-" else " " for c in d
                ).split(),
            ),
        )
    )

    # Inicializa os limites da bounding box
    min_x = float("inf")
    max_x = float("-inf")
    min_y = float("inf")
    max_y = float("-inf")

    # Variáveis para acompanhar a posição atual
    current_x = 0.0
    current_y = 0.0

    # Processa cada par de coordenadas
    for i in range(0, len(coords), 2):
        dx = coords[i]
        dy = coords[i + 1]

        current_x += dx
        current_y += dy

        # Atualiza os limites da bounding box
        min_x = min(min_x, current_x)
        max_x = max(max_x, current_x)
        min_y = min(min_y, current_y)
        max_y = max(max_y, current_y)

    return min_x, max_x, min_y, max_y


def load_icon(type: str, width: int, height: int) -> str:
    """
    Carrega um ícone SVG do tipo especificado e ajusta sua largura e altura.

    Args:
        type (str): O tipo do ícone a ser carregado (nome do arquivo sem extensão).
        width (int): A largura desejada para o ícone.
        height (int): A altura desejada para o ícone.

    Returns:
        str: Uma string contendo o conteúdo SVG do ícone com a largura e altura ajustadas.
    """
    # Define o caminho do ícone; usa 'generico.svg' se o tipo não for especificado
    icon_path = (
        "assets/icones/generico.svg" if type == "" else f"assets/icones/{type}.svg"
    )

    # Remove hífens do caminho (se necessário)
    icon_path = icon_path.replace("-", "")

    # Registra o namespace SVG vazio
    ET.register_namespace("", "http://www.w3.org/2000/svg")

    # Carrega o arquivo SVG
    tree = ET.parse(icon_path)
    root = tree.getroot()

    # Ajusta a largura e altura do ícone
    root.set("width", str(width))
    root.set("height", str(height))

    # Converte o elemento SVG de volta para string
    svg_str = ET.tostring(root, encoding="unicode")
    return svg_str


def calculate_font_size(base_font_size: float, text: str, width: float) -> float:
    """
    Calcula um tamanho de fonte ajustado para que o texto caiba dentro da largura especificada.

    Args:
        base_font_size (float): O tamanho base da fonte.
        text (str): O texto cujo tamanho será ajustado.
        width (float): A largura máxima disponível para o texto.

    Returns:
        float: O tamanho de fonte ajustado.
    """
    scale_factor = 0.8  # Fator de escala para estimar a largura do texto
    needed_width = len(text) * base_font_size * scale_factor
    if needed_width > width:
        # Ajusta o tamanho da fonte para caber na largura disponível
        return width / (len(text) * scale_factor)
    else:
        return base_font_size


def calculate_transform(
    cx: float, cy: float, svg_width: float, svg_height: float, scale_factor: float
) -> str:
    """
    Calcula a transformação necessária para centralizar e escalar um elemento SVG.

    Args:
        cx (float): Coordenada x do centro onde o SVG deve ser posicionado.
        cy (float): Coordenada y do centro onde o SVG deve ser posicionado.
        svg_width (float): Largura original do SVG.
        svg_height (float): Altura original do SVG.
        scale_factor (float): Fator de escala a ser aplicado ao SVG.

    Returns:
        str: Uma string contendo a transformação 'translate' e 'scale' para uso em um elemento SVG.
    """
    # Calcular o tamanho do SVG após a aplicação do fator de escala
    scaled_width = svg_width * scale_factor
    scaled_height = svg_height * scale_factor

    # Calcular as coordenadas de translação para centralizar o SVG no ponto (cx, cy)
    translate_x = cx - (scaled_width / 2)
    translate_y = cy - (scaled_height / 2)

    # Retorna a transformação no formato apropriado para o atributo 'transform' do SVG
    return f"translate({translate_x}, {translate_y}) scale({scale_factor})"


def create_path_element(props: PathSchema) -> str:
    """
    Cria um elemento SVG <path> com base nas propriedades fornecidas, incluindo ícones e textos associados.

    Args:
        props (PathSchema): Um objeto contendo as propriedades do caminho SVG.

    Returns:
        str: Uma string contendo o elemento SVG completo.
    """
    if props.type == "":
        # Se o tipo não for especificado, cria um elemento <path> simples com os atributos fornecidos
        params = [
            ("fill", props.fill),
            ("d", props.d),
            ("fill-rule", props.fillRule),
            ("id", props.id),
            ("stroke", props.stroke),
            ("stroke-width", props.strokeWidth),
            ("stroke-linecap", props.strokeLinecap),
            ("stroke-linejoin", props.strokeLinejoin),
        ]
        # Filtra os atributos que não estão vazios e formata como strings
        attributes = [f'{key}="{value}"' for key, value in params if value != ""]
        # Constrói o elemento <path>
        path_element = f'<path {" ".join(attributes)} />'
        return path_element

    # Caso contrário, processa para incluir ícones e textos
    d = props.d
    dim = 200  # Dimensão base para ícones

    # Calcula a bounding box do caminho SVG
    min_x, max_x, min_y, max_y = parse_svg_path(d)

    # Calcula o centro e dimensões do caminho
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    width = max_x - min_x
    height = max_y - min_y
    text_distance = height * 0.15

    icon_svg = ""  # Inicializa o ícone como vazio

    # Carrega o ícone apropriado com base no tipo
    if props.type == "sala-de-aula":
        icon_svg = load_icon("sala-de-aula", dim, dim)
    elif props.type == "sala-de-professor":
        icon_svg = load_icon("sala-de-professor", dim, dim)
    elif props.type == "banheiro-masculino":
        icon_svg = load_icon("banheiro-masculino", dim, dim)
    elif props.type == "banheiro-feminino":
        icon_svg = load_icon("banheiro-feminino", dim, dim)
    elif props.type == "biblioteca":
        icon_svg = load_icon("biblioteca", dim, dim)
    elif props.type == "auditorio":
        icon_svg = load_icon("auditorio", dim, dim)
    elif props.type == "laboratorio":
        icon_svg = load_icon("laboratorio", dim, dim)
    elif props.type == "laboratorio-de-pesquisa":
        icon_svg = load_icon("laboratorio-de-pesquisa", dim, dim)
    elif props.type == "generico":
        icon_svg = load_icon("generico", dim, dim)
    else:
        # Se o tipo não corresponder a nenhum conhecido, ajusta o text_distance
        text_distance = dim * 0.15

    # Função interna para renderizar o texto superior
    def render_upper_text(
        title: str,
        center_x: float,
        center_y: float,
        text_distance: float,
        width: float,
        type_: str = "none",
    ) -> str:
        """Renderiza o texto superior centralizado com tamanho de fonte ajustável."""
        # Ajusta a posição y do texto
        adjusted_y = (
            center_y - text_distance - (0 if title == "" and type_ == "none" else 15)
        )
        # Calcula o tamanho da fonte ajustado
        font_size = calculate_font_size(16, title, width) if title else None
        # Cria o elemento de texto SVG
        return create_text(
            text=title.upper(),
            x=center_x,
            y=adjusted_y,
            font_size=str(font_size) if font_size else "14",
        )

    # Função interna para renderizar o texto inferior
    def render_bottom_text(
        description: str,
        center_x: float,
        center_y: float,
        text_distance: float,
        width: float,
        type_: str = "none",
    ) -> str:
        """Renderiza o texto inferior centralizado com tamanho de fonte ajustável."""
        # Ajusta a posição y do texto
        adjusted_y = (
            center_y
            + text_distance
            + (0 if description == "" and type_ == "none" else 15)
        )
        # Calcula o tamanho da fonte ajustado
        font_size = calculate_font_size(12, description, width) if description else None
        # Cria o elemento de texto SVG
        return create_text(
            text=description.upper(),
            x=center_x,
            y=adjusted_y,
            font_size=str(font_size) if font_size else "12",
        )

    # Cria os parâmetros do elemento <path>
    params = [
        ("fill", props.fill),
        ("d", props.d),
        ("fill-rule", props.fillRule),
        ("id", props.id if props.id != "" else props.title),
        ("class", props.type),
    ]

    # Filtra os atributos não vazios
    attributes = [f'{key}="{value}"' for key, value in params if value and value != ""]

    # Constrói o elemento <path>
    path_element = f'<path {" ".join(attributes)} />'

    # Adiciona o ícone dentro de um grupo com transformação
    path_element += f'<g transform="{calculate_transform(center_x, center_y, dim, dim, 0.25)}"> {icon_svg} </g>'

    # Adiciona o texto superior
    path_element += render_upper_text(
        props.title, center_x, center_y, text_distance, width, props.type
    )

    # Adiciona o texto inferior
    path_element += render_bottom_text(
        props.description, center_x, center_y, text_distance, width, props.type
    )

    return path_element


def build_svg_map(map_name: str, write: bool = True) -> str:
    """
    Constrói um mapa SVG com base no nome do mapa fornecido.

    Args:
        map_name (str): Nome do mapa (andar) a ser construído.
        write (bool, opcional): Se True, salva o SVG gerado em um arquivo. Padrão é True.

    Returns:
        str: O conteúdo SVG gerado.
    """
    # Caminho para o arquivo JSON do mapa
    json_path = os.path.join("assets", "andares", f"{map_name}.json")

    # Verifica se o arquivo JSON existe
    if not os.path.isfile(json_path):
        raise Exception(
            f"Arquivo JSON para o andar '{map_name}' não encontrado em '{json_path}'."
        )

    # Carrega os dados do mapa a partir do JSON
    with open(json_path, "r", encoding="utf-8") as file:
        try:
            map_data = json.load(file)
        except json.JSONDecodeError as e:
            raise Exception(f"Erro ao decodificar JSON para o andar '{map_name}': {e}")

    # Cria uma lista de objetos RetanguloSchema a partir dos dados
    rects: list[RetanguloSchema] = [
        RetanguloSchema(
            title=component.get("title", ""),
            description=component.get("description", ""),
            id=component.get("id", ""),
            color=component.get("color", ""),
            colorOnHover=component.get("colorOnHover", ""),
            d=component.get("d", ""),
        )
        for component in map_data
    ]

    elements: list[str] = []

    # Itera sobre os componentes do mapa para criar os elementos SVG
    for component in map_data:
        id = component.get("id", "")
        title = component.get("title", "")

        # Usa o título como ID se o ID não estiver definido
        id = id if id != "" else title

        # Cria o elemento <a> com o elemento do caminho SVG
        elements.append(
            f'<a id="{id}" href="#">'
            + create_path_element(
                PathSchema(
                    fill=component.get("fill", ""),
                    d=component.get("d", ""),
                    id=component.get("id", ""),
                    type=component.get("type", ""),
                    title=component.get("title", ""),
                    description=component.get("description", ""),
                    fillOpacity=component.get("fillOpacity", ""),
                    fillRule=component.get("fillRule", ""),
                    stroke=component.get("stroke", ""),
                    strokeWidth=component.get("strokeWidth", ""),
                    strokeLinecap=component.get("strokeLinecap", ""),
                    strokeLinejoin=component.get("strokeLinejoin", ""),
                )
            )
            + "</a>"
        )

    styles: list[str] = []

    # Cria os estilos CSS para os elementos
    for rect in rects:
        if rect.id == "" and rect.title == "":
            continue

        # Define uma cor padrão para o hover se não estiver definida
        if rect.colorOnHover == "":
            rect.colorOnHover = "#B2BCBE"  # Cor padrão

        # Adiciona o estilo para o ID ou título do retângulo
        styles.append(f"""#{rect.id if rect.id != '' else rect.title} {{
                transition: fill 0.3s ease;
            }}
            a:hover #{rect.id if rect.id != '' else rect.title} {{
                fill: {rect.colorOnHover};
                stroke: black;
                stroke-width: 5px;
                transition: fill 0.4s;
            }}""")

    # Junta os estilos e elementos em strings únicas
    styles_str = "\n".join(styles)
    elements_str = "\n".join(elements)

    # Monta o conteúdo do SVG completo
    svg_content = f"""
<svg version="1.1" viewBox="0.0 0.0 960.0 540.0" fill="none" stroke="none" stroke-linecap="square"
    stroke-miterlimit="10" xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns="http://www.w3.org/2000/svg">
    <style>
    {styles_str}
    </style>
    <defs />
    <clipPath id="g11a8898941b_2_54.0">
        <path d="m0 0l960.0 0l0 540.0l-960.0 0l0 -540.0z" clip-rule="nonzero" />
    </clipPath>
    <g clip-path="url(#g11a8898941b_2_160.0)">
        {elements_str}
    </g>
</svg>"""

    # Se 'write' for True, salva o SVG em um arquivo
    if write:
        processed_path = os.path.join("assets", "processado")
        os.makedirs(processed_path, exist_ok=True)

        output_path = os.path.join(processed_path, f"{map_name}.svg")
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(svg_content)

    return svg_content


def load_map(level: str) -> str:
    """
    Carrega o arquivo SVG correspondente ao andar selecionado.

    Args:
        level (str): O nome do andar a ser carregado.

    Returns:
        str: O conteúdo do arquivo SVG correspondente ou uma mensagem de erro.
    """
    # Mapeia a escolha do usuário para o arquivo SVG correto
    arquivos_svg = {
        "Subsolo": "assets/processado/subsolo.svg",
        "Térreo": "assets/processado/terreo.svg",
        "Primeiro Andar": "assets/processado/primeiro_andar.svg",
        "Segundo Andar": "assets/processado/segundo_andar.svg",
        "Terceiro Andar": "assets/processado/terceiro_andar.svg",
    }

    # Obtém o caminho do arquivo SVG correspondente
    caminho_arquivo = arquivos_svg.get(level, None)
    if caminho_arquivo is None:
        return f"O mapa SVG do {level} não foi encontrado."

    # Tenta abrir e ler o conteúdo do arquivo SVG
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo_svg:
            return arquivo_svg.read()
    except FileNotFoundError:
        return f"O mapa SVG do {level} não foi encontrado."


if __name__ == "__main__":
    # Lista de andares para os quais o mapa SVG será construído
    _andares = [
        "subsolo",
        "terreo",
        "primeiro_andar",
        "segundo_andar",
        "terceiro_andar",
    ]

    # Constrói o mapa SVG para cada andar na lista
    for andar in _andares:
        build_svg_map(andar)
