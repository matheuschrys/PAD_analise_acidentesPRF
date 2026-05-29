# Anexo - acidentes relacionados a alcool/embriaguez na PRF

Este anexo reune os numeros que encontrei em publicacoes da PRF sobre sinistros ligados a alcool ou embriaguez ao volante. Como os CSVs originais nao ficam salvos no Git deste projeto, deixei os valores oficiais em formato de texto e tambem em `reports/acidentes_embriaguez_prf_resumo_oficial.csv`.

## Sinistros com causa principal ingestao de alcool pelo condutor

| Ano | Sinistros | Mortes | Feridos | Fonte |
|---:|---:|---:|---:|---|
| 2024 | 3.854 | 194 | 3.108 | PRF, 30/01/2026 |
| 2025 | 3.685 | 223 | 3.219 | PRF, 30/01/2026 |

Na pagina de 30/01/2026 existe uma diferenca pequena no numero de feridos de 2025: o texto cita 3.129, mas a tabela da propria pagina informa 3.219. Neste projeto, mantive 3.219 porque segui a tabela da PRF e registrei essa observacao no CSV.

## Comparativo divulgado pela PRF

| Periodo | Sinistros envolvendo motorista sob efeito de alcool | Mortes | Autuacoes por embriaguez/recusa | Detidos por embriaguez |
|---|---:|---:|---:|---:|
| 2023 | 3.600 | 176 | 60.142 | 4.360 |
| 2024 | 3.854 | 194 | 58.115 | 4.052 |
| Jan-Nov/2024 | 3.507 | 178 | 52.664 | 3.668 |
| Jan-Nov/2025 | 3.355 | 204 | 46.741 | 3.074 |

## Recortes informados para 2025

| Recorte | Ocorrencias |
|---|---:|
| Sabados | 1.016 |
| Domingos | 1.197 |
| Noite | 1.286 |
| Madrugada | 1.019 |

A PRF tambem informou, para 2025, mais de 3,5 milhoes de testes de alcoolemia, mais de 7.900 autuacoes por conduzir sob efeito de alcool e mais de 43 mil recusas ao teste do etilometro.

## Como eu filtraria no dataset do projeto

Para puxar esses casos no dataset local, o caminho e procurar termos relacionados a alcool na coluna `causa_acidente`. Quando a coluna `causa_principal` existir, filtro apenas os casos marcados como causa principal. Isso evita misturar causas secundarias com a causa principal do acidente.

```python
termos_alcool = r"alcool|álcool|alcoolemia|embriaguez|bebida|substâncias psicoativas|substancias psicoativas"

df_alcool = df_completo[
    df_completo["causa_acidente"].astype(str).str.contains(termos_alcool, case=False, regex=True, na=False)
].copy()

if "causa_principal" in df_alcool.columns:
    df_alcool = df_alcool[
        df_alcool["causa_principal"].astype(str).str.strip().str.lower().eq("sim")
    ]

resumo_alcool = (
    df_alcool
    .assign(ano=pd.to_datetime(df_alcool["data_inversa"]).dt.year)
    .groupby("ano")
    .agg(
        acidentes=("id", "nunique"),
        mortos=("mortos", "sum"),
        feridos_graves=("feridos_graves", "sum"),
        feridos_leves=("feridos_leves", "sum"),
    )
    .reset_index()
)
```

## Observacao sobre a base local

Nesta copia do repositorio, os CSVs brutos e os Parquets derivados nao estao presentes. Por isso, o ranking recalculado diretamente pelo dataset deve ser gerado quando os arquivos originais estiverem em `data/raw/` ou quando os Parquets estiverem em `data/processed/dados_otimizados/`.

## Fontes usadas

- PRF - Dia Nacional de Mobilizacao contra embriaguez ao volante, 30/01/2026: https://www.gov.br/prf/pt-br/noticias/nacionais/2026/janeiro/prf-promove-dia-nacional-de-mobilizacao-contra-a-embriaguez-ao-volante-1
- PRF - Operacao Rodovida Ano Novo, 30/12/2025: https://www.gov.br/prf/pt-br/noticias/nacionais/2025/dezembro/operacao-rodovida-ano-novo-prf-reforca-tolerancia-zero-a-mistura-de-alcool-e-direcao-para-diminuir-mortes-no-transito
