# README do Codigo - Analise de Acidentes PRF

Este documento explica o codigo do projeto com mais calma, quase como se fosse uma apresentacao guiada. A ideia e mostrar o que cada parte faz, por que ela existe e como as pecas se conectam.

O arquivo principal analisado aqui e:

`notebooks/acidentes_prf_trabalho_part1.ipynb`

Tambem sao explicados os modulos auxiliares:

- `src/etl/schema.py`
- `src/utils/benchmark.py`
- `src/utils/plotting.py`

## Visao geral

O projeto funciona como uma linha de producao de dados:

1. Os CSVs brutos entram pela pasta `data/raw/`.
2. O codigo confere se as colunas esperadas existem.
3. Os CSVs sao lidos com tipos definidos por schema.
4. A data e o horario sao combinados em `data_hora`.
5. Os dados sao salvos em Parquet, um formato mais eficiente para analise.
6. O notebook executa consultas por volume temporal.
7. Os graficos sao gerados e salvos em `reports/`.
8. O benchmark compara Pandas, Polars, PyArrow e Dask.
9. A Parte 4 executa Dask distribuido com 1, 2 e 3 workers.

Uma analogia simples: imagine uma fabrica. O CSV bruto e a materia-prima; o schema e o molde; o Parquet e o produto embalado de forma compacta; os graficos e relatorios sao a vitrine; o Dask distribuido e quando a fabrica chama mais equipes para dividir o trabalho.

## Celula inicial do notebook

Trecho:

```python
import os
import sys
import glob
import textwrap
from datetime import datetime
from pathlib import Path

import pandas as pd
import polars as pl
import pyarrow.compute as pc
import pyarrow.dataset as ds
import dask.dataframe as dd
from dask.distributed import Client, LocalCluster
import matplotlib.pyplot as plt
import seaborn as sns
```

Explicacao:

- `os`: usado para criar pastas e trabalhar com operacoes do sistema.
- `sys`: usado para permitir que o notebook encontre os modulos locais dentro de `src/`.
- `glob`: procura arquivos por padrao, como todos os `*.csv`.
- `textwrap`: quebra textos longos, usado no grafico de causas para melhorar leitura.
- `datetime`: converte strings de data para objetos de data e hora.
- `Path`: cria caminhos de arquivo de forma mais organizada que strings soltas.
- `pandas`: biblioteca principal para leitura, validacao e agregacoes locais.
- `polars`: biblioteca usada no benchmark, com leitura lazy de Parquet.
- `pyarrow.compute`: funcoes de filtro e comparacao usadas pelo PyArrow.
- `pyarrow.dataset`: permite consultar uma pasta de Parquets como um dataset.
- `dask.dataframe`: usado para DataFrames distribuidos.
- `Client` e `LocalCluster`: conectam ao Dask local ou distribuido.
- `matplotlib.pyplot`: base para criacao dos graficos.
- `seaborn`: biblioteca de graficos estatisticos, usada por cima do Matplotlib.

Analogia: esse bloco e como separar todas as ferramentas na bancada antes de comecar. O Pandas e uma chave de fenda muito versatil; o Polars e uma ferramenta eletrica rapida; o PyArrow e uma ferramenta especializada em formato colunar; o Dask e a equipe que divide tarefas.

## Configuracao de caminhos

Trecho:

```python
BASE_DIR = Path.cwd()
if BASE_DIR.name == "notebooks":
    BASE_DIR = BASE_DIR.parent

RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"
PARQUET_DIR = PROCESSED_DATA_DIR / "dados_otimizados"

PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
```

Explicacao linha a linha:

- `BASE_DIR = Path.cwd()`: pega a pasta atual onde o notebook esta rodando.
- `if BASE_DIR.name == "notebooks":`: verifica se o usuario abriu o notebook de dentro da pasta `notebooks`.
- `BASE_DIR = BASE_DIR.parent`: se estiver dentro de `notebooks`, sobe um nivel para chegar na raiz do projeto.
- `RAW_DATA_DIR = ...`: define onde ficam os CSVs originais.
- `PROCESSED_DATA_DIR = ...`: define onde ficam dados processados.
- `REPORTS_DIR = ...`: define onde graficos e relatorios serao salvos.
- `PARQUET_DIR = ...`: define a subpasta dos arquivos Parquet.
- `mkdir(..., exist_ok=True)`: cria as pastas se elas ainda nao existirem.

Exemplo: se o notebook estiver rodando em `pad_acidentes_prf/notebooks`, o codigo percebe isso e usa `pad_acidentes_prf` como raiz. Isso evita erro de caminho quando alguem abre o notebook em lugares diferentes.

## Importacao dos modulos locais

Trecho:

```python
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.etl.schema import (
    DATE_COLUMNS,
    SCHEMA_PANDAS,
    TIME_COLUMNS,
    columns_to_read,
    validate_dataframe_quality,
    validate_required_columns,
)
from src.utils.benchmark import conversion_size_report, measure_seconds
from src.utils.plotting import apply_dark_theme, save_report_figure
```

Explicacao:

- `sys.path` e a lista de lugares onde o Python procura modulos.
- O projeto tem codigo em `src/`, entao a raiz precisa estar em `sys.path`.
- `SCHEMA_PANDAS` traz os tipos esperados das colunas.
- `DATE_COLUMNS` e `TIME_COLUMNS` informam quais colunas sao de data e hora.
- `columns_to_read` evita tentar ler colunas ausentes.
- `validate_dataframe_quality` gera relatorios de qualidade.
- `validate_required_columns` confere se todos os CSVs possuem as colunas obrigatorias.
- `conversion_size_report` compara tamanho CSV versus Parquet.
- `measure_seconds` mede tempo de execucao.
- `apply_dark_theme` padroniza o visual dos graficos.
- `save_report_figure` salva graficos na pasta `reports/`.

Analogia: em vez de escrever tudo dentro do notebook, algumas ferramentas foram guardadas em uma caixa chamada `src/`. O notebook apenas pega essas ferramentas quando precisa.

## Parte 1 - Schema e validacao

### Criacao da pasta de saida

Trecho:

```python
pasta_saida = PARQUET_DIR
os.makedirs(pasta_saida, exist_ok=True)
```

