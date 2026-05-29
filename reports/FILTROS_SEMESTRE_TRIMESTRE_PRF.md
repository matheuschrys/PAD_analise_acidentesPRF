# Filtros por semestre e trimestre no dataset da PRF

Este anexo deixa pronto o criterio que usei para separar o dataset por trimestre e por semestre. A base tem a coluna `data_inversa`, entao o filtro deve partir dela. A ideia e criar colunas auxiliares de periodo e depois usar essas colunas nas consultas.

## Colunas criadas

- `ano`: ano da ocorrencia.
- `trimestre`: trimestre calendario, de 1 a 4.
- `semestre`: semestre calendario, 1 ou 2.
- `ano_trimestre`: identificador no formato `2025-T1`, `2025-T2` etc.
- `ano_semestre`: identificador no formato `2025-S1` ou `2025-S2`.

## Exemplo direto no notebook

```python
df_periodos = df_completo.copy()
datas = pd.to_datetime(df_periodos["data_inversa"], errors="coerce")

df_periodos["ano"] = datas.dt.year
df_periodos["trimestre"] = datas.dt.quarter
df_periodos["semestre"] = ((datas.dt.month - 1) // 6) + 1

# Exemplo: primeiro trimestre de 2025
primeiro_trimestre_2025 = df_periodos[
    (df_periodos["ano"] == 2025) &
    (df_periodos["trimestre"] == 1)
]

# Exemplo: segundo semestre de 2025
segundo_semestre_2025 = df_periodos[
    (df_periodos["ano"] == 2025) &
    (df_periodos["semestre"] == 2)
]
```

## Usando as funcoes do projeto

Tambem deixei funcoes prontas em `src/etl/time_filters.py` para nao precisar repetir a logica em toda consulta.

```python
from src.etl.time_filters import add_period_columns, filter_by_quarter, filter_by_semester, summarize_by_period

# Adiciona as colunas de periodo no dataset completo
df_periodos = add_period_columns(df_completo)

# Filtra um trimestre especifico
trimestre_1_2025 = filter_by_quarter(df_completo, year=2025, quarter=1)

# Filtra um semestre especifico
semestre_2_2025 = filter_by_semester(df_completo, year=2025, semester=2)

# Resumo por trimestre, contando acidentes unicos e somando vitimas
resumo_trimestral = summarize_by_period(df_periodos, "ano_trimestre")

# Resumo por semestre, contando acidentes unicos e somando vitimas
resumo_semestral = summarize_by_period(df_periodos, "ano_semestre")
```

## Observacao para o trabalho

Como a base usada no projeto e agrupada por pessoa e pode trazer mais de uma linha para o mesmo acidente, nas contagens gerais e melhor usar `id` distinto (`nunique`) quando a pergunta for quantidade de acidentes. Para totais de vitimas, como `mortos`, `feridos_graves` e `feridos_leves`, a soma das colunas continua sendo a forma mais direta dentro do recorte escolhido.
