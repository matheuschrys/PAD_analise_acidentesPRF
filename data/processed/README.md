# Dados Processados

Esta pasta recebe os dados prontos para analise.

O notebook principal salva os arquivos Parquet em:

```text
data/processed/dados_otimizados/
```

Esses arquivos sao derivados dos CSVs de `data/raw/` e podem ser recriados executando o notebook.

Durante a conversao, tambem e criada a coluna derivada `data_hora`, usada para processamentos com granularidade por horas.