Explicacao:

- `pasta_saida = PARQUET_DIR`: escolhe a pasta onde os Parquets serao salvos.
- `os.makedirs(...)`: cria essa pasta se ela nao existir.
- `exist_ok=True`: evita erro se a pasta ja existir.

Exemplo: se `data/processed/dados_otimizados` ainda nao existir, o codigo cria. Se ja existir, ele segue normalmente.

### Busca dos arquivos CSV

Trecho:

```python
caminho_busca = str(RAW_DATA_DIR / "*.csv")
arquivos_csv = sorted(glob.glob(caminho_busca))

print(f"Encontrei {len(arquivos_csv)} arquivos CSV em {RAW_DATA_DIR}!")
```

Explicacao:

- `RAW_DATA_DIR / "*.csv"` monta um padrao para procurar todos os CSVs.
- `glob.glob(caminho_busca)` retorna os caminhos encontrados.
- `sorted(...)` coloca os arquivos em ordem, geralmente por ano.
- `print(...)` informa quantos arquivos foram encontrados.

Analogia: e como dizer "procure em uma gaveta todos os papeis que terminam com `.csv` e organize por ordem".

### Definicao do schema

Trecho:

```python
meu_schema = SCHEMA_PANDAS
colunas_data = DATE_COLUMNS
colunas_hora = TIME_COLUMNS
```

Explicacao:

- `meu_schema` recebe o dicionario de tipos esperado.
- `colunas_data` recebe a lista de colunas que devem virar data.
- `colunas_hora` recebe a lista de colunas de horario.

O schema funciona como um contrato. Ele diz: "a coluna `uf` deve ser categoria", "a coluna `mortos` deve ser inteiro pequeno", "a coluna `br` deve ser texto".

## Modulo `src/etl/schema.py`

Esse modulo centraliza a parte de schema e validacao. Isso evita copiar o mesmo dicionario de tipos em varias celulas.

### Schema principal

Trecho:

```python
SCHEMA_PANDAS = {
    "id": "Int64",
    "dia_semana": "category",
    "uf": "category",
    "br": "string",
    "municipio": "category",
    "causa_acidente": "category",
    "tipo_acidente": "category",
    "fase_dia": "category",
    "condicao_metereologica": "category",
    "tipo_pista": "category",
    "tracado_via": "category",
    "ilesos": "Int16",
    "feridos_leves": "Int16",
    "feridos_graves": "Int16",
    "mortos": "Int8",
}
```

Explicacao:

- O dicionario tem formato `"coluna": "tipo"`.
- `category` e usado em colunas repetitivas, como UF, municipio e causa.
- `string` e usado para texto.
- `Int16` e `Int8` economizam memoria em numeros pequenos.
- `Int64` e usado para `id`, que pode ser maior.

Exemplo: a coluna `uf` repete valores como `AM`, `MG`, `SP`. Como sao poucos valores repetidos, `category` e mais economico que texto puro.

Analogia: guardar `uf` como texto seria escrever "MG" milhares de vezes. Guardar como categoria e como criar uma tabela de codigos: `1 = MG`, `2 = SP`, `3 = AM`.

### Colunas especiais

Trecho:

```python
DATE_COLUMNS = ["data_inversa"]
TIME_COLUMNS = ["horario"]
NUMERIC_NON_NEGATIVE_COLUMNS = ["ilesos", "feridos_leves", "feridos_graves", "mortos"]
```

Explicacao:

- `DATE_COLUMNS`: colunas que representam datas.
- `TIME_COLUMNS`: colunas que representam horarios.
- `NUMERIC_NON_NEGATIVE_COLUMNS`: colunas que nao deveriam ter numeros negativos.

Exemplo: nao faz sentido ter `mortos = -2`, entao a validacao verifica se isso ocorre.

### Funcao `expected_columns`

Trecho:

```python
def expected_columns() -> list[str]:
    """Retorna as colunas esperadas no dataset bruto."""
    return list(SCHEMA_PANDAS.keys()) + DATE_COLUMNS + TIME_COLUMNS
```

Explicacao:

- `def expected_columns()`: cria uma funcao.
- `-> list[str]`: indica que ela retorna uma lista de strings.
- `SCHEMA_PANDAS.keys()`: pega os nomes das colunas do schema.
- `+ DATE_COLUMNS + TIME_COLUMNS`: adiciona data e horario.
- `return`: devolve a lista final.

Analogia: e a lista de chamada da sala. Todo CSV precisa ter os nomes dessa lista.

### Funcao `available_columns`

Trecho:

```python
def available_columns(csv_path: str | Path, sep: str = ";", encoding: str = "latin1") -> list[str]:
    """Le apenas o cabecalho do CSV para descobrir as colunas disponiveis."""
    return list(pd.read_csv(csv_path, sep=sep, encoding=encoding, nrows=0).columns)
```

Explicacao:

- `csv_path`: caminho do CSV.
- `sep=";"`: os arquivos da PRF usam ponto e virgula como separador.
- `encoding="latin1"`: codificacao comum em bases brasileiras antigas.
- `nrows=0`: le apenas o cabecalho, sem carregar milhoes de linhas.
- `.columns`: pega os nomes das colunas.

Analogia: em vez de ler o livro inteiro, o codigo le so o sumario para saber os capitulos.

### Funcao `columns_to_read`

Trecho:

```python
def columns_to_read(csv_path: str | Path, sep: str = ";", encoding: str = "latin1") -> list[str]:
    """Cruza schema esperado com colunas existentes para evitar erro por coluna ausente."""
    present_columns = set(available_columns(csv_path, sep=sep, encoding=encoding))
    return [column for column in expected_columns() if column in present_columns]
```

Explicacao:

- `present_columns` pega as colunas que existem no CSV.
- `set(...)` transforma em conjunto para busca mais rapida.
- A lista final mantem apenas colunas esperadas que realmente existem.

Isso protege a leitura. Se um CSV antigo nao tiver uma coluna esperada, o codigo nao quebra imediatamente na leitura.

### Funcao `validate_required_columns`

Trecho:

