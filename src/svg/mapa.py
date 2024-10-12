from dataclasses import dataclass
from typing import Tuple
import json
import os
import xml.etree.ElementTree as ET


@dataclass
class RetanguloSchema:
    title: str
    description: str
    id: str
    color: str
    colorOnHover: str
    d: str


@dataclass
class PathSchema:
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
    return (
        f'<text x="{x}" y="{y}" font-family="{font_family}" font-size="{font_size}" '
        f'fill="{fill}" text-anchor="{text_anchor}" alignment-baseline="{alignment_baseline}" '
        f'font-weight="{font_weight}">{text}</text>'
    )


def parse_svg_path(d: str) -> Tuple[float, float, float, float]:
    """
    Parseia uma string de caminho SVG e calcula a bounding box (caixa delimitadora).

    Args:
        d (str): String contendo o caminho SVG.

    Returns:
        Dict[str, float]: Dicionário contendo minX, maxX, minY e maxY.
    """
    # Remove letras e divide em valores numéricos
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

    # Inicializa variáveis de bounding box
    min_x, max_x, min_y, max_y = (
        float("inf"),
        float("-inf"),
        float("inf"),
        float("-inf"),
    )

    # Variáveis para acompanhar a posição atual
    current_x, current_y = 0.0, 0.0

    # Processa cada par de coordenadas
    for i in range(0, len(coords), 2):
        current_x += coords[i]
        current_y += coords[i + 1]

        # Atualiza os limites da bounding box
        min_x = min(min_x, current_x)
        max_x = max(max_x, current_x)
        min_y = min(min_y, current_y)
        max_y = max(max_y, current_y)

    return min_x, max_x, min_y, max_y


def load_icon(type: str, width: int, height: int) -> str:
    icon_path = (
        "assets/icones/generico.svg" if type == "" else f"assets/icones/{type}.svg"
    )
    ET.register_namespace("", "http://www.w3.org/2000/svg")

    tree = ET.parse(icon_path.replace("-", ""))
    root = tree.getroot()

    root.set("width", str(width))
    root.set("height", str(height))

    svg_str = ET.tostring(root, encoding="unicode")
    return svg_str


def calculate_font_size(base_font_size: float, text: str, width: float) -> float:
    scale_factor = 0.8
    needed_width = len(text) * base_font_size * scale_factor
    if needed_width > width:
        return width / (len(text) * scale_factor)
    return base_font_size


def calculate_transform(
    cx: float, cy: float, svg_width: float, svg_height: float, scale_factor: float
) -> str:
    # Calcular o tamanho do SVG após a aplicação do fator de escala
    scaled_width = svg_width * scale_factor
    scaled_height = svg_height * scale_factor

    # Calcular as coordenadas de translação para centralizar o SVG
    translate_x = cx - (scaled_width / 2)
    translate_y = cy - (scaled_height / 2)

    # Retorna a transformação no formato apropriado para o SVG
    return f"translate({translate_x}, {translate_y}) scale({scale_factor})"


