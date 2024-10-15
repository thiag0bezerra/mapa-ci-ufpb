# Projeto de Visualização de Salas do Centro de Informática

Este projeto gera mapas SVG e permite a visualização interativa de mapas, suas salas e horários, além de possibilitar a análise de dados.

## Requisitos

- Python 3.11 ou superior

## Configuração do Ambiente Virtual

### Linux

1. Crie e ative o ambiente virtual:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

### Windows (PowerShell)

1. Crie e ative o ambiente virtual:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate
   ```

2. Instale as dependências:

   ```powershell
   pip install -r requirements.txt
   ```

## Geração dos Mapas SVG

Para gerar os mapas em formato SVG, execute o seguinte comando:

```bash
python3 -m src.svg.mapa
```

## Executando a Aplicação Streamlit

Para visualizar o mapa da sala e horários de maneira interativa via Streamlit, execute:

```bash
python3 -m streamlit run src/app/web.py
```