```python
def validate_required_columns(
    csv_paths: Iterable[str | Path],
    required_columns: Iterable[str] | None = None,
    sep: str = ";",
    encoding: str = "latin1",
) -> pd.DataFrame:
    """Gera relatorio de colunas ausentes por arquivo CSV."""
    required = list(required_columns or expected_columns())
    rows = []

    for csv_path in csv_paths:
        path = Path(csv_path)
        present = set(available_columns(path, sep=sep, encoding=encoding))
        missing = [column for column in required if column not in present]
        rows.append(
            {
                "arquivo": path.name,
                "colunas_esperadas": len(required),
                "colunas_ausentes": len(missing),
                "lista_colunas_ausentes": ", ".join(missing) if missing else "Nenhuma",
            }
        )

    return pd.DataFrame(rows)
```

Explicacao por blocos:

- A funcao recebe varios caminhos de CSV.
- `required` define quais colunas sao obrigatorias.
- `rows = []` cria uma lista para guardar o resultado de cada arquivo.
- O `for` percorre CSV por CSV.
- `present` pega as colunas existentes naquele arquivo.
- `missing` calcula quais obrigatorias nao apareceram.
- `rows.append(...)` guarda um registro de validacao.
- `pd.DataFrame(rows)` transforma a lista em tabela.

Exemplo de saida: se um arquivo tiver todas as colunas, `colunas_ausentes` sera `0` e `lista_colunas_ausentes` sera `Nenhuma`.

### Funcao `validate_dataframe_quality`

Trecho resumido:

```python
def validate_dataframe_quality(df: pd.DataFrame, schema: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Cria relatorios simples de tipos, nulos e valores invalidos."""
    schema = schema or SCHEMA_PANDAS

    type_rows = []
    for column, expected_type in schema.items():
        if column not in df.columns:
            type_rows.append({
                "coluna": column,
                "tipo_esperado": expected_type,
                "tipo_encontrado": "AUSENTE",
                "status": "ausente",
            })
            continue

        found_type = str(df[column].dtype)
        type_rows.append({
            "coluna": column,
            "tipo_esperado": expected_type,
            "tipo_encontrado": found_type,
            "status": "ok" if found_type == expected_type else "verificar",
        })
```

Explicacao:

- A funcao recebe um DataFrame ja carregado.
- Se nenhum schema for passado, usa `SCHEMA_PANDAS`.
- Percorre cada coluna esperada.
- Se a coluna nao existir, marca como `AUSENTE`.
- Se existir, compara tipo esperado com tipo encontrado.
- Se bater, status `ok`; se nao bater, status `verificar`.

Trecho de nulos:

```python
null_report = (
    df.isna()
    .sum()
    .reset_index()
    .rename(columns={"index": "coluna", 0: "qtd_nulos"})
    .sort_values("qtd_nulos", ascending=False)
)
null_report["percentual_nulos"] = (null_report["qtd_nulos"] / len(df) * 100).round(2)
```

Explicacao:

- `df.isna()` marca valores vazios.
- `.sum()` conta quantos vazios existem em cada coluna.
- `.reset_index()` transforma o resultado em tabela.
- `.rename(...)` melhora os nomes das colunas.
- `.sort_values(...)` coloca as colunas com mais nulos no topo.
- A ultima linha calcula percentual de nulos.

Trecho de invalidos:

```python
for column in NUMERIC_NON_NEGATIVE_COLUMNS:
    if column in df.columns:
        invalid_rows.append({
            "coluna": column,
            "regra": "valor >= 0",
            "valores_invalidos": int((df[column] < 0).sum()),
        })
```

Explicacao:

- Percorre colunas como `mortos` e `feridos_graves`.
- Verifica se ha valores menores que zero.
- Conta quantos invalidos existem.

Analogia: essa funcao e como um fiscal de qualidade. Ela nao muda o produto; apenas aponta se existe algo fora do padrao.

## Conversao CSV para Parquet

Trecho:

```python
for arquivo in arquivos_csv:
    ano = Path(arquivo).stem.replace("acidentes", "")[:4]
    print(f"[{ano}] Lendo CSV e aplicando schema...")

    try:
        colunas_para_ler = columns_to_read(arquivo)

        df = pd.read_csv(
            arquivo,
            sep=";",
            encoding="latin1",
            dtype=meu_schema,
            parse_dates=colunas_data,
            usecols=colunas_para_ler,
        )
```

Explicacao linha a linha:

- `for arquivo in arquivos_csv`: repete o processo para cada CSV anual.
- `ano = ...`: extrai o ano do nome do arquivo.
- `print(...)`: mostra andamento no notebook.
- `try`: tenta executar o bloco; se der erro, cai no `except`.
- `columns_to_read(arquivo)`: decide quais colunas ler.
- `pd.read_csv(...)`: le o CSV.
- `sep=";"`: define separador.
- `encoding="latin1"`: define codificacao.
- `dtype=meu_schema`: aplica tipos definidos.
- `parse_dates=colunas_data`: converte `data_inversa` para data.
- `usecols=colunas_para_ler`: le apenas as colunas desejadas.

Trecho de criacao de `data_hora`:

```python
if "horario" in df.columns:
    df["data_hora"] = pd.to_datetime(
        df["data_inversa"].dt.strftime("%Y-%m-%d") + " " + df["horario"].astype(str),
        errors="coerce",
    )
```

Explicacao:

- Verifica se a coluna `horario` existe.
- Transforma `data_inversa` em texto no formato `YYYY-MM-DD`.
- Junta data e horario com um espaco no meio.
- `pd.to_datetime(...)` converte o texto final em data e hora real.
- `errors="coerce"` transforma valores problemáticos em `NaT`, em vez de quebrar o notebook.

Exemplo:

```text
data_inversa = 2017-01-01
horario = 13:45:00
data_hora = 2017-01-01 13:45:00
```

Trecho de salvamento:

```python
nome_saida = pasta_saida / f"acidentes_{ano}.parquet"
df.to_parquet(nome_saida, engine="pyarrow", index=False)
```

Explicacao:

- `nome_saida` monta o nome do arquivo Parquet.
- `to_parquet(...)` salva no formato Parquet.
- `engine="pyarrow"` usa PyArrow como motor de escrita.
- `index=False` evita salvar o indice do Pandas como coluna extra.

