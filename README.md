# RMA GeoHydro

**Open-Source QGIS Plugin for CAD/DXF Processing and Preliminary Surface Drainage Delineation**

**Version:** 0.2.4 — Experimental  
**Author:** Riller Mairon de Oliveira Alves  
**License:** GNU General Public License v3.0  
**Minimum QGIS Version:** 3.28

## Overview

RMA GeoHydro is an open-source QGIS plugin designed to assist with CAD/DXF processing and preliminary surface drainage sector delineation, particularly for mining and geotechnical engineering applications.

The plugin identifies drainage channels, topographic divides, and downchutes from user-selected CAD layers and generates preliminary drainage sectors using geometric relationships between the selected features.

The plugin is an independent project, with no affiliation to any specific company.

## Main Features

- Import and assisted interpretation of CAD/DXF files.
- User-controlled selection of drainage channels, topographic divides, and downchutes.
- Preliminary drainage sector generation.
- Support for longitudinal, transverse, and combined orientation settings.
- Detection of channel gaps and geometric offsets.
- Automatic geometric alert classification using the `alerta_geom` field.
- Vector layer generation and Shapefile export.
- Preliminary diagnostic information for engineering review.

## Geometric Alert Classification

Generated sectors include an integer field named `alerta_geom`.

| Value | Meaning |
|---|---|
| 0 | No automatic geometric warning detected |
| 1 | Geometric warning detected; technical review required |

A value of 0 does not indicate hydrological validation or engineering approval.

## Installation

### Option 1 — Official QGIS Plugin Repository (Recommended)

1. Open QGIS.
2. Navigate to **Plugins > Manage and Install Plugins**.
3. Open the **Settings** tab.
4. Enable **Show also experimental plugins**.
5. Search for **RMA GeoHydro**.
6. Select the plugin and click **Install Experimental Plugin**.

Official plugin page: https://plugins.qgis.org/plugins/rma_geohydro/

### Option 2 — Manual Installation

1. Download the plugin ZIP package from the GitHub Releases page.
2. Open QGIS.
3. Navigate to **Plugins > Manage and Install Plugins**.
4. Select **Install from ZIP**.
5. Choose the downloaded package and install it.

## Basic Workflow

1. Select a compatible DXF file.
2. Confirm the coordinate reference system.
3. Select the CAD layers containing drainage channels, topographic divides, and downchutes.
4. Configure the available drainage orientation settings.
5. Run the assisted drainage sector generation tool.
6. Inspect the resulting preliminary polygons and geometric warnings.
7. Export the results to the desired vector format.

## Requirements

- QGIS 3.28 or later within the declared QGIS 3.x compatibility range.
- A compatible DXF file containing the required drainage geometries.
- A correctly defined projected coordinate reference system with metric units for distance-based processing.

## Important Limitations

RMA GeoHydro generates preliminary geometric drainage sectors, not automatically validated hydrological catchments.

The plugin does not perform hydraulic channel sizing, calculate design discharges, or independently verify drainage flow directions.

Longitudinal and transverse orientation settings do not constitute automatic hydraulic classification.

Generated polygons, geometric gaps, offsets, and drainage boundaries must be reviewed against reliable topographic information, actual drainage structures, flow paths, and engineering design requirements.

## Development Status

Version 0.2.4 is an experimental release.

Testing with a reference DXF containing 23 transverse elements produced:

- **22 preliminary drainage sectors.**
- **15 sectors without automatic geometric warnings.**
- **7 sectors flagged for geometric review.**

The results were reproduced after the Flake8 E731 correction introduced in version 0.2.4.

The official QGIS Plugin Repository also reported successful automated security and quality checks for this version.

These results are specific to the reference dataset and do not guarantee equivalent performance for other CAD drawings.

## Version History

### v0.2.4 — Experimental

- Fixed Flake8 E731 warning in `setores.py`.
- Replaced an assigned lambda expression with an equivalent named function.
- Preserved preliminary drainage sector generation and geometric alert classification.

### v0.2.3 — Experimental

- Added automatic geometric alert classification using the integer `alerta_geom` field.
- Preserved the drainage sector generation workflow and vector export functionality.

### v0.2.2 — Experimental

- Improved the combined selection of topographic divides and downchutes.
- Added confirmation of CAD element counts before processing.
- Added longitudinal, transverse, and combined orientation settings.
- Improved preliminary drainage sector generation.

## Author

**Riller Mairon de Oliveira Alves (RMA)**

Contact: rillermairongod@gmail.com

## Source Code and Issue Tracking

**Official QGIS Plugin:** https://plugins.qgis.org/plugins/rma_geohydro/

**GitHub Repository:** https://github.com/RillerMairon/rma-geohydro

**GitHub Releases:** https://github.com/RillerMairon/rma-geohydro/releases

**Issue Tracker:** https://github.com/RillerMairon/rma-geohydro/issues

## License

This project is distributed under the GNU General Public License v3.0.
