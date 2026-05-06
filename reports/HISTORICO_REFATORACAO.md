# Historico da Refatoracao

**Autores:** Chrysthyan Matheus e Eric Gabriel

## Objetivo

Registrar a reorganizacao realizada antes da versao oficial do projeto, documentando as melhorias aplicadas sem tratar a entrega atual como uma versao provisoria.

## O que foi feito

- Criada a pasta `pad_acidentes_prf/` como nova raiz organizada do projeto.
- Criada a estrutura `data/raw`, `data/interim`, `data/processed`, `notebooks`, `src`, `reports` e `tests`.
- Copiados os CSVs originais para `data/raw/`.
- Gerado o arquivo `data/raw/CHECKSUMS.sha256` para controle de integridade dos dados brutos.
- Consolidado o notebook principal em `notebooks/acidentes_prf_trabalho_part1.ipynb`.
- Copiado o relatorio de verificacao para `reports/RELATORIO_VERIFICACAO.md`.
- Copiado o PDF de requisitos para `reports/requisitos_trabalho.pdf`.
- Criado `requirements.txt` com as bibliotecas usadas no trabalho.
- Adicionadas documentacoes curtas em cada pasta principal.

## Ajustes incorporados ao notebook oficial

O notebook oficial manteve o fluxo analitico do trabalho:

1. Leitura dos CSVs.
2. Definicao e aplicacao de schema.
3. Conversao para Parquet.
4. Processamento incremental por volume temporal.
5. Geracao de graficos.
6. Benchmark com Pandas, Polars, PyArrow e Dask local.

Os principais ajustes foram:

- Inclusao de uma introducao com autores e escopo.
- Inclusao de textos explicativos antes das secoes principais.
- Troca do caminho absoluto dos CSVs por caminhos relativos ao projeto.
- Implementacao da granularidade por horas com a coluna `horario` e o campo derivado `data_hora`.
- Inclusao de validacao formal de schema, com relatorios de colunas ausentes, tipos, nulos e valores invalidos.
- Extracao de funcoes auxiliares para `src/`, reduzindo repeticoes no notebook.
- Direcionamento dos Parquets para `data/processed/dados_otimizados/`.
- Direcionamento dos graficos para `reports/`.
- Inclusao de referencias e observacao sobre o uso de Dask.

## Funcoes extraidas para `src/`

O projeto passou a usar pequenos modulos auxiliares:

- `src/etl/schema.py`: centraliza o schema esperado, colunas de data/hora e validacoes de qualidade dos dados.
- `src/utils/benchmark.py`: centraliza a medicao de tempo usada nos benchmarks.
- `src/utils/plotting.py`: centraliza o tema escuro e o salvamento dos graficos em `reports/`.

Essa organizacao mantem o notebook como arquivo principal da entrega, mas evita repeticao de trechos e deixa mais claro onde cada responsabilidade esta localizada.

## Validacao formal

Foram adicionados relatorios gerados automaticamente na pasta `reports/`:

- `validacao_colunas_ausentes.csv`
- `validacao_tipos.csv`
- `validacao_nulos.csv`
- `validacao_invalidos.csv`

Esses arquivos documentam a existencia das colunas esperadas, os tipos encontrados, a quantidade de valores nulos e regras simples de valores invalidos, como numeros negativos em colunas de vitimas.

## Granularidade por horas

A coluna `horario` foi incorporada ao fluxo de leitura. Durante a conversao dos CSVs para Parquet, o notebook cria a coluna derivada `data_hora`, combinando `data_inversa` e `horario`.

Com isso, o processamento incremental passou a incluir o corte `2.1 - Horas`, usando a janela inicial de `2017-01-01 00:00:00` ate `2017-01-01 00:59:59`.

## Dask e processamento paralelo

A comparacao de desempenho com Dask local foi mantida, pois ela esta presente no codigo original.

O processamento paralelo distribuido em 1, 2 e 3 maquinas fisicas continua ignorado nesta versao por limitacao externa informada.

## Pontos que ainda podem evoluir

- Adicionar testes automatizados quando a logica for movida para scripts Python.
- Extrair mais trechos do benchmark para funcoes especificas por biblioteca, se o notebook crescer.