Analogia: CSV e como uma planilha grande e repetitiva. Parquet e como um armario organizado por colunas: se a consulta precisa so de `uf`, `mortos` e `feridos_graves`, ela nao precisa abrir todas as gavetas.

## Comparativo de tamanho CSV versus Parquet

Trecho:

```python
df_tamanhos_conversao = conversion_size_report(arquivos_csv, PARQUET_DIR)
caminho_tamanhos = REPORTS_DIR / "comparativo_tamanho_csv_parquet.csv"
df_tamanhos_conversao.to_csv(caminho_tamanhos, index=False)
```

Explicacao:

- `conversion_size_report(...)` calcula tamanho dos CSVs e Parquets.
- `caminho_tamanhos` define onde o relatorio sera salvo.
- `to_csv(...)` grava o relatorio em `reports/`.

Trecho:

```python
total_csv_mb = df_tamanhos_conversao["csv_mb"].sum()
total_parquet_mb = df_tamanhos_conversao["parquet_mb"].sum()
reducao_total = 0 if total_csv_mb == 0 else (1 - total_parquet_mb / total_csv_mb) * 100
```

Explicacao:

- Soma o tamanho total dos CSVs.
- Soma o tamanho total dos Parquets.
- Calcula a reducao percentual.
- Se `total_csv_mb` for zero, evita divisao por zero.

Exemplo: se CSV tem 100 MB e Parquet tem 5 MB:

```text
reducao = (1 - 5 / 100) * 100 = 95%
```

## Modulo `src/utils/benchmark.py`

### Medicao de tempo

Trecho:

```python
def measure_seconds(function: Callable[[], Any]) -> tuple[Any, float]:
    """Executa uma funcao e retorna seu resultado com a duracao em segundos."""
    start = time.time()
    result = function()
    duration = round(time.time() - start, 4)
    return result, duration
```

Explicacao:

- A funcao recebe outra funcao como parametro.
- `start = time.time()` marca a hora inicial.
- `result = function()` executa a funcao recebida.
- `duration = ...` calcula quanto tempo passou.
- `return result, duration` devolve o resultado e o tempo.

Analogia: e um cronometro. Voce entrega uma tarefa, ele aperta "iniciar", roda a tarefa, aperta "parar" e devolve o resultado junto com o tempo.

### Formatacao de bytes

Trecho:

```python
def format_bytes(size_bytes: int | float) -> str:
    """Formata bytes em uma unidade legivel para relatorios."""
    size = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(size) < 1024 or unit == "TB":
            return f"{size:.2f} {unit}"
        size /= 1024
```

Explicacao:

- Recebe um tamanho em bytes.
- Testa unidades em ordem: bytes, KB, MB, GB, TB.
- Enquanto o numero for maior que 1024, divide por 1024.
- Retorna texto como `119.12 MB`.

### Relatorio de conversao

Trecho:

```python
def conversion_size_report(csv_paths: Iterable[str | Path], parquet_dir: str | Path) -> pd.DataFrame:
    """Compara o tamanho dos CSVs originais com os Parquets gerados por ano."""
    parquet_dir = Path(parquet_dir)
    rows = []

    for csv_path in csv_paths:
        csv_path = Path(csv_path)
        year = "".join(character for character in csv_path.stem if character.isdigit())[:4]
        parquet_path = parquet_dir / f"acidentes_{year}.parquet"
```

Explicacao:

- Recebe lista de CSVs e pasta dos Parquets.
- Cria uma lista `rows` para acumular os resultados.
- Para cada CSV, extrai o ano do nome.
- Monta o caminho do Parquet correspondente.

Trecho:

```python
csv_size = csv_path.stat().st_size if csv_path.exists() else 0
parquet_size = parquet_path.stat().st_size if parquet_path.exists() else 0
reduction_percent = 0 if csv_size == 0 else (1 - parquet_size / csv_size) * 100
```

Explicacao:

- `stat().st_size` pega tamanho do arquivo.
- Se o arquivo nao existir, usa zero.
- Calcula reducao percentual.

## Validacao apos Parquet

Trecho:

```python
df_validacao = pd.read_parquet(PARQUET_DIR)
relatorios_validacao = validate_dataframe_quality(df_validacao, meu_schema)
```

Explicacao:

- `pd.read_parquet(PARQUET_DIR)` le todos os Parquets da pasta.
- `validate_dataframe_quality(...)` cria relatorios de tipos, nulos e invalidos.

Trecho:

```python
for nome_relatorio, relatorio in relatorios_validacao.items():
    caminho_relatorio = REPORTS_DIR / f"validacao_{nome_relatorio}.csv"
    relatorio.to_csv(caminho_relatorio, index=False)
    print(f"Relatorio salvo: {caminho_relatorio.name}")
```

Explicacao:

- Percorre cada relatorio gerado.
- Cria nomes como `validacao_tipos.csv`.
- Salva cada relatorio em `reports/`.

## Parte 2 - Operacoes em grandes volumes

Trecho:

```python
df_completo = pd.read_parquet(PARQUET_DIR)
df_completo["data_inversa"] = pd.to_datetime(df_completo["data_inversa"])
```

Explicacao:

- Le todos os Parquets otimizados.
- Garante que a coluna `data_inversa` esta em formato de data.

Trecho:

```python
if "data_hora" not in df_completo.columns and "horario" in df_completo.columns:
    df_completo["data_hora"] = pd.to_datetime(
        df_completo["data_inversa"].dt.strftime("%Y-%m-%d") + " " + df_completo["horario"].astype(str),
        errors="coerce",
    )
df_completo["data_hora"] = pd.to_datetime(df_completo["data_hora"], errors="coerce")
```

Explicacao:

- Se os Parquets forem antigos e nao tiverem `data_hora`, a coluna e recriada.
- A ultima linha garante que `data_hora` realmente esta como data e hora.

Isso torna o notebook mais robusto. Mesmo se alguem reaproveitar Parquets antigos, ele ainda tenta funcionar.

### Cortes temporais

Trecho:

