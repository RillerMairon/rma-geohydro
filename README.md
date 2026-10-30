# RMA GeoHydro

**Open-Source QGIS Plugin for CAD/DXF Processing and Preliminary Surface Drainage Area Delineation**

**Version:** 0.3.3 — Initial Stable Release Candidate  
**Author:** Riller Mairon de Oliveira Alves  
**License:** GNU General Public License v3.0  
**Minimum QGIS Version:** 3.28  
**Languages:** Portuguese (Brazil) and English (US)

## Overview

RMA GeoHydro is an open-source QGIS plugin designed to assist with CAD/DXF processing and preliminary surface drainage area delineation, particularly for mining embankments and geotechnical engineering applications.

The plugin identifies drainage channels, topographic divides, and downchutes from user-selected CAD layers. It generates preliminary drainage areas using geometric relationships between the selected features.

RMA GeoHydro supports Portuguese and English interfaces and bilingual CAD layer recognition, making it suitable for testing with engineering drawings from different countries.

The plugin is an independent project, with no affiliation to any specific company.

## Main Features

- Assisted import and interpretation of CAD/DXF files.
- Automatic recognition of CAD layer names in Portuguese and English.
- User-controlled selection and verification of drainage elements.
- Preliminary geometric drainage area generation.
- Support for longitudinal, transverse, and combined orientation settings.
- Detection of channel gaps and geometric offsets.
- Automatic geometric warning classification using the `alerta_geom` field.
- Simplified interface with collapsible advanced recognition settings.
- Portuguese (Brazil) and English (US) interface options.
- Language-specific output layer and export file names.
- Shapefile and GeoPackage export options.
- Diagnostic information to support engineering review.

## Multilingual Support

RMA GeoHydro provides two interface languages:

- Portuguese (Brazil) — PT-BR
- English (US) — EN-US

The selected language controls the main interface labels and output layer names.

CAD layer recognition operates independently of the selected interface language. The plugin can recognize Portuguese and English technical terminology within the same drawing.

Examples include:

| Portuguese | English |
|---|---|
| Canal de drenagem | Drainage Channel |
| Canal periférico | Peripheral Channel |
| Divisor topográfico | Topographic Divide |
| Descida d'água | Downchute |
| Setas de fluxo | Flow Arrows |
| Áreas de drenagem preliminares | Preliminary Drainage Areas |

Additional recognition keywords are accessible through the advanced settings.

Some internal attribute values and secondary messages may remain untranslated in this release.

## Output Layers

The plugin generates vector layers representing the identified drainage elements and preliminary drainage areas.

### Portuguese Interface

- `RMA_01_setas_fluxo`
- `RMA_02_divisores_descidas`
- `RMA_03_canais`
- `RMA_04_AREAS_DRENAGEM_PRELIMINARES_REVISAR`

### English Interface

- `RMA_01_flow_arrows`
- `RMA_02_divides_downchutes`
- `RMA_03_channels`
- `RMA_04_PRELIMINARY_DRAINAGE_AREAS_REVIEW`

The names of the original CAD layers are not changed.

## Geometric Warning Classification

Generated preliminary drainage areas include an integer attribute named `alerta_geom`.

| Value | Meaning |
|---|---|
| 0 | No automatic geometric warning detected |
| 1 | Geometric warning detected; technical review required |

The field name remains unchanged in both languages to maintain compatibility with existing processing workflows.

A value of 0 does not indicate hydrological validation, geometric accuracy certification, or engineering approval.

## Installation

### Option 1 — Official QGIS Plugin Repository

Once version 0.3.3 has been approved and published in the official QGIS Plugin Repository:

1. Open QGIS.
2. Navigate to **Plugins > Manage and Install Plugins**.
3. Search for **RMA GeoHydro**.
4. Select the available compatible version.
5. Click **Install Plugin**.

Until the non-experimental release is published, an earlier experimental version may still be available. In that case, enable **Show also experimental plugins** under Settings.

Official plugin page: https://plugins.qgis.org/plugins/rma_geohydro/

### Option 2 — Manual Installation

1. Download the version 0.3.3 ZIP package from GitHub Releases when published.
2. Open QGIS.
3. Navigate to **Plugins > Manage and Install Plugins**.
4. Select **Install from ZIP**.
5. Choose the downloaded package.
6. Install and open RMA GeoHydro.

## Basic Workflow

1. Select a compatible CAD/DXF file.
2. Confirm the coordinate reference system.
3. Identify the CAD layers containing drainage channels, topographic divides, and downchutes.
4. Review the automatically recognized drainage elements.
5. Configure the appropriate drainage orientation settings.
6. Run the assisted preliminary drainage area generation tool.
7. Inspect the generated polygons, channel gaps, offsets, and geometric warnings.
8. Export the results to Shapefile or GeoPackage.
9. Review and validate the results using appropriate engineering information.

## Requirements

- QGIS 3.28 or later, within the declared QGIS 3.x compatibility range.
- Compatible CAD/DXF drawings containing drainage-related line geometries.
- An appropriately defined projected coordinate reference system with suitable linear units for distance-based processing.

