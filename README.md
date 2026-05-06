# PAD - Analise de Acidentes PRF

**Autores:** Chrysthyan Matheus e Eric Gabriel

Projeto desenvolvido para a disciplina de Programacao para Analise de Dados. O trabalho analisa dados de acidentes em rodovias federais, com foco em definicao de schemas, preparacao em formato Parquet, consultas em grandes volumes, geracao de graficos e comparacao de desempenho entre bibliotecas Python.

## Escopo

O projeto cobre:

- Definicao e aplicacao de schema sobre arquivos CSV.
- Validacao formal de colunas, tipos, nulos e valores invalidos.
- Conversao dos dados brutos para Parquet.
- Processamento incremental por janelas temporais, incluindo horas.
- Consultas com agrupamentos e graficos.
- Comparacao de desempenho com Pandas, PyArrow, Polars e Dask local.

O processamento paralelo distribuido com Dask em 1, 2 e 3 maquinas fisicas foi desconsiderado por limitacao externa informada.

## Estrutura

```text
pad_acidentes_prf/
├── data/
│   ├── raw/          # CSVs originais e checksums
│   ├── interim/      # espaco para dados intermediarios documentados
│   └── processed/    # dados finais gerados pelo notebook, como Parquet
├── notebooks/
│   └── acidentes_prf_trabalho_part1.ipynb
├── reports/
│   ├── RELATORIO_VERIFICACAO.md
│   ├── HISTORICO_REFATORACAO.md
│   └── requisitos_trabalho.pdf
├── src/
│   ├── etl/
│   └── utils/
├── tests/
├── README.md
└── requirements.txt
```

## Como executar

1. Abra a pasta `pad_acidentes_prf/` como raiz do projeto.
2. Instale as dependencias listadas em `requirements.txt`.
3. Abra o notebook `notebooks/acidentes_prf_trabalho_part1.ipynb`.
4. Execute as celulas em ordem.

O notebook detecta se esta sendo executado a partir da raiz do projeto ou da pasta `notebooks/` e ajusta os caminhos para:

- `data/raw/`: entrada dos CSVs.
- `data/processed/dados_otimizados/`: saida dos Parquets.
- `reports/`: saida dos graficos e relatorios de validacao.

## Dados

Os CSVs originais devem ficar em `data/raw/` e devem ser tratados como imutaveis. Por serem arquivos grandes, eles nao sao versionados no Git; o arquivo `data/raw/CHECKSUMS.sha256` registra os checksums SHA-256 para verificar integridade dos dados quando forem copiados ou baixados novamente.

Os Parquets em `data/processed/dados_otimizados/` tambem nao sao versionados, pois sao derivados dos CSVs e podem ser recriados executando o notebook.

Durante a execucao, o notebook cria a coluna `data_hora` a partir de `data_inversa` e `horario`, permitindo analises com granularidade por horas.

## Validacao

O notebook gera relatorios de validacao em `reports/`:

- `validacao_colunas_ausentes.csv`
- `validacao_tipos.csv`
- `validacao_nulos.csv`
- `validacao_invalidos.csv`
- `comparativo_tamanho_csv_parquet.csv`, com o tamanho original dos CSVs, o tamanho dos Parquets gerados e a reducao percentual.
- `resumo_benchmark_bibliotecas.csv` e `vencedores_benchmark_por_volume.csv`, com o resumo dos tempos entre Pandas, Polars, PyArrow e Dask local.

## Notebook principal

Use `notebooks/acidentes_prf_trabalho_part1.ipynb` para a entrega/apresentacao oficial.

O historico da reorganizacao do projeto foi preservado em `reports/HISTORICO_REFATORACAO.md`.

## Observacao sobre Dask

A comparacao de desempenho com Dask foi mantida porque o notebook executa benchmark local com `LocalCluster`. Apenas o processamento paralelo distribuido em multiplas maquinas fisicas foi desconsiderado.