```python
cortes_tempo = {
    "2.1 - Horas": "2017-01-01 00:59:59",
    "2.2 - Dias": "2017-01-01 23:59:59",
    "2.3 - Semanas": "2017-01-07 23:59:59",
    "2.4 - Meses": "2017-01-31 23:59:59",
    "2.5 - Trimestres": "2017-03-31 23:59:59",
    "2.6 - Semestres": "2017-06-30 23:59:59",
    "2.7 - Anos": "2017-12-31 23:59:59",
    "2.8 - Limite Maximo": "2025-12-31 23:59:59",
}
```

Explicacao:

- O dicionario define os volumes testados.
- Todos comecam em `2017-01-01 00:00:00`.
- Cada chave representa um tamanho de janela.
- O valor e a data final da janela.

Analogia: e como testar uma torneira com copos cada vez maiores: primeiro uma hora, depois um dia, depois uma semana, ate encher o maior recipiente possivel.

### Loop de processamento

Trecho:

```python
for nome_corte, data_final_str in cortes_tempo.items():
    data_final = pd.to_datetime(data_final_str)

    df_filtrado = df_completo[
        (df_completo["data_hora"] >= data_inicial) &
        (df_completo["data_hora"] <= data_final)
    ]
```

Explicacao:

- Percorre cada corte temporal.
- Converte a data final para formato de data.
- Filtra linhas entre a data inicial e a data final.
- O filtro funciona como uma peneira temporal.

Trecho:

```python
consulta, duracao_segundos = measure_seconds(
    lambda: df_filtrado.groupby("uf", observed=True)[["mortos", "feridos_graves"]].sum()
)
```

Explicacao:

- `measure_seconds` mede o tempo da consulta.
- `lambda` cria uma funcao anonima para ser cronometrada.
- `groupby("uf")` agrupa por estado.
- `[["mortos", "feridos_graves"]]` escolhe as colunas numericas.
- `.sum()` soma mortos e feridos graves por UF.

Exemplo simplificado:

```text
UF  mortos
AM  2
AM  3
PA  1

Depois do groupby:
AM  5
PA  1
```

Trecho:

```python
resultados.append({
    "Volume": nome_corte,
    "Linhas": volume_linhas,
    "Tempo_Segundos": duracao_segundos,
})
```

Explicacao:

- Guarda o nome do corte.
- Guarda quantas linhas foram processadas.
- Guarda o tempo medido.
- Depois isso vira tabela e grafico.

## Graficos

### Tema visual

Trecho de `src/utils/plotting.py`:

```python
DARK_THEME_CONFIG = {
    "axes.facecolor": "#1e1e1e",
    "figure.facecolor": "#121212",
    "grid.color": "#333333",
    "axes.edgecolor": "#333333",
    "text.color": "white",
    "axes.labelcolor": "white",
    "xtick.color": "white",
    "ytick.color": "white",
}
```

Explicacao:

- Define cores padronizadas para todos os graficos.
- Fundo escuro, texto branco e grid discreto.
- Isso evita graficos com estilos diferentes entre si.

Trecho:

```python
def apply_dark_theme() -> None:
    """Aplica o estilo visual usado em todos os graficos do trabalho."""
    plt.style.use("dark_background")
    sns.set_theme(style="darkgrid", rc=DARK_THEME_CONFIG)
```

Explicacao:

- Ativa estilo escuro no Matplotlib.
- Configura o tema do Seaborn com o dicionario criado.

Trecho:

```python
def save_report_figure(reports_dir: str | Path, file_name: str, dpi: int = 300) -> Path:
    """Salva a figura atual na pasta de relatorios e retorna o caminho gerado."""
    output_path = Path(reports_dir) / file_name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi)
    return output_path
```

Explicacao:

- Recebe a pasta e o nome do arquivo.
- Garante que a pasta existe.
- `tight_layout()` ajusta margens para nao cortar textos.
- `savefig(...)` salva a imagem.
- `dpi=300` gera boa resolucao.

### Grafico de ranking por UF

Trecho:

```python
ranking_completo = consulta.sort_values(by="mortos", ascending=False).reset_index()
```

Explicacao:

- `consulta` contem o resultado do maior corte temporal.
- `sort_values(...)` ordena por mortos, do maior para o menor.
- `reset_index()` transforma `uf` de indice para coluna comum.

Trecho:

```python
sns.barplot(
    data=ranking_completo,
    x="mortos",
    y="uf",
    hue="uf",
    palette="magma",
    dodge=False,
    legend=False,
)
```

Explicacao:

- Cria grafico de barras.
- Eixo X: total de mortos.
- Eixo Y: UF.
- `palette="magma"` define a paleta de cores.
- `legend=False` remove legenda redundante.

### Grafico de desempenho Pandas

Trecho:

```python
sns.lineplot(
    data=df_resultados,
    x="Volume",
    y="Tempo_Segundos",
    marker="o",
    color="#00ffcc",
    linewidth=2,
    markersize=8,
)
```

Explicacao:

- Cria grafico de linha.
- O eixo X mostra o tamanho do corte temporal.
- O eixo Y mostra o tempo.
- Os marcadores deixam cada ponto visivel.

Analogia: e como acompanhar uma corrida. Cada ponto mostra quanto tempo o Pandas levou quando o percurso ficou maior.

### Heatmap de dia da semana por fase do dia

Trecho:

```python
matriz_dia_fase = df_completo.groupby(["dia_semana", "fase_dia"], observed=True).size().unstack(fill_value=0)
```

Explicacao:

- Agrupa por `dia_semana` e `fase_dia`.
- `.size()` conta registros.
- `.unstack(fill_value=0)` transforma uma das categorias em colunas.

Exemplo conceitual:

```text
segunda-feira | Pleno dia | 100
segunda-feira | Noite     | 80

vira uma matriz:

              Pleno dia  Noite
segunda-feira       100     80
```

Trecho:

```python
sns.heatmap(
    matriz_dia_fase,
    cmap="flare",
    annot=True,
    fmt="d",
    cbar_kws={"label": "Qtd. de Acidentes"},
    linewidths=.5,
    linecolor="#1e1e1e",
)
```

Explicacao:

- `heatmap` cria mapa de calor.
- Cores mais intensas indicam mais acidentes.
- `annot=True` mostra os numeros dentro das celulas.
- `fmt="d"` formata como inteiro.

### Grafico de causas

Trecho:

