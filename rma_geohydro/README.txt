RMA GeoHydro v0.3.4 — REV1 | INITIAL STABLE RELEASE
Author: Riller Mairon de Oliveira Alves
License: GNU General Public License v3.0

OVERVIEW / VISÃO GERAL

RMA GeoHydro is an open-source QGIS plugin for assisted CAD/DXF processing and preliminary geometric drainage area delineation, initially focused on mining embankments and geotechnical engineering.

O RMA GeoHydro é um complemento de código aberto para QGIS, desenvolvido para auxiliar no processamento de arquivos CAD/DXF e na delimitação geométrica preliminar de áreas de drenagem, inicialmente voltado a maciços de mineração e aplicações geotécnicas.

INSTALLATION / INSTALAÇÃO

QGIS > Plugins > Manage and Install Plugins > Install from ZIP.

Select the RMA_GeoHydro_v0.3.4_REV1.zip package.

This version declares experimental=False. Availability through the official QGIS Plugin Repository depends on its approval and publication.

LANGUAGE / IDIOMA

- Português (Brasil) — PT-BR
- English (US) — EN-US

Select the interface language at the top of the plugin window.

The selected language controls the main interface and output layer names.

CAD layer recognition supports both Portuguese and English terminology, independently of the selected interface language.

Some internal attribute values and secondary technical messages may remain in Portuguese to preserve compatibility.

MAIN FEATURES / FUNCIONALIDADES

- Assisted CAD/DXF feature classification.
- Recognition of drainage channels, topographic divides and downchutes.
- Bilingual recognition of international CAD layer names.
- Preliminary geometric drainage area generation.
- Longitudinal, transverse and combined orientation settings.
- Detection of channel gaps and geometric offsets.
- Automatic geometric warning classification using the alerta_geom attribute.
- Shapefile and GeoPackage export options.
- Simplified interface with collapsible advanced settings.
- Language-specific output layer names.
- Direct access through the QGIS Plugins menu.

GEOMETRIC WARNING CLASSIFICATION

alerta_geom = 0:
No automatic geometric warning detected.

alerta_geom = 1:
Geometric warning detected; technical review required.

An alerta_geom value of 0 does not establish hydrological validity or engineering approval.

REFERENCE DATASET TESTING / TESTES

Reference file: Drenagem_macico.dxf

- Reference channel segments: 4
- Topographic divides: 12
- Downchutes: 11
- Total transverse elements: 23
- Flow arrows: 67
- Preliminary drainage areas: 22
- Areas without geometric warnings: 15
- Areas requiring geometric review: 7
- Rejected elements: 0

The reference results were confirmed in Portuguese and English using version 0.3.3.

Shapefile export was also successfully tested.

Version 0.3.4 REV1 includes targeted code-quality and Qt6 compatibility corrections. Its complete regression testing and official validation results must be confirmed separately.

VERSION 0.3.4 REV1 — CHANGES

- Fixed Flake8 F811 caused by a duplicate QFileDialog import.
- Updated QFormLayout.LabelRole to QFormLayout.ItemRole.LabelRole to address a Qt6 compatibility warning.
- Preserved direct access through the QGIS Plugins menu.
- Maintained bilingual Portuguese/English interface support.
- Preserved international CAD recognition and language-specific output layer names.
- Maintained the existing preliminary drainage area generation workflow.
- Preserved the alerta_geom attribute.

IMPORTANT LIMITATIONS / RESSALVAS TÉCNICAS

- Generated drainage areas are PRELIMINARY GEOMETRIC REPRESENTATIONS.
- They are NOT automatically validated catchments, watersheds or hydraulic designs.
- The plugin does not calculate design discharges or perform hydraulic channel sizing.
- The current workflow does not automatically determine drainage areas from terrain elevations or a digital elevation model.
- Longitudinal and transverse orientation settings do not constitute hydraulic flow-direction calculations.
- The area-generation workflow is intended for compatible ASCII DXF LWPOLYLINE geometries.
- Verify the source DXF, coordinate reference system, linear units, drainage connectivity, channel gaps, divides, downchutes and polygon boundaries.
- Generated areas require independent topographic, hydrological and engineering review before technical application.

COMPATIBILITY / COMPATIBILIDADE

Minimum declared QGIS version: 3.28
Maximum declared QGIS version: 3.99

The declared compatibility range does not guarantee successful operation in every QGIS environment.

SOURCE CODE / CÓDIGO-FONTE

https://github.com/RillerMairon/rma-geohydro

OFFICIAL QGIS PLUGIN REPOSITORY

https://plugins.qgis.org/plugins/rma_geohydro/

ISSUE TRACKER / RELATAR PROBLEMAS

https://github.com/RillerMairon/rma-geohydro/issues

LICENSE / LICENÇA

GNU General Public License v3.0.
