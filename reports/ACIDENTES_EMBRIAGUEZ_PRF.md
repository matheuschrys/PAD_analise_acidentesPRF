# Acidentes por embriaguez ou alcool no transito - PRF

## Resposta direta

Sim, consegui levantar dados oficiais relacionados a embriaguez/alcool no transito em rodovias federais. Como os CSVs brutos da PRF nao estao versionados neste repositorio, os numeros abaixo foram consolidados a partir de publicacoes oficiais da PRF e salvos tambem em `reports/acidentes_embriaguez_prf_resumo_oficial.csv`.

## Dados nacionais oficiais encontrados

### Sinistros com causa principal ingestao de alcool pelo condutor

| Ano | Sinistros | Mortes | Feridos | Fonte |
|---:|---:|---:|---:|---|
| 2024 | 3.854 | 194 | 3.108 | PRF, noticia de 30/01/2026 |
| 2025 | 3.685 | 223 | 3.219 | PRF, noticia de 30/01/2026 |

Observacao: na noticia de 30/01/2026, o paragrafo textual cita 3.129 feridos em 2025, mas a tabela da propria pagina informa 3.219. Para manter consistencia tabular, o CSV deste repositorio usa 3.219 e registra essa divergencia na coluna `observacao`.

### Comparativo adicional divulgado pela PRF em 30/12/2025

| Periodo | Sinistros envolvendo motoristas sob efeito de alcool | Mortes | Autuados por embriaguez - constatacao e recusa | Detidos por embriaguez |
|---|---:|---:|---:|---:|
| 2023 | 3.600 | 176 | 60.142 | 4.360 |
| 2024 | 3.854 | 194 | 58.115 | 4.052 |
| Jan-Nov/2024 | 3.507 | 178 | 52.664 | 3.668 |
| Jan-Nov/2025 | 3.355 | 204 | 46.741 | 3.074 |

### Distribuicao informada para 2025

A PRF informou que, em 2025, a maioria dos sinistros cuja causa principal foi ingestao de alcool pelo condutor ocorreu:

| Recorte | Ocorrencias |
|---|---:|
| Sabados | 1.016 |
| Domingos | 1.197 |
| Periodo da noite | 1.286 |
| Madrugada | 1.019 |

A mesma publicacao informou ainda mais de 3,5 milhoes de testes de alcoolemia em 2025, mais de 7.900 motoristas autuados por conduzir sob efeito de alcool e mais de 43 mil recusas ao teste do etilometro.

## Como extrair isso do dataset do projeto

Para reproduzir no dataset bruto/Parquet do projeto, use a coluna `causa_acidente` e busque termos relacionados a alcool, embriaguez e substancias psicoativas. Como a base usada no projeto e de pessoa/todas as causas e tipos, a recomendacao e filtrar `causa_principal == "Sim"`, quando a coluna existir, e contar acidentes unicos pelo `id`.

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

## Limite local

Nesta copia do repositorio, `data/raw/` possui apenas `README.md` e `CHECKSUMS.sha256`, e `data/processed/dados_otimizados/` nao existe. Por isso, nao foi possivel recalcular localmente o ranking completo a partir dos CSVs do projeto. O arquivo CSV adicionado nesta entrega contem os valores oficiais encontrados nas paginas da PRF, e o bloco acima deixa a consulta pronta para rodar quando os CSVs/Parquets estiverem presentes.

## Fontes

- PRF - Dia Nacional de Mobilizacao contra embriaguez ao volante, publicado em 30/01/2026: https://www.gov.br/prf/pt-br/noticias/nacionais/2026/janeiro/prf-promove-dia-nacional-de-mobilizacao-contra-a-embriaguez-ao-volante-1
- PRF - Operacao Rodovida Ano Novo, publicado em 30/12/2025: https://www.gov.br/prf/pt-br/noticias/nacionais/2025/dezembro/operacao-rodovida-ano-novo-prf-reforca-tolerancia-zero-a-mistura-de-alcool-e-direcao-para-diminuir-mortes-no-transito