def create_path_element(props: PathSchema) -> str:
    if props.type == "":
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
        return f'<path {' '.join([f'{param[0]}="{param[1]}"' for param in params if param[1] != ""])} />'

    d = props.d
    dim = 200

    minX, maxX, minY, maxY = parse_svg_path(d)

    centerX = (minX + maxX) / 2
    centerY = (minY + maxY) / 2
    width = maxX - minX
    height = maxY - minY
    text_distance = height * 0.15

    icone = ""

    if props.type == "sala-de-aula":
        icone = load_icon("sala-de-aula", dim, dim)
    elif props.type == "sala-de-professor":
        icone = load_icon("sala-de-professor", dim, dim)
    elif props.type == "banheiro-masculino":
        icone = load_icon("banheiro-masculino", dim, dim)
    elif props.type == "banheiro-feminino":
        icone = load_icon("banheiro-feminino", dim, dim)
    elif props.type == "biblioteca":
        icone = load_icon("biblioteca", dim, dim)
    elif props.type == "auditorio":
        icone = load_icon("auditorio", dim, dim)
    elif props.type == "laboratorio":
        icone = load_icon("laboratorio", dim, dim)
    elif props.type == "laboratorio-de-pesquisa":
        icone = load_icon("laboratorio-de-pesquisa", dim, dim)
    elif props.type == "generico":
        icone = load_icon("generico", dim, dim)
    else:
        text_distance = dim * 0.15


    def render_upper_text(
        title: str,
        center_x: float,
        center_y: float,
        text_distance: float,
        width: float,
        type_: str = "none",
    ) -> str:
        """Renderiza o texto superior centralizado com tamanho de fonte ajustável."""
        adjusted_y = (
            center_y - text_distance - (0 if title == "" and type_ == "none" else 15)
        )
        font_size = calculate_font_size(16, title, width) if title else None
        return create_text(
            text=title.upper(),
            x=center_x,
            y=adjusted_y,
            font_size=str(font_size) if font_size else "14",
        )

    def render_bottom_text(
        description: str,
        center_x: float,
        center_y: float,
        text_distance: float,
        width: float,
        type_: str = "none",
    ) -> str:
        """Renderiza o texto inferior centralizado com tamanho de fonte ajustável."""
        adjusted_y = (
            center_y
            + text_distance
            + (0 if description == "" and type_ == "none" else 15)
        )
        font_size = calculate_font_size(12, description, width) if description else None
        return create_text(
            text=description.upper(),
            x=center_x,
            y=adjusted_y,
            font_size=str(font_size) if font_size else "12",
        )

    params = [
        ("fill", props.fill),
        ("d", props.d),
        ("fill-rule", props.fillRule),
        ("id", props.id if props.id != '' else props.title),
        ("class", props.type)
    ]

    path_element = f'<path {' '.join([f'{param[0]}="{param[1]}"' for param in params if param[1] != ""])} />'
    path_element += f'<g transform="{calculate_transform(centerX,centerY,dim,dim,0.25)}"> {icone} </g>'
    path_element += render_upper_text(props.title, centerX, centerY, text_distance, width, props.type)
    path_element += render_bottom_text(props.description, centerX, centerY, text_distance, width, props.type)

    return path_element


def svg_map(map_name: str, write: bool = True) -> tuple[str, str]:
    svg_id = map_name.replace("_", "-")

    json_path = os.path.join("assets", "andares", f"{map_name}.json")
    if not os.path.isfile(json_path):
        raise Exception(
            f"Arquivo JSON para o andar '{map_name}' não encontrado em '{json_path}'."
        )

    with open(json_path, "r", encoding="utf-8") as file:
        try:
            map_data = json.load(file)
        except json.JSONDecodeError as e:
            raise Exception(f"Erro ao decodificar JSON para o andar '{map_name}': {e}")

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

    elements: list[str] = [
        create_path_element(
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
        for component in map_data
    ]

    styles: list[str] = []

    for rect in rects:

        if rect.id == '' and rect.title == '':
            continue
        
        
        if rect.colorOnHover == '':
            rect.colorOnHover = 'blue'
        
        styles.append(f"""
{svg_id} path#{rect.id if rect.id != '' else rect.title}:hover {{
fill: {rect.colorOnHover};
stroke: red;
stroke-width: 3px;
transition: fill 0.4s;
}}""")

    svg_content = f"""
<svg version="1.1" viewBox="0.0 0.0 960.0 540.0" fill="none" stroke="none" stroke-linecap="square"
    stroke-miterlimit="10" xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns="http://www.w3.org/2000/svg">
    <defs />
    <clipPath id="g11a8898941b_2_54.0">
        <path d="m0 0l960.0 0l0 540.0l-960.0 0l0 -540.0z" clip-rule="nonzero" />
    </clipPath>
    <g clip-path="url(#g11a8898941b_2_160.0)">
        {'\n'.join(elements)}
    </g>
</svg>"""

    if write:
        processed_path = os.path.join("assets", "processado")
        os.makedirs(processed_path, exist_ok=True)

        output_path = os.path.join(processed_path, f"{map_name}.svg")
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(svg_content)

        output_path = os.path.join(processed_path, f"{map_name}.css")
        with open(output_path, "w", encoding="utf-8") as file:
            file.write('\n'.join(styles))


    return svg_content, '\n'.join(styles)


if __name__ == "__main__":
    _andares = [
        "subsolo",
        "terreo",
        "primeiro_andar",
        "segundo_andar",
        "terceiro_andar",
    ]

    for andar in _andares:
        svg_map(andar)
