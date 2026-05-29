# Analise das causas de acidentes nos dados da PRF

## Resposta curta

Sim. Existe forma de descobrir as causas dos acidentes no projeto: os CSVs da PRF usados neste trabalho sao da base **Agrupados por pessoa - Todas as causas e tipos de acidentes**, e o dicionario oficial da PRF descreve a coluna `causa_acidente` como a causa presumivel do acidente, baseada em vestigios, indicios e provas coletadas no local.

Para responder quais foram as causas mais frequentes, a consulta recomendada e agrupar por `causa_acidente`. Quando a coluna `causa_principal` estiver disponivel, o ideal e filtrar `causa_principal == "Sim"` para obter o ranking de causas principais, e contar acidentes unicos por `id` para evitar duplicidade por pessoa envolvida.

## O que foi verificado

1. A pagina oficial de Dados Abertos da PRF informa que a base BAT disponibiliza arquivos de acidentes em CSV, inclusive a versao **Agrupados por pessoa - Todas as causas e tipos de acidentes** para 2017 em diante.
2. A pagina oficial do Dicionario de Dados de Acidentes da PRF aponta o dicionario especifico para **acidentes agrupados por pessoa com todas as causas e tipos de acidentes (2017 em diante)**.
3. O dicionario identifica:
   - `causa_principal`: indica se a causa do acidente foi identificada como principal pelo policial.
   - `causa_acidente`: causa presumivel do acidente, baseada nos vestigios, indicios e provas coletadas no local do acidente.
   - `tipo_acidente`: tipo do acidente, como colisao frontal, saida de pista etc.
4. O notebook do projeto ja mostra essas colunas na amostra lida do CSV bruto: `causa_principal`, `causa_acidente`, `ordem_tipo_acidente` e `tipo_acidente`.

## Como interpretar no projeto

- `causa_acidente` responde **qual causa foi associada ao acidente**.
- `causa_principal` responde **se aquela causa foi marcada como principal**.
- Como a base e de pessoas e contem todas as causas/tipos, uma contagem simples de linhas pode superestimar a quantidade de acidentes. Por isso, para ranking de causas de acidentes, a abordagem mais segura e contar `id` distintos.

Consulta recomendada em Pandas:

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

## Limite da verificacao local

Os CSVs brutos e os Parquets derivados nao estao versionados no Git deste repositorio. Localmente, a pasta `data/raw/` contem apenas `README.md` e `CHECKSUMS.sha256`, e `data/processed/dados_otimizados/` nao esta presente. Portanto, nesta revisao foi possivel confirmar a existencia e o significado das colunas pelo dicionario oficial da PRF, pelo schema/notebook do projeto e pelas saidas ja salvas no notebook; para listar o ranking real atualizado, e necessario executar o notebook com os CSVs originais na pasta `data/raw/`.

## Fontes externas consultadas

- Dados Abertos da PRF: https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf
- Dicionario de dados - Acidentes da PRF: https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dicionario-acidentes
- Espelho indexado do dicionario de variaveis BAT 2017+ com todas as causas e tipos: https://ide.geobases.es.gov.br/documents/1690/download
