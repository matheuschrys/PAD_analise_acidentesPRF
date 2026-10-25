# Dashboard Power BI — Análise de Acidentes da PRF

Este diretório contém o relatório de análise exploratória de acidentes em rodovias federais, desenvolvido em **Microsoft Power BI**.

## Arquivo

- **[Baixar `analise_acidentes_prf.pbix`](https://github.com/matheuschrys/PAD_analise_acidentesPRF/releases/download/powerbi-dashboard-2026-10-25/analise_acidentes_prf.pbix)** — projeto editável do Power BI Desktop, com modelo de dados, medidas e visualizações.
- **Tamanho aproximado:** 125,9 MB (120,1 MiB).
- **Conteúdo verificado:** 15 páginas de relatório. A integridade estrutural do contêiner `.pbix` (ZIP) foi verificada; a abertura no Power BI Desktop não foi testada neste ambiente.

## Principais painéis

| Página do relatório | Tema | Conteúdo identificado |
| --- | --- | --- |
| Informações Gerais | Visão executiva | Acidentes, vítimas, mortos, feridos, envolvidos, índice de letalidade; filtros de UF, BR, ano e fase do dia |
| Geografia e Rodovias - 1 | Trechos críticos | Mapa e tabela dos trechos com acidentes fatais |
| Geografia e Rodovias - 6 | Estados | Mapa temático e ranking de letalidade por UF |
| Geografia e Rodovias - 8 | Rodovias | Densidade de acidentes por km e comparação com referência nacional |
| Tempo e Evolução - 2 | Evolução mensal | Acidentes por gravidade ao longo do tempo |
| Tempo e Evolução - 3 | Sazonalidade semanal | Distribuição por fase do dia e dia da semana |
| Tempo e Evolução - 7 | Tendência por tipo | Variação anual de acidentes fatais por tipo de acidente |
| Tempo e Evolução - 11 | Perfil trimestral | Percentuais de ilesos, feridos e mortos por trimestre |
| Causas, Tipo de Acidente e Infraestrutura - 4 | Causas | Frequência e gravidade por causa/tipo de acidente |
| Causas, Tipo de Acidente e Infraestrutura - 9 | Infraestrutura | Tipo de pista, traçado da via e pontuação de gravidade |
| Veículos e Envolvidos - 5 | Veículos | Acidentes fatais segundo tipo e marca de veículo |
| Veículos e Envolvidos - 10 | Perfil demográfico | Envolvidos em acidentes fatais por faixa etária e sexo |
| Veículos e Envolvidos - 12 | Perfil de gravidade | Gravidade conforme tipo de veículo e papel do envolvido |
| Página 1 | Análises complementares | Horário, município, condição meteorológica e marca do veículo |
| Página 2 | Gravidade por fase do dia | Mortos, feridos graves e feridos leves por fase do dia |

Os nomes na primeira coluna refletem os títulos presentes no arquivo original. As duas últimas páginas possuem nomes genéricos no Power BI, aqui documentados pelo conteúdo observado; **os nomes internos não foram alterados**.

## Como abrir

1. Instale o [Power BI Desktop](https://www.microsoft.com/pt-br/power-platform/products/power-bi/desktop).
2. Baixe o arquivo `.pbix` pelo link acima ou pela [página da release](https://github.com/matheuschrys/PAD_analise_acidentesPRF/releases/tag/powerbi-dashboard-2026-10-25).
3. Abra o arquivo baixado no Power BI Desktop.
4. Explore os visuais e os filtros disponíveis em cada página.
5. Para **atualizar as fontes**, verifique *Transformar dados > Configurações da fonte de dados* e ajuste caminhos/credenciais, se necessário.

O relatório possui um modelo de dados embutido no arquivo, mas a conexão utilizada para **atualizações futuras não foi validada** fora do Power BI Desktop. Não há garantia de atualização automática ou publicação pública no Power BI Service.

## Escopo dos indicadores

As visualizações incluem medidas rotuladas no projeto como `Total de Acidentes`, `Total de Mortos`, `Total de Feridos Leves`, `Total de Feridos Graves`, `Índice de Letalidade por 100 Envolvidos`, `Pontuação de Gravidade`, `Densidade de Acidentes por KM` e análises de variação temporal. Os cálculos efetivos devem ser consultados no modelo de dados e nas medidas DAX do projeto ao abrir o PBIX.

**Atenção metodológica:** diferenças na unidade de análise (ocorrência x pessoa envolvida), período, filtros e definição de fatalidade podem afetar a interpretação de totais e percentuais. Para relatórios oficiais, confira os metadados dos dados da PRF e as fórmulas DAX antes de utilizar os resultados.

## Download e atualização

O arquivo `.pbix` está publicado como ativo da release do projeto, separado do histórico Git. Por isso, clonar o repositório não baixa o relatório; use o link de download acima. O botão de visualização do GitHub não substitui a execução no Power BI Desktop.