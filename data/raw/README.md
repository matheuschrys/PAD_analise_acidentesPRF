# Dados Brutos

Esta pasta deve receber os CSVs originais usados no trabalho.

Fonte dos dados: Dados Abertos da Policia Rodoviaria Federal (PRF), base BAT - Boletim de Acidente de Transito, documentos CSV de Acidentes agrupados por pessoa, com todas as causas e tipos de acidentes.

https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf

Regra de uso:

- Nao editar estes arquivos diretamente.
- Usar os arquivos desta pasta como fonte de entrada do ETL.
- Manter os CSVs fora do Git, pois os arquivos sao grandes.
- Conferir `CHECKSUMS.sha256` caso seja necessario validar a integridade dos dados.

Os dados processados devem ser gerados em `data/processed/`.
