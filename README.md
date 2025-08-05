# ReCreate-Element-Database
## Relational Database for Reusable Precast Concrete Elements
This repository includes a modular, multi-layer relational database designed to support structural reuse of precast concrete elements across their entire value chain by capturing high-fidelity geometry, physical properties, and analysis-ready capacities. 

## Project Overview
The EU H2020 ReCreate project addresses the growing need for systematic tracking, digitisation, and sustainable reuse of deconstructed precast concrete elements, as an alternative to traditional non-circular practices. To cultivate the design of new structures using salvaged elements, an underlying data network storing and monitoring all relevant details is paramount. By deconstructing existing structures, cataloguing their geometry and reinforcement, and including capabilities to automate structural capacity estimations, the system provided in this repository enables informed reuse decisions and paves the way for detailed lifecycle assessments, cost analyses, and digital twins. 

## Database Structure
The relational database was built in MySQL and consists of three parallel schemas linked through ETL pipelines.

* Core Layer: Stores raw parametric data as universally machine-readable WKT for geometry and reinforcement, scalar information, and references custom taxonomies, metadata, material properties, quality management data, circularity information, LCA and LCC.  
*	Physical Layer: Mirrors core records and populates derived physical attributes from the parametric data (e.g., dimensions, volumes, masses, etc.) via a YAML-driven loader and Python formulas. 
*	Analysis Layer: Ingests derived physical properties and scalar core properties to compute structural capacities and other performance metrics via the same YAML loader system. Future extensions may include LCA, LCC, durability checks, etc.

A full overview of the database architecture and development can be read in our forthcoming journal article, which will be linked here once published. 

## Repository Layout

|— models/

|	|—core_model.mwb

|	|—phys_model.mwb

## CLI Loading Instructions
Data storage is managed through the unified cli.py script for all schemas. The core layer is the authoritative source where all new data must be loaded first. The Physical and Analysis layers are then semi-automatically populated from Core via mapped formulas and lookups.

To run cli.py, clone or download the whole directory from this repository to your local system. Next, open a terminal and navigate to the directory path for the downloaded package. The current data collection workflow includes XLSX templates for each element type, which are published on Zenodo (see Related Work). Run the following commands to load data from the Excel data templates into MySQL for each layer:

**1.	Core Layer**

Storage is order-sensitive to satisfy MySQL key constraints (parent-child). For the core layer, start by loading the material properties, then the site data, followed by the element-specific templates. 

python source/cli.py --host <HOST> --port <PORT> --user <USER> --password <PASSWORD> load-core --db element_database_core --element <ELEMENT> --file data/excel_file_path.xlsx
Replace all <ELEMENT> fields with the relevant element type being loaded (all lowercase): materials, site, wall, beam, column, slab, or hcs. Material libraries only need to be loaded once at the beginning. 

**2.	Physical Layer**

python source/cli.py --host <HOST> --port <PORT> --user <USER> --password <PASSWORD> load-phys --db_core element_database_core --db_phys element_database_phys --mapping configs/phys_map.yml --element <ELEMENT> 

**3.	Analysis Layer**

python source/cli.py --host <HOST> --port <PORT> --user <USER> --password <PASSWORD> load-anal --db_core element_database_core --db_phys element_database_phys --db_anal element_database_anal --mapping configs/anal_map.yml

Substitute all <> marked fields with the database characteristics defined when installing MySQL. 

## Dependencies

*	Python 3.9+
*	MySQL 8.0+
*	SQLAlchemy
*	pandas
*	numpy
*	Shapely 	              # for WKT parsing
*	mysql-connector-python

## Related Work
*	A complete accounting of the element database development and architecture is given in our accompanying journal article, currently under peer review, which will be linked once published. If this database is used in any future research or commercial applications, please cite the original authors and contributors. 
*	Historical material libraries for concrete and steel reinforcement specifications from the 20th century have been compiled for each of the four country clusters and can be accessed at the following repository: 
*	XLSX templates for data collection and a supporting guidelines report are available on Zenodo: 

## Data Availability
The datasets used to develop and validate the database described in the journal article originate from real-life deconstructed precast elements, which are proprietary commercial assets and cannot be publicly shared in full. Modified and anonymised datasets may be available upon request for demonstration and educational purposes. 

## Contact & Acknowledgements
If you have any questions or would like to reach out to the researchers, please contact:
Dr. Ben Matthews: b.j.m.matthews@tue.nl
Ir. Marcel Vullings: marcel.vullings@tno.nl

This project has received funding from the European Union’s Horizon 2020 research and innovation programme under Grant Agreement No 958200. 
Disclaimer: The content presented herein reflects the authors’ views. The European Commission is not responsible for any use that may be made of the information this publication contains. 

