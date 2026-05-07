# PAD - Analise de Acidentes PRF

**Autores:** Chrysthyan Matheus e Eric Gabriel

Projeto desenvolvido para a disciplina de Programacao para Analise de Dados. O trabalho analisa dados de acidentes em rodovias federais brasileiras usando schemas, validacao, conversao para Parquet, consultas em grandes volumes, comparacao de bibliotecas Python e processamento paralelo distribuido com Dask.

O notebook oficial da entrega esta em:

`notebooks/acidentes_prf_trabalho_part1.ipynb`

Para uma explicacao detalhada do codigo, com trechos comentados e analogias, consulte:

`README_CODIGO.md`

## Fonte dos dados

A base usada vem dos Dados Abertos da Policia Rodoviaria Federal (PRF), base BAT - Boletim de Acidente de Transito. Foram usados os documentos CSV de Acidentes de 2017 a 2025, agrupados por pessoa, com todas as causas e tipos de acidentes.

Fonte oficial:

https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf

Os CSVs brutos ficam em `data/raw/` e sao tratados como imutaveis. Por serem arquivos grandes, eles nao sao versionados no Git. O arquivo `data/raw/CHECKSUMS.sha256` registra os checksums SHA-256 para conferir a integridade dos dados quando eles forem copiados ou baixados novamente.

## Dados utilizados

Resumo da base local usada no notebook:

| Item | Valor |
|---|---:|
| Periodo analisado | 2017 a 2025 |
| Arquivos CSV brutos | 9 |
| Tamanho total dos CSVs | aproximadamente 1.48 GB |
| Arquivos Parquet gerados | 9 |
| Tamanho total dos Parquets | aproximadamente 30.5 MB |
| Reducao aproximada CSV -> Parquet | 97.94% |
| Maior volume processado no notebook | 4.069.971 linhas |

Durante a preparacao, o notebook cria a coluna `data_hora` combinando `data_inversa` e `horario`, permitindo analises por hora, dia, semana, mes, trimestre, semestre, ano e limite maximo do dataset.

## Escopo do projeto

O trabalho cobre:

- Definicao e aplicacao de schema sobre os CSVs da PRF.
- Validacao formal de colunas, tipos, nulos e valores invalidos.
- Conversao dos CSVs brutos para Parquet.
- Processamento incremental por janelas temporais.
- Consultas com agrupamento por UF, fase do dia, dia da semana e causa de acidente.
- Geracao de graficos para analise e apresentacao.
- Benchmark com Pandas, Polars, PyArrow e Dask local.
- Processamento paralelo distribuido com Dask Cluster, variando 1, 2 e 3 workers.

## Estrutura

```text
pad_acidentes_prf/
├── data/
│   ├── raw/          # CSVs originais e checksums
│   ├── interim/      # espaco para dados intermediarios documentados
│   └── processed/    # Parquets gerados pelo notebook
├── notebooks/
│   └── acidentes_prf_trabalho_part1.ipynb
├── reports/          # graficos, relatorios CSV e PDF de requisitos
├── src/
│   ├── etl/          # schema e validacoes
│   └── utils/        # benchmark e utilitarios de graficos
├── tests/
├── README.md
└── requirements.txt
```

## Como executar

1. Abra a pasta `pad_acidentes_prf/` como raiz do projeto.
2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

3. Garanta que os CSVs originais estejam em `data/raw/`.
4. Abra `notebooks/acidentes_prf_trabalho_part1.ipynb`.
5. Execute as celulas em ordem.

O notebook detecta se esta sendo executado a partir da raiz do projeto ou da pasta `notebooks/` e ajusta automaticamente os caminhos para:

- `data/raw/`: entrada dos CSVs.
- `data/processed/dados_otimizados/`: saida dos Parquets.
- `reports/`: saida dos graficos e relatorios.

## Validacao dos dados

O notebook gera relatorios de validacao em `reports/`:

- `validacao_colunas_ausentes.csv`
- `validacao_tipos.csv`
- `validacao_nulos.csv`
- `validacao_invalidos.csv`
- `comparativo_tamanho_csv_parquet.csv`, com o tamanho original dos CSVs, o tamanho dos Parquets gerados e a reducao percentual.
- `resumo_benchmark_bibliotecas.csv` e `vencedores_benchmark_por_volume.csv`, com o resumo dos tempos entre Pandas, Polars, PyArrow e Dask local.

Resultados registrados:

- Todos os arquivos de 2017 a 2025 possuem as 17 colunas esperadas.
- Todos os tipos definidos no schema foram aplicados com status `ok`.
- Nao foram encontrados valores invalidos nas regras testadas para vitimas, datas e horarios.
- As colunas de vitimas possuem aproximadamente 9.51% de nulos, ponto documentado no relatorio de nulos.

## Resultados e insights