```python
causas = df_completo.groupby("causa_acidente", observed=True).size().reset_index(name="total_acidentes")
top_10_causas = causas.sort_values(by="total_acidentes", ascending=False).head(10)
```

Explicacao:

- Conta quantos acidentes existem por causa.
- Ordena do maior para o menor.
- Pega as 10 causas mais frequentes.

Trecho:

```python
top_10_causas["causa_acidente"] = top_10_causas["causa_acidente"].apply(lambda x: textwrap.fill(x, width=45))
```

Explicacao:

- Algumas causas sao textos longos.
- `textwrap.fill` quebra o texto em linhas menores.
- Isso evita que o eixo Y fique ilegivel.

## Parte 3 - Benchmark entre bibliotecas

O objetivo do benchmark e comparar quatro formas de fazer a mesma consulta:

1. Pandas.
2. Polars.
3. PyArrow.
4. Dask local.

A consulta e sempre a mesma: filtrar por intervalo de `data_hora` e somar `mortos` e `feridos_graves` por UF.

### Dask local

Trecho:

```python
cluster = LocalCluster(n_workers=4, threads_per_worker=2)
client = Client(cluster)
```

Explicacao:

- Cria um cluster Dask local.
- `n_workers=4`: cria 4 workers na maquina local.
- `threads_per_worker=2`: cada worker usa 2 threads.
- `Client(cluster)` conecta o notebook ao cluster.

Analogia: e como dividir uma tarefa entre 4 mesas dentro da mesma sala.

### Metodo Pandas

Trecho:

```python
def run_pandas():
    df_pd = pd.read_parquet(PARQUET_DIR)
    df_pd["data_inversa"] = pd.to_datetime(df_pd["data_inversa"])
    if "data_hora" not in df_pd.columns:
        df_pd["data_hora"] = pd.to_datetime(
            df_pd["data_inversa"].dt.strftime("%Y-%m-%d") + " " + df_pd["horario"].astype(str),
            errors="coerce",
        )
    df_pd["data_hora"] = pd.to_datetime(df_pd["data_hora"], errors="coerce")
    mask = (df_pd["data_hora"] >= data_inicial_dt) & (df_pd["data_hora"] <= data_final_dt)
    return df_pd[mask].groupby("uf", observed=True)[["mortos", "feridos_graves"]].sum()
```

Explicacao:

- Le os Parquets para memoria.
- Garante as colunas de data.
- Cria uma mascara booleana.
- Aplica filtro com `df_pd[mask]`.
- Agrupa por UF e soma.

Mascara booleana e como uma lista de "sim" e "nao" para cada linha. Se a linha esta dentro do periodo, entra na consulta. Se nao esta, fica fora.

### Metodo Polars

Trecho:

```python
def run_polars():
    df_pl = pl.scan_parquet(str(PARQUET_DIR / "*.parquet"))
    query_polars = (
        df_pl
        .filter((pl.col("data_hora") >= data_inicial_dt) & (pl.col("data_hora") <= data_final_dt))
        .group_by("uf")
        .agg([pl.col("mortos").sum(), pl.col("feridos_graves").sum()])
    )
    return query_polars.collect()
```

Explicacao:

- `scan_parquet` nao carrega tudo imediatamente.
- Ele monta um plano de consulta.
- `.filter(...)` define o filtro.
- `.group_by("uf")` define o agrupamento.
- `.agg(...)` define as somas.
- `.collect()` executa de verdade.

Analogia: Polars primeiro faz o plano da viagem, escolhe a rota mais eficiente, e so depois sai de casa.

### Metodo PyArrow

Trecho:

```python
def run_pyarrow():
    dataset_arrow = ds.dataset(PARQUET_DIR, format="parquet")
    filtro = (pc.field("data_hora") >= data_inicial_dt) & (pc.field("data_hora") <= data_final_dt)
    tabela_filtrada = dataset_arrow.to_table(filter=filtro)
    return tabela_filtrada.group_by("uf").aggregate([("mortos", "sum"), ("feridos_graves", "sum")])
```

Explicacao:

- `ds.dataset(...)` trata a pasta de Parquets como um dataset unico.
- `pc.field("data_hora")` aponta para a coluna no formato Arrow.
- `to_table(filter=filtro)` le apenas o que passa no filtro.
- `group_by("uf").aggregate(...)` agrupa e soma.

PyArrow e bem proximo do formato Parquet, por isso costuma ser muito eficiente em leitura colunar.

### Metodo Dask local

Trecho:

```python
def run_dask():
    df_dd = dd.read_parquet(str(PARQUET_DIR / "*.parquet"))
    if "data_hora" not in df_dd.columns:
        df_dd["data_hora"] = dd.to_datetime(
            df_dd["data_inversa"].astype(str) + " " + df_dd["horario"].astype(str),
            errors="coerce",
        )
    mask_dd = (df_dd["data_hora"] >= data_inicial_str) & (df_dd["data_hora"] <= data_final_str)
    return df_dd[mask_dd].groupby("uf", observed=True)[["mortos", "feridos_graves"]].sum().compute()
```

Explicacao:

- `dd.read_parquet` cria um DataFrame Dask.
- Dask trabalha por particoes.
- A mascara filtra por data.
- O agrupamento e definido.
- `.compute()` executa a tarefa.

Sem `.compute()`, Dask apenas monta o plano. Com `.compute()`, ele manda executar.

### Registro dos tempos

Trecho:

```python
resultados_gerais.append({"Volume": nome_corte, "Biblioteca": "Pandas", "Tempo (s)": t_pandas})
resultados_gerais.append({"Volume": nome_corte, "Biblioteca": "Polars", "Tempo (s)": t_polars})
resultados_gerais.append({"Volume": nome_corte, "Biblioteca": "PyArrow", "Tempo (s)": t_arrow})
resultados_gerais.append({"Volume": nome_corte, "Biblioteca": "Dask", "Tempo (s)": t_dask})
```

Explicacao:

- Cada biblioteca gera uma linha no relatorio.
- Para cada volume temporal, sao adicionadas 4 linhas.
- Depois isso vira tabela e grafico comparativo.

## Parte 4 - Dask distribuido

Na Parte 3, o Dask roda localmente. Na Parte 4, o Dask conecta a um cluster externo.

