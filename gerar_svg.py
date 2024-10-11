import json
import re
import os
import logging
from dataclasses import dataclass
from typing import Optional, List, Tuple

import xml.etree.ElementTree as ET

# Configurar o logging para registrar avisos
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

@dataclass
class Icone:
    caminho_svg: str
    largura: int
    altura: int
    posicao_x: float
    posicao_y: float

@dataclass
class Texto:
    titulo: Optional[str]
    descricao: Optional[str]
    posicao_x: float
    posicao_y: float
    tamanho_fonte_titulo: int = 14
    peso_fonte_titulo: str = "bold"
    tamanho_fonte_descricao: int = 12

@dataclass
class Sala:
    id: str
    fill: str
    d: str
    fill_rule: str
    stroke: str
    stroke_width: str
    stroke_linecap: str
    stroke_linejoin: str
    tipo: str
    titulo: Optional[str]
    descricao: Optional[str]
    icone: Icone
    texto: Texto
    minX: float
    maxX: float
    minY: float
    maxY: float

def carregar_svg_icone(caminho_svg: str, largura: int, altura: int) -> str:
    """
    Carrega um ícone SVG de um arquivo e ajusta os atributos de largura e altura.

    Args:
        caminho_svg (str): O caminho para o arquivo SVG.
        largura (int): A nova largura desejada.
        altura (int): A nova altura desejada.

    Returns:
        str: O conteúdo do SVG ajustado como string.
    """
    tree = ET.parse(caminho_svg)
    root = tree.getroot()

    root.set('width', str(largura))
    root.set('height', str(altura))

    svg_str = ET.tostring(root, encoding='unicode')
    return svg_str

def parse_svg_path(d: str) -> Tuple[float, float, float, float]:
    """
    Analisa uma string de dados de caminho SVG e retorna as coordenadas da caixa delimitadora.

    Args:
        d (str): O atributo 'd' de um caminho SVG.

    Returns:
        Tuple[float, float, float, float]: (minX, maxX, minY, maxY)
    """
    # Remove letras e divide em valores numéricos
    _coords = re.sub(r"[a-zA-Z]", " ", d).split()
    coords = []

    # Converter para floats e filtrar valores válidos
    for coord in _coords:
        try:
            coords.append(float(coord))
        except ValueError:
            logging.warning(f"Valor não numérico encontrado na string do caminho SVG: '{coord}'")

    # Verificar se o número de coordenadas é par
    if len(coords) % 2 != 0:
        logging.warning("Número ímpar de coordenadas encontrado no caminho SVG. A última coordenada será ignorada.")
        coords = coords[:-1]  # Ignorar a última coordenada

    # Inicializar variáveis da caixa delimitadora
    minX, maxX = float("inf"), float("-inf")
    minY, maxY = float("inf"), float("-inf")

    # Variáveis para rastrear a posição atual
    currentX, currentY = 0.0, 0.0

    # Processar cada par de coordenadas
    for i in range(0, len(coords), 2):
        deltaX = coords[i]
        deltaY = coords[i + 1]
        currentX += deltaX
        currentY += deltaY

        minX = min(minX, currentX)
        maxX = max(maxX, currentX)
        minY = min(minY, currentY)
        maxY = max(maxY, currentY)

    return minX, maxX, minY, maxY

def criar_sala(component: dict) -> Sala:
    """
    Cria uma instância da dataclass Sala a partir de um componente de dados.

    Args:
        component (dict): Dicionário contendo atributos do caminho SVG e metadados adicionais.

    Returns:
        Sala: Instância da dataclass Sala.
    """
    minX, maxX, minY, maxY = parse_svg_path(component['d'])
    centerX = (minX + maxX) / 2
    centerY = (minY + maxY) / 2

    icones = {
        "sala-de-aula": "assets/icones/saladeaula.svg",
        "sala-de-professor": "assets/icones/salaprofessor.svg",
        "banheiro-masculino": "assets/icones/banheiromasculino.svg",
        "banheiro-feminino": "assets/icones/banheirofeminino.svg",
        "biblioteca": "assets/icones/biblioteca.svg",
        "auditorio": "assets/icones/auditorio.svg",
        "laboratorio": "assets/icones/laboratorio.svg",
        "laboratorio-de-pesquisa": "assets/icones/laboratoriodepesquisa.svg",
        "generico": "assets/icones/generico.svg"
    }

    caminho_icone = icones.get(component.get('type', ''), "assets/icones/generico.svg")
    icone_svg = carregar_svg_icone(caminho_icone, 40, 40)

    icone = Icone(
        caminho_svg=caminho_icone,
        largura=40,
        altura=40,
        posicao_x=centerX - 20,
        posicao_y=centerY - 20
    )

    texto = Texto(
        titulo=component.get('title'),
        descricao=component.get('description'),
        posicao_x=centerX,
        posicao_y=centerY,
    )

    sala = Sala(
        id=component.get('id', ''),
        fill=component.get('fill', ''),
        d=component.get('d', ''),
        fill_rule=component.get('fillRule', ''),
        stroke=component.get('stroke', ''),
        stroke_width=component.get('strokeWidth', ''),
        stroke_linecap=component.get('strokeLinecap', ''),
        stroke_linejoin=component.get('strokeLinejoin', ''),
        tipo=component.get('type', ''),
        titulo=component.get('title'),
        descricao=component.get('description'),
        icone=icone,
        texto=texto,
        minX=minX,
        maxX=maxX,
        minY=minY,
        maxY=maxY
    )

    return sala

