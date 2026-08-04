# Artefact Alpha Testing - Open-Source Python 

## Overview

This project contains a prototype implementation of the IC-ENC Gaps and Overlaps (GaOs) workflow developed as part of the GEOM186 MSc GIS dissertation.

The prototype extends earlier proof-of-concept work by restructuring overlap detection and classification processes into a modular Python codebase. The aim was to investigate how potential ENC data limit overlaps could be automatically identified and classified before manual review.

The project was developed as a research artefact and was not operationalised. Testing was performed through `test_main.py`, which orchestrates the prototype workflow.

## Objectives

The prototype explores the feasibility of:

- Creating potential overlap records from incoming S-57 ENC data.
- Comparing candidate Cell Work Items (CWIs) against:
  - Existing ENC coverage on the market.
  - Other CWIs currently within the production workflow.
- Applying business-rule filtering to reduce false positives.
- Automatically classifying overlaps based on spatial characteristics.

## Project Structure

### `test_main.py`

Test harness used to execute and evaluate the prototype workflow.

The script controls the overall processing sequence, loads required modules, and performs end-to-end testing of overlap creation and classification.

### `get_S57_overlaps.py`

Contains functions for generating and filtering S-57 ENC overlaps.

Responsibilities include:

- Creating overlap geometries.
- Applying overlap filtering rules.
- Merging overlap datasets from multiple sources.

### `autoclassifications.py`

Contains experimental methods for automatically classifying overlap records.

This includes geodesic buffering approaches and spatial analysis techniques used to categorise overlap severity and identify likely residual geometry issues.

### `static_vars.py`

Central location for static configuration values and shared variables used throughout the prototype.

### `utils`

Supporting package used to simplify imports and expose functionality from individual modules.

## Status

This repository represents prototype research and experimentation rather than production software.

Several components were developed to evaluate design options and support dissertation analysis. While the code demonstrates the feasibility of automated overlap detection and classification, the workflow was never deployed operationally and remained under active development at the conclusion of the research.
