# Anexo - como identificar causas de acidentes na base da PRF

Este anexo registra como vou tratar as causas dos acidentes no projeto. A base usada e a de acidentes agrupados por pessoa, com todas as causas e tipos. Por isso, a leitura precisa de um cuidado: uma linha nem sempre deve ser interpretada como um acidente unico.

## Colunas principais

- `causa_acidente`: mostra a causa presumivel registrada para o acidente.
- `causa_principal`: indica se aquela causa foi marcada como principal.
- `tipo_acidente`: descreve o tipo do acidente, por exemplo colisao, saida de pista etc.
- `id`: identificador do acidente. E a melhor coluna para contar acidentes unicos.

## Criterio que vou usar

Para descobrir as principais causas, eu uso `causa_acidente`. Quando `causa_principal` estiver disponivel, filtro somente `causa_principal == "Sim"`. Depois disso, conto `id` distintos, porque a base pode ter mais de uma linha para o mesmo acidente.

```python
df_causas = df_completo.copy()

if "causa_principal" in df_causas.columns:
    df_causas = df_causas[
        df_causas["causa_principal"].astype(str).str.strip().str.lower().eq("sim")
    ]

ranking_causas = (
    df_causas
    .dropna(subset=["causa_acidente"])
    .groupby("causa_acidente", observed=True)["id"]
    .nunique()
    .reset_index(name="total_acidentes")
    .sort_values("total_acidentes", ascending=False)
)
```

## Por que nao contar apenas linhas

A contagem por linha pode aumentar artificialmente o resultado, principalmente porque a base e por pessoa e tambem traz todas as causas/tipos. Se duas pessoas estiverem envolvidas no mesmo acidente, ou se houver mais de uma causa associada, o mesmo `id` pode aparecer mais de uma vez. Por isso, para responder quantidade de acidentes, uso `nunique` no `id`.

## Fontes consultadas

- Dados Abertos da PRF: https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf
- Dicionario de dados - Acidentes da PRF: https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dicionario-acidentes
- Espelho do dicionario de variaveis BAT 2017+ com todas as causas e tipos: https://ide.geobases.es.gov.br/documents/1690/download