def gerar_elemento_svg(sala: Sala) -> str:
    """
    Gera o código SVG para uma única sala, incluindo ícone e texto.

    Args:
        sala (Sala): Instância da dataclass Sala.

    Returns:
        str: Código SVG gerado para a sala.
    """
    path_element = '<path'

    atributos = {
        'fill': sala.fill,
        'd': sala.d,
        'fill-rule': sala.fill_rule,
        'id': sala.id,
        'stroke': sala.stroke,
        'stroke-width': sala.stroke_width,
        'stroke-linecap': sala.stroke_linecap,
        'stroke-linejoin': sala.stroke_linejoin
    }

    for attr, valor in atributos.items():
        if valor:
            path_element += f' {attr}="{valor}"'

    path_element += '/>'

    if not sala.tipo:
        return path_element

    icone_svg = carregar_svg_icone(sala.icone.caminho_svg, sala.icone.largura, sala.icone.altura)
    icon_element = f'<g transform="translate({sala.icone.posicao_x}, {sala.icone.posicao_y})">{icone_svg}</g>'

    textos = []
    distancia_texto = 15

    if sala.titulo:
        titulo_texto = sala.titulo.upper()
        textos.append(
            f'<text x="{sala.texto.posicao_x}" y="{sala.texto.posicao_y - distancia_texto}" '
            f'font-size="{sala.texto.tamanho_fonte_titulo}" font-weight="{sala.texto.peso_fonte_titulo}" '
            f'text-anchor="middle" alignment-baseline="central">{titulo_texto}</text>'
        )

    if sala.descricao:
        descricao_texto = sala.descricao.upper()
        textos.append(
            f'<text x="{sala.texto.posicao_x}" y="{sala.texto.posicao_y + distancia_texto}" '
            f'font-size="{sala.texto.tamanho_fonte_descricao}" text-anchor="middle" '
            f'alignment-baseline="central">{descricao_texto}</text>'
        )

    text_elements = "\n".join(textos)

    return f"{path_element}\n{icon_element}\n{text_elements}"

def gerar_svg_andar(nome_andar: str) -> None:
    """
    Gera o código SVG para um determinado andar lendo seus dados em JSON.

    Args:
        nome_andar (str): O nome do andar (ex.: 'subsolo').

    Returns:
        None
    """
    caminho_json = os.path.join("assets", "andares", f"{nome_andar}.json")
    if not os.path.isfile(caminho_json):
        logging.error(f"Arquivo JSON para o andar '{nome_andar}' não encontrado em '{caminho_json}'.")
        return

    with open(caminho_json, "r", encoding="utf-8") as arquivo:
        try:
            dados_andar = json.load(arquivo)
        except json.JSONDecodeError as e:
            logging.error(f"Erro ao decodificar JSON para o andar '{nome_andar}': {e}")
            return

    salas: List[Sala] = []
    for componente in dados_andar:
        try:
            sala = criar_sala(componente)
            salas.append(sala)
        except KeyError as e:
            logging.warning(f"Componente faltando chave {e} no andar '{nome_andar}'. Componente ignorado.")
        except Exception as e:
            logging.warning(f"Erro ao criar sala para componente no andar '{nome_andar}': {e}")

    elementos_svg = [gerar_elemento_svg(sala) for sala in salas]

    cabecalho_svg = """<svg version="1.1" viewBox="0 0 960 540" fill="none" stroke="none" stroke-linecap="square" stroke-miterlimit="10" xmlns="http://www.w3.org/2000/svg">
    <defs />
    """

    rodape_svg = "</svg>"

    codigo_svg = f"{cabecalho_svg}\n" + "\n".join(elementos_svg) + f"\n{rodape_svg}"

    caminho_processado = os.path.join("assets", "processado")
    os.makedirs(caminho_processado, exist_ok=True)

    caminho_saida = os.path.join(caminho_processado, f"{nome_andar}.svg")
    with open(caminho_saida, "w", encoding="utf-8") as arquivo_saida:
        arquivo_saida.write(codigo_svg)

    logging.info(f"SVG para o andar '{nome_andar}' gerado com sucesso em '{caminho_saida}'.")

if __name__ == "__main__":

    _andares = [
        "subsolo",
        "terreo",
        "primeiro_andar",
        "segundo_andar",
        "terceiro_andar",
    ]

    for andar in _andares:
        gerar_svg_andar(andar)