Compatibility declarations do not guarantee successful operation in every QGIS version or operating environment.

## Reference Dataset Testing

Version 0.3.3 was tested using the reference file `Drenagem_macico.dxf`.

The test produced:

| Parameter | Result |
|---|---:|
| Reference channel segments | 4 |
| Topographic divides | 12 |
| Downchutes | 11 |
| Total transverse elements | 23 |
| Flow arrows | 67 |
| Preliminary drainage areas | 22 |
| Areas without automatic warnings | 15 |
| Areas flagged for review | 7 |
| Rejected elements | 0 |

The same feature counts and preliminary drainage area counts were observed with the Portuguese and English interfaces.

The seven areas flagged for geometric review corresponded to sector identifiers 4, 5, 9, 16, 17, 18, and 19.

Three channel gaps were reported, approximately 30.13 m, 22.96 m, and 92.43 m.

Shapefile export was also successfully tested.

These observations relate to the reference dataset and do not establish universal compatibility or hydrological correctness.

## Important Engineering Limitations

RMA GeoHydro generates **preliminary geometric drainage areas**, not automatically validated hydrological catchments or watersheds.

The current version does not independently:

- Determine surface flow direction from a digital elevation model.
- Calculate design discharges or hydraulic channel capacities.
- Validate drainage boundaries against terrain elevations.
- Verify the hydraulic connectivity of all drainage structures.
- Certify the suitability of generated areas for engineering design.

Longitudinal and transverse orientation settings do not constitute automatic hydraulic classification.

Generated polygons, offsets, gaps, boundaries, and drainage paths must be reviewed against reliable topographic information, actual drainage structures, and applicable engineering requirements before technical use.

## Development Status

Version 0.3.3 is intended as the first non-experimental release of RMA GeoHydro, following the experimental 0.2.x series.

The release includes interface internationalization, improved CAD layer recognition, and usability enhancements while retaining the existing preliminary geometric processing workflow.

Testing with additional DXF datasets, QGIS versions, and operating environments remains important.

Future development may include support for elevation-based topographic analysis, contour lines, digital elevation models, and improved drainage area delineation methods.

These future features are not part of version 0.3.3.

## Version History

### v0.3.3 — Initial Stable Release Candidate

- Added language-specific output layer and export file names.
- Replaced previous drainage sector naming with preliminary drainage area terminology in the output layer names.
- Preserved the existing geometric processing workflow.
- Maintained the `alerta_geom` attribute and geometric warning classification.
- Confirmed consistent reference DXF results in Portuguese and English.
- Confirmed Shapefile export in the reference test.

### v0.3.2 — Experimental Development

- Simplified the CAD layer classification interface.
- Moved recognition keyword lists into collapsible advanced settings.
- Improved readability and organization.
- Preserved bilingual CAD layer recognition.

### v0.3.1 — Experimental Development

- Expanded recognition of international CAD layer terminology.
- Added English recognition terms for drainage channels, topographic divides, and downchutes.
- Maintained Portuguese CAD terminology for compatibility with existing drawings.

### v0.3.0 — Experimental Development

- Introduced Portuguese and English interface selection.
- Updated user-facing terminology to preliminary drainage areas.
- Added multilingual interface support while preserving the original geometry workflow.

### v0.2.5 — Experimental Development

- Updated legacy QGIS/Qt enumeration references.
- Improved source-code compatibility with newer QGIS/Qt API conventions.
- Preserved the existing geometric processing workflow.

### v0.2.4 — Experimental

- Fixed the Flake8 E731 warning in `setores.py`.
- Replaced an assigned lambda expression with an equivalent named function.
- Preserved preliminary drainage area generation and geometric alert classification.

### v0.2.3 — Experimental

- Added automatic geometric warning classification using the integer `alerta_geom` attribute.
- Preserved drainage area generation and vector export functionality.

### v0.2.2 — Experimental

- Improved the combined selection of topographic divides and downchutes.
- Added confirmation of CAD element counts before processing.
- Added longitudinal, transverse, and combined orientation settings.
- Improved preliminary geometric drainage area generation.

## Contributing and Feedback

RMA GeoHydro is an independent open-source project.

Users are welcome to report bugs, suggest improvements, and contribute testing feedback through GitHub Issues.

Additional testing with international CAD/DXF datasets is particularly welcome.

## Author

**Riller Mairon de Oliveira Alves (RMA)**

Contact: rillermairongod@gmail.com

## Source Code and Issue Tracking

**Official QGIS Plugin:**  
https://plugins.qgis.org/plugins/rma_geohydro/

**GitHub Repository:**  
https://github.com/RillerMairon/rma-geohydro

**GitHub Releases:**  
https://github.com/RillerMairon/rma-geohydro/releases

**Issue Tracker:**  
https://github.com/RillerMairon/rma-geohydro/issues

## License

This project is distributed under the GNU General Public License v3.0.
