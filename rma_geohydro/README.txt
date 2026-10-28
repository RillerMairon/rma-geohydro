RMA GeoHydro — v0.1.0 (experimental)
Autor: RMA | Plugin independente, sem vinculacao empresarial.

INSTALACAO
QGIS > Complementos > Gerenciar e instalar complementos > Instalar a partir de ZIP.
Selecione RMA_GeoHydro_v0.1.0.zip. Ative o plugin e clique no icone RMA.

COMO USAR
1. Abra o plugin e selecione um DXF.
2. Escolha a subcamada e confira o campo que indica o layer CAD de cada entidade.
3. Informe o EPSG original do CAD. Nunca atribua um EPSG arbitrario.
4. Ajuste as palavras-chave para divisores, canais e descidas, conforme os nomes de layers do seu DXF.
5. Informe o tipo de canal longitudinal/transversal e a tolerancia de conexao (metros).
6. Escolha pasta e formato de saida, opcionalmente ative a polygonizacao.
7. Clique Analisar e exportar e confira o diagnostico TXT.

REQUISITOS
QGIS 3.28+ com PyQt5 e GDAL/OGR (normalmente inclusos no QGIS).
Arquivos DXF com entidades geometricas lineares e campo de layer CAD disponivel.

LIMITACOES IMPORTANTES
- Nao desenha automaticamente um sistema completo de drenagem e NAO dimensiona canais.
- Classifica linhas por nomes de layers CAD e NAO por interpretacao visual/topografica.
- A escolha longitudinal/transversal e registrada no diagnostico, mas nao modifica a geometria.
- A polygonizacao so produz superficies quando os segmentos delimitam aneis fechados.
- Nao faz snapping automatico nem corrige lacunas ou linhas que cruzam sem nos.
- Somente considera extremidades de linhas no diagnostico aproximado de conexoes.
- Sem MDE ou cotas confiaveis, nao estima sentido de fluxo ou declividade.
- O formato SHP limita tamanho de nomes de campo e nao preserva todos os tipos.
- Execute primeiro em COPIA do DXF e em pasta nova, pois arquivos de saida com os mesmos nomes sao sobrescritos.
- Teste primeiro em amostra pequena; nao houve teste de interface dentro de uma instalacao real do QGIS neste ambiente.

Este e um prototipo funcional de classificacao e diagnostico. A automatizacao
geometrica especializada do script anterior devera ser portada e testada como
uma proxima versao apos conferencia das regras e geometrias originais.