Analogia: Dask local e como dividir tarefas entre mesas da mesma sala. Dask distribuido e como dividir tarefas entre salas diferentes, possivelmente em maquinas diferentes.

### Configuracao do cenario

Trecho:

```python
ENDERECO_SCHEDULER = "tcp://10.100.39.211:8786"
CENARIO_WORKERS_ESPERADO = 1

DATA_INICIAL = "2017-01-01 00:00:00"
DATA_FINAL = "2025-12-31 23:59:59"

ARQUIVO_ESCALABILIDADE = REPORTS_DIR / "relatorio_escalabilidade_dask_cluster.csv"
```

Explicacao:

- `ENDERECO_SCHEDULER`: endereco do scheduler Dask.
- `CENARIO_WORKERS_ESPERADO`: quantidade de workers esperada naquele teste.
- `DATA_INICIAL` e `DATA_FINAL`: periodo completo analisado.
- `ARQUIVO_ESCALABILIDADE`: CSV que acumula os resultados dos testes.

Nos cenarios seguintes, a logica e igual. O que muda e:

```python
CENARIO_WORKERS_ESPERADO = 2
```

ou:

```python
CENARIO_WORKERS_ESPERADO = 3
```

### Diagnostico dos workers

Trecho:

```python
def diagnosticar_worker(parquet_dir: str) -> dict:
    import os
    import socket
    from pathlib import Path

    caminho = Path(parquet_dir)
    arquivos = list(caminho.glob("*.parquet")) if caminho.exists() else []

    return {
        "host": socket.gethostname(),
        "pid": os.getpid(),
        "cwd": os.getcwd(),
        "parquet_dir": str(caminho),
        "parquet_dir_existe": caminho.exists(),
        "qtd_parquets": len(arquivos),
    }
```

Explicacao:

- Essa funcao roda dentro de cada worker.
- `socket.gethostname()` identifica a maquina.
- `os.getpid()` mostra o processo.
- `os.getcwd()` mostra a pasta atual.
- `Path(parquet_dir)` transforma o caminho em objeto Path.
- `glob("*.parquet")` lista Parquets encontrados.
- O retorno e um dicionario com o diagnostico.

Analogia: antes de mandar cada trabalhador executar a tarefa, o codigo pergunta: "voce esta online? voce sabe onde estao os arquivos? quantos arquivos consegue ver?"

### Conexao ao cluster

Trecho:

```python
client = Client(ENDERECO_SCHEDULER)

try:
    client.wait_for_workers(CENARIO_WORKERS_ESPERADO, timeout=60)
```

Explicacao:

- `Client(...)` conecta ao scheduler.
- `wait_for_workers(...)` espera a quantidade correta de workers.
- `timeout=60` define limite de espera de 60 segundos.
- O `try` garante que o `finally` feche a conexao depois.

### Leitura das informacoes do cluster

Trecho:

```python
info_cluster = client.scheduler_info()
workers = info_cluster.get("workers", {})

workers_ativos = len(workers)
threads_ativas = sum(w.get("nthreads", 0) for w in workers.values())
memoria_total_gb = sum(w.get("memory_limit", 0) for w in workers.values()) / (1024 ** 3)
```

Explicacao:

- `scheduler_info()` pega informacoes do cluster.
- `workers` pega o bloco de workers.
- `len(workers)` conta workers ativos.
- `threads_ativas` soma threads de todos os workers.
- `memoria_total_gb` soma memoria e converte bytes para GB.

### Verificacao do cenario correto

Trecho:

```python
if workers_ativos != CENARIO_WORKERS_ESPERADO:
    raise RuntimeError(
        f"O cenario esperado era {CENARIO_WORKERS_ESPERADO} worker(s), "
        f"mas o cluster possui {workers_ativos} worker(s) ativo(s)."
    )
```

Explicacao:

- Compara workers ativos com o esperado.
- Se nao bater, interrompe o teste.
- Isso evita medir o cenario errado.

Exemplo: se o teste e de 3 workers, mas so 2 estao conectados, o resultado nao serviria para comparacao. Por isso o codigo para.

### Execucao do diagnostico

Trecho:

```python
diagnosticos = client.run(diagnosticar_worker, str(PARQUET_DIR))
```

Explicacao:

- `client.run(...)` manda uma funcao rodar em todos os workers.
- Cada worker executa `diagnosticar_worker`.
- O resultado volta para o notebook.

Trecho:

```python
df_diagnostico = (
    pd.DataFrame.from_dict(diagnosticos, orient="index")
    .reset_index()
    .rename(columns={"index": "worker_address"})
)
```

Explicacao:

- Converte o dicionario de diagnosticos em DataFrame.
- `orient="index"` indica que cada chave vira uma linha.
- `reset_index()` transforma o endereco do worker em coluna.
- `rename(...)` chama essa coluna de `worker_address`.

### Validacao dos arquivos nos workers

Trecho:

```python
if not df_diagnostico["parquet_dir_existe"].all():
    raise FileNotFoundError(
        "Pelo menos um worker nao encontrou a pasta dos Parquets."
    )

if (df_diagnostico["qtd_parquets"] == 0).any():
    raise FileNotFoundError(
        "Pelo menos um worker encontrou a pasta, mas nao encontrou arquivos .parquet."
    )
```

Explicacao:

- A primeira condicao verifica se todos os workers encontraram a pasta.
- `.all()` exige que todos sejam `True`.
- A segunda condicao verifica se algum worker viu zero Parquets.
- `.any()` acusa se algum caso problemático existir.

Analogia: nao adianta ter tres pessoas trabalhando se uma delas nao recebeu o material.

### Medicao da consulta distribuida

Trecho:

```python
t0 = time.perf_counter()

df_dask = dd.read_parquet(str(PARQUET_DIR / "*.parquet"), engine="pyarrow")
```

Explicacao:

- `perf_counter()` marca inicio da medicao.
- `dd.read_parquet(...)` cria um DataFrame Dask com os Parquets.
- O Dask divide os arquivos em tarefas para o cluster.

Trecho:

```python
df_filtrado = df_dask[
    (df_dask["data_hora"] >= data_inicial)
    & (df_dask["data_hora"] <= data_final)
]
```