Alguns resultados observados no processamento:

- A conversao para Parquet reduziu fortemente o volume em disco, de cerca de 1.48 GB em CSV para cerca de 30.5 MB em Parquet.
- Minas Gerais foi a UF com maior total de mortos no agregado distribuido, seguida por Parana, Bahia, Santa Catarina e Goias.
- Minas Gerais tambem concentrou o maior total de feridos graves, seguida por Parana, Santa Catarina, Rio Grande do Sul e Bahia.
- No agregado por UF gerado pelo Dask distribuido, os totais foram 180.874 mortos e 454.126 feridos graves no periodo analisado.
- A analise por fase do dia e dia da semana ajuda a observar concentracoes temporais de acidentes, enquanto o ranking de causas facilita a leitura dos fatores mais recorrentes.

Top 5 UFs por mortos no resultado distribuido:

| UF | Mortos |
|---|---:|
| MG | 24.137 |
| PR | 18.431 |
| BA | 14.850 |
| SC | 11.504 |
| GO | 10.627 |

Top 5 UFs por feridos graves:

| UF | Feridos graves |
|---|---:|
| MG | 63.192 |
| PR | 48.383 |
| SC | 39.396 |
| RS | 27.260 |
| BA | 27.056 |

## Benchmark entre bibliotecas

A comparacao de desempenho executou a mesma tarefa nas quatro bibliotecas: leitura dos Parquets, filtro temporal e agregacao por UF.

Resumo dos tempos medios registrados:

| Biblioteca | Tempo medio |
|---|---:|
| PyArrow | 0.0646 s |
| Polars | 0.0727 s |
| Dask local | 0.4129 s |
| Pandas | 0.7375 s |

Principais aprendizados do benchmark:

- PyArrow e Polars se beneficiaram bastante do formato colunar Parquet.
- Polars teve o melhor tempo no limite maximo do dataset registrado no benchmark.
- Pandas foi mais simples de usar, mas carregou mais trabalho em memoria e ficou mais lento neste tipo de consulta.
- Dask local teve overhead maior nos cortes pequenos, mas continua importante para comparar o modelo de execucao paralela.

## Dask distribuido

A Parte 4 do notebook executa processamento paralelo distribuido em cluster Dask externo. O scheduler usado nos testes foi:

`tcp://10.100.39.211:8786`

Antes de processar, cada cenario valida:

- quantidade esperada de workers ativos;
- numero de threads informadas pelo cluster;
- memoria total disponivel;
- acesso dos workers a pasta `dados_otimizados`;
- quantidade de arquivos Parquet visiveis por worker.

Ultimos tempos registrados por cenario:

| Workers | Threads | Memoria total | Tempo |
|---:|---:|---:|---:|
| 1 | 2 | 7.75 GB | 3.0141 s |
| 2 | 4 | 15.51 GB | 1.5147 s |
| 3 | 6 | 23.26 GB | 1.4024 s |

Com 2 workers, o tempo caiu cerca de 49.7% em relacao ao cenario com 1 worker. Com 3 workers, a queda foi de cerca de 53.5%. O ganho entre 2 e 3 workers foi menor, indicando que existe overhead de coordenacao e que a consulta ja estava ficando limitada por outros fatores alem da quantidade de workers.

## Arquivos de saida

Principais artefatos gerados em `reports/`:

- `grafico_consulta_estados.png`
- `grafico_desempenho_pandas.png`
- `grafico_consulta_heatmap.png`
- `grafico_consulta_causas.png`
- `grafico_benchmark_completo.png`
- `grafico_escalabilidade_dask_cluster.png`
- `comparativo_tamanho_csv_parquet.csv`
- `resumo_benchmark_bibliotecas.csv`
- `vencedores_benchmark_por_volume.csv`
- `relatorio_escalabilidade_dask_cluster.csv`
- `resultado_dask_cluster_1_workers.csv`
- `resultado_dask_cluster_2_workers.csv`
- `resultado_dask_cluster_3_workers.csv`

## O que foi aprendido

O trabalho mostrou na pratica que a escolha do formato de armazenamento e tao importante quanto a biblioteca usada para processar os dados. A conversao para Parquet reduziu drasticamente o tamanho em disco e favoreceu consultas colunares.

Tambem ficou claro que bibliotecas diferentes resolvem o mesmo problema com perfis diferentes: Pandas e direto e conhecido, PyArrow e Polars aproveitam muito bem leitura colunar e lazy evaluation, e Dask se torna mais interessante quando o processamento precisa ser distribuido.

Na parte distribuida, o principal aprendizado foi que aumentar workers melhora o tempo ate certo ponto, mas nao elimina custos de comunicacao, agendamento e leitura. Por isso, validar o cluster e registrar os cenarios de forma controlada foi essencial para comparar os resultados.
