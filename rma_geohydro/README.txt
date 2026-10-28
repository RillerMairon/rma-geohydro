RMA GeoHydro 0.2.0 - EXPERIMENTAL
Author: Riller Mairon de Oliveira Alves
License: GPL-3.0

INSTALL: QGIS > Plugins > Manage and Install Plugins > Install from ZIP.
The ZIP root must contain the folder rma_geohydro.

TWO ACTIONS IN THE DIALOG:
1. GERAR SETORES DE DRENAGEM (assistido): runs the recovered universal workflow.
   Select DXF, channel, dividers, optional downchutes, optional flow arrows,
   and optional external boundary. Enter a metric projected EPSG.
   Preliminary areas are added as TEMPORARY QGIS layers for visual inspection.
   Optionally export the temporary result to SHP after processing.
2. Classificar linhas e exportar: retains v0.1 layer classification and
   export functionality, with optional CLOSED-RING polygonization.

WARNING: Sector polygon geometry is a preliminary geometric approximation.
Lines spanning gaps may be interpolated; verify all gaps and boundaries.
The longitudinal/transverse setting in the v0.1 classifier still only
records orientation and is not a hydraulic computation.
No fixed coordinate, source DXF name, or CAD layer name is required.
Check the resulting sectors against the original CAD and engineering data.
Always work on copies, never on production source data.
This plugin has been checked for Python syntax but has NOT been
run or validated here in a QGIS desktop application.

VERSÃO 0.2.2: modo Ambas e seleção de DESCIDA corrigida. Valide a quantidade de DIVISOR e DESCIDA na tela de confirmação. A orientação declarada não comprova classificação hidráulica; o traçado é construído a partir das camadas escolhidas.
