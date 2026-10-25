# Análise de Acidentes da PRF | Python e Power BI

**Autores do projeto de Programação para Análise de Dados:** Chrysthyan Matheus e Eric Gabriel.

Projeto acadêmico de análise de acidentes em rodovias federais brasileiras com dados da Polícia Rodoviária Federal (PRF). O repositório reúne um fluxo de **preparação, validação, processamento e análise de dados em Python**, além de um **relatório interativo em Power BI** para exploração visual dos indicadores de acidentes, vítimas e fatores associados.

## Visão geral

| Componente | Finalidade | Tecnologias principais |
| --- | --- | --- |
| Preparação e validação | Aplicar schemas, verificar colunas, tipos, nulos e valores inválidos | Python, Pandas, PyArrow |
| Armazenamento e análise | Converter CSV em Parquet, analisar volumes e intervalos temporais | Parquet, Pandas, Polars, PyArrow |
| Benchmark | Comparar o desempenho das bibliotecas em processamento local | Pandas, Polars, PyArrow, Dask LocalCluster |
| Dashboard | Explorar indicadores geográficos, temporais e de gravidade | Microsoft Power BI |

O processamento **distribuído em múltiplas máquinas físicas não faz parte da entrega** documentada atualmente. A análise de desempenho com Dask utiliza `LocalCluster`, em execução local.

## Dashboard Power BI

**Download do PBIX:** [analise_acidentes_prf.pbix](https://github.com/matheuschrys/PAD_analise_acidentesPRF/releases/download/powerbi-dashboard-2026-10-25/analise_acidentes_prf.pbix) (125,9 MB, disponível nos ativos da release).

O relatório disponibiliza **15 páginas**, organizadas em análises de:

- **Indicadores gerais:** acidentes, mortos, feridos, envolvidos e índice de letalidade.
- **Geografia e rodovias:** locais com acidentes fatais, letalidade por UF, trechos e densidade de acidentes por rodovia.
- **Tempo e evolução:** séries mensais, distribuição por fase do dia e dia da semana, variação anual de acidentes fatais e recortes trimestrais.
- **Causas e infraestrutura:** causas, tipos de acidente, características da pista e gravidade associada.
- **Veículos e pessoas envolvidas:** tipo e marca de veículo, faixa etária, sexo, perfil dos envolvidos e severidade.

São utilizados gráficos, mapas, tabelas, matrizes, indicadores e filtros interativos conforme a página. Os dados e as medidas já incorporados ao arquivo podem ser explorados ao abri-lo no **Power BI Desktop**.

> **Importante:** o arquivo `.pbix` está anexado à [release do dashboard](https://github.com/matheuschrys/PAD_analise_acidentesPRF/releases/tag/powerbi-dashboard-2026-10-25), separado do código-fonte; ele não vem ao clonar o repositório. A visualização do dashboard não é executada diretamente na página do GitHub. A atualização dos dados pode exigir ajustes nos caminhos e nas credenciais da fonte no Power BI Desktop.

Veja [a documentação do dashboard](powerbi/README.md) para conhecer as páginas e abrir o relatório.

## Escopo da análise em Python

- Definição e aplicação de schemas em arquivos CSV.
- Validação de colunas, tipos, campos nulos e valores inválidos.
- Conversão de CSV para Parquet.
- Processamento incremental por janelas temporais, com análise por horas.
- Consultas, agregações e geração de gráficos.
- Comparação de desempenho entre Pandas, PyArrow, Polars e Dask local.

## Estrutura do repositório

```text
PAD_analise_acidentesPRF/
├── data/
│   ├── raw/                       # CSVs de origem e checksums
│   ├── interim/                   # Dados intermediários
│   └── processed/                 # Dados derivados, como Parquet
├── notebooks/
│   └── acidentes_prf_trabalho_part1.ipynb
├── powerbi/
│   └── README.md                  # Descrição e guia do dashboard
├── reports/                       # Relatórios técnicos e verificações
├── src/                           # Código de ETL e utilitários
├── tests/                         # Testes do projeto
├── .gitignore
├── INSTRUCOES_DE_PUBLICACAO.md
├── README.md
├── README_CODIGO.md
└── requirements.txt
```

## Como executar o projeto em Python

1. Clone o repositório e abra sua pasta como raiz do projeto.
2. Instale as dependências com `pip install -r requirements.txt` em um ambiente Python compatível.
3. Disponibilize os CSVs originais em `data/raw/`.
4. Abra `notebooks/acidentes_prf_trabalho_part1.ipynb`.
5. Execute as células na ordem indicada pelo notebook.

O notebook aceita execução a partir da raiz do repositório ou da pasta `notebooks/` e utiliza os seguintes diretórios:

- `data/raw/`: entrada dos arquivos CSV.
- `data/processed/dados_otimizados/`: saída de arquivos Parquet.
- `reports/`: saída de gráficos, verificações e resultados.

Os CSVs originais são tratados como imutáveis. Por seu tamanho, **não são versionados no Git**; `data/raw/CHECKSUMS.sha256` documenta seus hashes SHA-256. Os Parquets gerados também não são versionados, pois podem ser recriados pelo notebook.

Durante a execução, a coluna `data_hora` é construída a partir de `data_inversa` e `horario`, permitindo análises na granularidade de horas.

## Saídas e documentação técnica

Os resultados do notebook podem incluir, em `reports/`:

- `validacao_colunas_ausentes.csv`, `validacao_tipos.csv`, `validacao_nulos.csv` e `validacao_invalidos.csv`.
- `comparativo_tamanho_csv_parquet.csv`, com os tamanhos e a redução percentual.
- `resumo_benchmark_bibliotecas.csv` e `vencedores_benchmark_por_volume.csv`, comparando Pandas, Polars, PyArrow e Dask local.
- `ANALISE_CAUSAS_ACIDENTES_PRF.md` e `ACIDENTES_EMBRIAGUEZ_PRF.md`, com orientações e verificações das análises respectivas.
- `FILTROS_SEMESTRE_TRIMESTRE_PRF.md`, com filtros por trimestre e semestre.
- `resumo_trimestral.csv` e `resumo_semestral.csv`, quando gerados pelo notebook.

O notebook `notebooks/acidentes_prf_trabalho_part1.ipynb` é a referência principal para a entrega de Programação para Análise de Dados. Veja também [`README_CODIGO.md`](README_CODIGO.md) e, quando disponível, `reports/HISTORICO_REFATORACAO.md`.

## Origem dos dados e observações

A análise tem como tema os dados de acidentes da **Polícia Rodoviária Federal (PRF)**. O portal oficial disponibiliza os conjuntos de dados e sua documentação: [Dados abertos da PRF](https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf).

Os dados embutidos no `.pbix` são independentes da execução do notebook no momento da abertura do relatório. **Não se deve presumir** que a base, o intervalo de datas ou o fluxo de transformação do dashboard sejam idênticos aos do notebook sem conferir as respectivas fontes no Power BI Desktop.

## Ferramentas

**Python · Jupyter Notebook · Pandas · PyArrow · Polars · Dask · Parquet · Microsoft Power BI**