# Relatorio de Verificacao dos Requisitos

Este relatorio compara o arquivo `README.md`, o PDF do trabalho e o notebook `notebooks/acidentes_prf_trabalho_part1.ipynb`.

Observacao importante: a comparacao de desempenho com Dask foi considerada nesta verificacao, pois ela aparece no notebook. Apenas o processamento paralelo distribuido em multiplas maquinas foi desconsiderado, conforme limitacao informada.

## Resumo Geral

O notebook oficial atende boa parte dos requisitos principais do trabalho: possui definicao de schema, validacao formal, conversao dos CSVs para Parquet, processamento em volumes crescentes, consultas com agrupamento, geracao de graficos e comparacao de desempenho entre Pandas, Polars, PyArrow e Dask.

Pontos corrigidos na versao atual:

- A granularidade por horas foi implementada com a coluna `horario` e o campo derivado `data_hora`.
- A validacao de schema foi formalizada com relatorios de colunas ausentes, tipos, nulos e valores invalidos.
- O caminho absoluto dos CSVs foi substituido por caminhos relativos da estrutura do projeto.
- As referencias e fontes foram adicionadas ao notebook.
- Os graficos passaram a ser salvos em `reports/`.

## Verificacao por Requisito

| Requisito | Situacao | Comentario |
|---|---:|---|
| Definicao de schemas | Atendido | O schema foi centralizado em `src/etl/schema.py` e usado pelo notebook. |
| Validacao dos schemas | Atendido | O notebook gera relatorios formais de colunas ausentes, tipos, nulos e valores invalidos em `reports/`. |
| Operacoes em grandes volumes | Atendido | O notebook processa volumes crescentes de 1 dia ate o limite maximo do dataset. O maior volume registrado foi de 4.069.582 linhas. |
| Incremento por horas | Atendido | A coluna `horario` foi incorporada ao fluxo e combinada com `data_inversa` para criar `data_hora`. O corte `2.1 - Horas` usa a janela inicial do dataset. |
| Incremento por dias | Atendido | Ha corte para `2017-01-01`, com 1.421 linhas processadas. |
| Incremento por semanas | Atendido | Ha corte ate `2017-01-07`, com 7.604 linhas processadas. |
| Incremento por meses | Atendido | Ha corte ate `2017-01-31`, com 30.388 linhas processadas. |
| Incremento por trimestres | Atendido | Ha corte ate `2017-03-31`, com 85.924 linhas processadas. |
| Incremento por semestres | Atendido | Ha corte ate `2017-06-30`, com 174.457 linhas processadas. |
| Incremento por anos | Atendido | Ha corte ate `2017-12-31`, com 342.497 linhas processadas. |
| Limite maximo do dataset | Atendido | Ha processamento ate `2025-12-31`, com 4.069.582 linhas. |
| Consultas com agrupamentos | Atendido | O notebook usa agrupamentos por `uf`, `dia_semana`/`fase_dia` e `causa_acidente`. |
| Geracao de graficos | Atendido | Ha graficos de ranking por UF, desempenho por volume, heatmap por dia/fase do dia, causas de acidente e comparativo de bibliotecas. |
| Comparacao com Pandas | Atendido | Pandas e usado no processamento incremental e no benchmark. |
| Comparacao com PyArrow | Atendido | PyArrow e usado no benchmark com `pyarrow.dataset` e `group_by`. |
| Comparacao com Polars | Atendido | Polars e usado no benchmark com `scan_parquet`, filtro e agregacao lazy. |
| Comparacao com Dask | Atendido | O notebook executa benchmark com Dask em cluster local (`LocalCluster`) e compara os tempos com Pandas, Polars e PyArrow. |
| Processamento paralelo com 1, 2 e 3 maquinas | Ignorado | Item desconsiderado conforme orientacao, pois o processamento paralelo distribuido em maquinas fisicas nao foi realizado por limitacao externa. |
| Notebook com resultados visiveis | Atendido | As celulas principais possuem `execution_count` e saidas de texto/graficos. |
| Referencias e fontes | Atendido | O notebook possui secao de referencias, documentacoes das bibliotecas e observacao sobre uso de IA. |

## Pontos Fortes

- O trabalho esta organizado em secoes que refletem os principais itens do enunciado.
- O uso de Parquet e adequado para o tema de formatos de dados e grandes volumes.
- A validacao de schema ficou mais objetiva e auditavel por meio de arquivos `.csv` em `reports/`.
- A granularidade por horas agora faz parte do processamento incremental.
- A comparacao entre Pandas, Polars, PyArrow e Dask esta coerente e usa a mesma operacao principal: filtro por data e agrupamento por UF.
- O volume maximo processado, 4.069.582 linhas, esta claramente registrado.

## Pontos Ainda Observaveis

1 - Processamento paralelo distribuido.

Como a comparacao com Dask local foi feita, mas o processamento paralelo em maquinas fisicas nao foi possivel, recomenda-se deixar isso claro em uma celula Markdown, por exemplo:

```markdown
## Observacao sobre processamento paralelo com Dask

O benchmark com Dask foi executado em ambiente local usando `LocalCluster`. O processamento paralelo distribuido com 3 maquinas fisicas nao foi executado devido a limitacoes de infraestrutura informadas pelo professor. Por isso, apenas o item de processamento distribuido em multiplas maquinas foi desconsiderado nesta entrega.
```

## Conclusao

Considerando a comparacao com Dask local e desconsiderando apenas o processamento paralelo distribuido em multiplas maquinas, o trabalho esta alinhado aos principais requisitos do README e do PDF.

Foram implementados os principais ajustes apontados anteriormente:

1 - Granularidade por horas.
2 - Validacao formal de schema.
3 - Caminhos relativos e estrutura de projeto.
4 - Referencias e fontes utilizadas.
5 - Comentario claro sobre Dask local versus processamento paralelo distribuido.
