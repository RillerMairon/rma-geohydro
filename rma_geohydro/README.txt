RMA GeoHydro v0.3.0 — INITIAL STABLE CANDIDATE / CANDIDATA ESTÁVEL INICIAL
Author: Riller Mairon de Oliveira Alves | License GPL-3.0

INSTALL / INSTALAÇÃO:
QGIS > Plugins > Manage and Install Plugins > Install from ZIP.
This package declares experimental=False. Official repository listing requires separate upload and approval.

LANGUAGE / IDIOMA:
Choose Português (Brasil) or English (US) at the top of the plugin window.
Preference is saved in QGIS settings; the main interface and key DXF selection/confirmation prompts have English translations.
Some legacy technical diagnostics and CAD-specific field values remain in Portuguese to preserve compatibility.

FUNCTION:
- CAD/DXF feature classification and export.
- PRELIMINARY GEOMETRIC drainage areas generated between selected transverse lines.
- Optional SHP/GPKG export and geometric warnings (alerta_geom = 0 or 1).
- Only ASCII DXF LWPOLYLINE entities are accepted by the area-generation workflow.

IMPORTANT LIMITATIONS / RESSALVAS:
- Drainage areas are NOT validated catchments, watersheds or hydraulic designs.
- alerta_geom=0 does NOT mean approval or hydrological validity.
- No automatic terrain-flow or elevation-based catchment processing is performed.
- The longitudinal / transverse selection is operational metadata; it is NOT a hydraulic direction solver.
- Verify source DXF, CRS in metres, connectivity, gaps, topographic divides, downchutes, and polygon boundaries.
- Preserve previous v0.2.4/v0.2.5 packages. Do not rely on this candidate in engineering design without checks.
- Demonstrated prior reference DXF: 22 preliminary polygons, 7 geometric alerts; not yet regression-tested in desktop QGIS for this build.
