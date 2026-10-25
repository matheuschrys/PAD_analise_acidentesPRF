# Instruções de acesso ao dashboard Power BI

O repositório reúne a análise em Python e o dashboard de acidentes da PRF. O arquivo editável do Power BI está anexado à release do projeto.

## Downloads

- [Baixar o relatório Power BI (.pbix)](https://github.com/matheuschrys/PAD_analise_acidentesPRF/releases/download/powerbi-dashboard-2026-10-25/analise_acidentes_prf.pbix)
- [Abrir a release e ver os ativos](https://github.com/matheuschrys/PAD_analise_acidentesPRF/releases/tag/powerbi-dashboard-2026-10-25)
- [Baixar o pacote de atualização (.zip)](https://github.com/matheuschrys/PAD_analise_acidentesPRF/releases/download/powerbi-dashboard-2026-10-25/Atualizacao_GitHub_PRF_PowerBI.zip)

## Como abrir

1. Baixe o arquivo `analise_acidentes_prf.pbix`.
2. Abra-o no [Power BI Desktop](https://www.microsoft.com/pt-br/power-platform/products/power-bi/desktop).
3. Explore as páginas, visuais e filtros do relatório.
4. Para atualizar os dados, confira em **Transformar dados > Configurações da fonte de dados** se caminhos e credenciais precisam de ajuste.

## Sobre o arquivo

- O relatório possui 15 páginas.
- O arquivo tem aproximadamente 125,9 MB e é distribuído como ativo da release. Ele não vem junto ao clonar o código-fonte.
- A estrutura interna do arquivo foi verificada como contêiner ZIP íntegro. A abertura e a atualização no Power BI Desktop não foram testadas neste ambiente.
- Os dados embutidos no relatório podem diferir da base e do intervalo usados pelo notebook. Confira as fontes e medidas no Power BI Desktop antes de comparar resultados.

## Sobre o projeto

Consulte o [README principal](README.md) para conhecer a análise em Python, a estrutura do projeto e a origem dos dados. Consulte também o [guia do dashboard](powerbi/README.md), que descreve as páginas e os indicadores identificados.
