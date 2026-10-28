# RMA GeoHydro

**Open-Source QGIS Plugin for CAD/DXF Processing and Preliminary Surface Drainage Delineation**

**Version:** 0.2.3 — Experimental  
**Author:** Riller Mairon de Oliveira Alves  
**License:** GNU General Public License v3.0  
**Minimum QGIS Version:** 3.28

## Overview

RMA GeoHydro is an open-source QGIS plugin designed to assist with CAD/DXF processing and preliminary surface drainage sector delineation, particularly for mining and geotechnical engineering applications.

The plugin identifies drainage channels, topographic divides, and downchutes from user-selected CAD layers and generates preliminary drainage sectors using geometric relationships between the selected features.

The plugin is independent of any specific company or engineering project.

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

1. Download the plugin ZIP package.
2. Open QGIS.
3. Navigate to Plugins > Manage and Install Plugins.
4. Select Install from ZIP.
5. Choose the downloaded package and install it.
6. Open RMA GeoHydro from the Plugins menu.

## Basic Workflow

1. Select a compatible DXF file.
2. Confirm the coordinate reference system.
3. Select the CAD layers containing drainage channels, topographic divides, and downchutes.
4. Configure the available drainage orientation option.
5. Run the assisted drainage sector generation tool.
6. Inspect the resulting preliminary polygons and geometric warnings.
7. Export the verified results to the desired vector format.

## Requirements

- QGIS 3.28 or later within the declared QGIS 3.x compatibility range.
- A compatible DXF file containing the required drainage geometries.
- A correctly defined projected coordinate reference system for distance-based processing.

## Important Limitations

RMA GeoHydro generates preliminary geometric drainage sectors, not automatically validated hydrological catchments.

The plugin does not perform hydraulic channel sizing, calculate design discharges, or independently verify drainage flow directions.

Longitudinal and transverse orientation settings do not constitute automatic hydraulic classification.

Generated polygons, geometric gaps, offsets, and drainage boundaries must be reviewed against reliable topographic information, actual drainage structures, flow paths, and engineering design requirements.

## Development Status

Version 0.2.3 is an experimental release.

Testing with a reference DXF produced 22 preliminary drainage sectors, including automatic identification of sectors requiring geometric review.

This result is specific to the reference dataset and does not guarantee equivalent performance for other CAD drawings.

## Author

**Riller Mairon de Oliveira Alves (RMA)**

Contact: rillermairongod@gmail.com

## Source Code and Issue Tracking

Repository: https://github.com/RillerMairon/rma-geohydro

Issues: https://github.com/RillerMairon/rma-geohydro/issues

## License

This project is distributed under the GNU General Public License v3.0.