Explicacao:

- Aplica filtro temporal.
- Mantem apenas linhas dentro do periodo completo.

Trecho:

```python
consulta_uf = (
    df_filtrado
    .groupby("uf", observed=True)[["mortos", "feridos_graves"]]
    .sum()
)
```

Explicacao:

- Agrupa por UF.
- Seleciona mortos e feridos graves.
- Soma os valores.

Trecho:

```python
total_linhas = df_filtrado.shape[0]
resultado_dask, linhas_processadas = compute(consulta_uf, total_linhas)
```

Explicacao:

- `shape[0]` representa a quantidade de linhas.
- `compute(...)` executa a agregacao e a contagem.
- O resultado volta em duas variaveis.

### Registro do tempo e resultado

Trecho:

```python
tempo_total = round(time.perf_counter() - t0, 4)
resultado_dask = resultado_dask.sort_index()
```

Explicacao:

- Calcula tempo total.
- Arredonda para 4 casas decimais.
- Ordena o resultado por UF.

Trecho:

```python
arquivo_resultado_uf = REPORTS_DIR / f"resultado_dask_cluster_{CENARIO_WORKERS_ESPERADO}_workers.csv"
resultado_dask.to_csv(arquivo_resultado_uf)
```

Explicacao:

- Cria um arquivo diferente para cada cenario.
- Exemplo: `resultado_dask_cluster_2_workers.csv`.
- Salva a tabela por UF.

Trecho:

```python
registro = pd.DataFrame([{
    "Data_Teste": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
    "Cenario_Workers_Esperado": CENARIO_WORKERS_ESPERADO,
    "Workers_Ativos": workers_ativos,
    "Threads_Ativas": threads_ativas,
    "Memoria_Total_GB": round(memoria_total_gb, 2),
    "Hosts": ", ".join(hosts),
    "Linhas_Processadas": int(linhas_processadas),
    "Tempo_Segundos": tempo_total,
    "Scheduler": ENDERECO_SCHEDULER,
}])
```

Explicacao:

- Cria uma linha de relatorio do teste.
- Guarda data do teste.
- Guarda cenario esperado.
- Guarda workers, threads e memoria.
- Guarda hosts.
- Guarda linhas processadas.
- Guarda tempo total.
- Guarda scheduler usado.

### Relatorio acumulativo

Trecho:

```python
if ARQUIVO_ESCALABILIDADE.exists():
    registro.to_csv(ARQUIVO_ESCALABILIDADE, mode="a", header=False, index=False)
else:
    registro.to_csv(ARQUIVO_ESCALABILIDADE, index=False)
```

Explicacao:

- Se o relatorio ja existe, adiciona uma nova linha.
- `mode="a"` significa append, ou seja, acrescentar.
- `header=False` evita repetir o cabecalho.
- Se nao existe, cria o arquivo com cabecalho.

Analogia: cada teste vira uma nova anotacao no caderno de laboratorio.

### Fechamento da conexao

Trecho:

```python
finally:
    client.close()
```

Explicacao:

- O `finally` roda mesmo se der erro.
- `client.close()` fecha a conexao do notebook com o scheduler.
- Isso nao desliga necessariamente o cluster externo; apenas encerra a sessao do notebook.

## Comparacao dos cenarios Dask

Trecho:

```python
df_escalabilidade = pd.read_csv(arquivo_escalabilidade)
```

Explicacao:

- Le o CSV com todos os testes acumulados.

Trecho:

```python
df_plot = (
    df_escalabilidade
    .drop_duplicates(subset=["Cenario_Workers_Esperado"], keep="last")
    .sort_values("Cenario_Workers_Esperado")
)
```

Explicacao:

- `drop_duplicates(...)` pega apenas um registro por cenario.
- `keep="last"` escolhe o ultimo teste valido de cada cenario.
- `sort_values(...)` ordena 1, 2 e 3 workers.

Trecho:

```python
sns.lineplot(
    data=df_plot,
    x="Cenario_Workers_Esperado",
    y="Tempo_Segundos",
    marker="o",
    linewidth=2.5,
    markersize=8,
)
```

Explicacao:

- Cria uma linha mostrando workers versus tempo.
- O objetivo e visualizar se mais workers reduziram o tempo.

## Como as partes se conectam

Fluxo completo:

```text
CSV bruto
  -> schema e validacao de colunas
  -> leitura tipada com Pandas
  -> criacao de data_hora
  -> salvamento em Parquet
  -> validacao de qualidade
  -> consultas e graficos
  -> benchmark local
  -> benchmark distribuido com Dask
  -> relatorios em reports/
```

Cada etapa depende da anterior:

- Sem CSV, nao existe materia-prima.
- Sem schema, os tipos podem ficar inconsistentes.
- Sem `data_hora`, nao existe granularidade por hora.
- Sem Parquet, as consultas ficam mais pesadas.
- Sem relatorios, a entrega fica menos auditavel.
- Sem Dask distribuido, nao ha demonstracao de escalabilidade horizontal.

## Resumo dos principais conceitos

| Conceito | O que significa no projeto |
|---|---|
| Schema | Contrato de tipos e colunas esperadas |
| Validacao | Conferencia de colunas, tipos, nulos e invalidos |
| Parquet | Formato colunar compacto e eficiente |
| `data_hora` | Coluna derivada para analise temporal fina |
| Groupby | Agrupamento, como somar mortos por UF |
| Benchmark | Comparacao de tempo entre bibliotecas |
| Dask local | Paralelismo dentro da mesma maquina |
| Dask distribuido | Paralelismo em cluster com scheduler e workers |
| Worker | Processo que executa tarefas do Dask |
| Scheduler | Coordenador que distribui tarefas para os workers |

## Leitura final

O codigo foi organizado para mostrar uma evolucao natural:

1. Primeiro, garantir que os dados estao corretos.
2. Depois, transformar os dados para um formato melhor.
3. Em seguida, analisar volumes crescentes.
4. Depois, comparar ferramentas.
5. Por fim, distribuir o processamento.

Essa ordem e importante porque processamento rapido sobre dado mal validado pode gerar conclusoes ruins. O projeto tenta primeiro criar uma base confiavel e depois medir desempenho sobre essa base.
