import argparse
import sys
from sqlalchemy import create_engine
import yaml

# Import core loader functions
from core.wall_run import load_wall
from core.beam_run import load_beam
from core.column_run import load_column
from core.hcs_run import load_hcs
from core.slab_run import load_slab
from core.materials_run import load_materials
from core.site_run import load_site

from phys_loader import PhysLoader
from anal_loader import AnalysisLoader

def main():
    parser = argparse.ArgumentParser(
        description="Load Core, Phys, or Analysis layers into MySQL"
    )

    # Common DB/connection flags
    parser.add_argument("--host", required=True, help="MySQL host")
    parser.add_argument("--port", type=int, default=3306, help="MySQL port")
    parser.add_argument("--user", required=True, help="MySQL user")
    parser.add_argument("--password", required=True, help="MySQL password")

    sub = parser.add_subparsers(dest="cmd", required=True)

    # Load-core subcommand
    pc = sub.add_parser("load-core", help="Load spreadsheets into core schema")
    pc.add_argument("--element", choices=["wall","beam","column","slab","hcs","materials","site"], required=True, help="Which element to load")
    pc.add_argument("--file", required=True, help="Path to Excel file")
    pc.add_argument("--db", required=True, help="Core database name")

    # Load-phys subcommand
    pp = sub.add_parser("load-phys", help="Generate phys layer from core")
    pp.add_argument("--element", choices=["wall","beam","column","slab","hcs"], required=True, help="Which element to load")
    pp.add_argument("--db_core", required=True, help="Name of the core schema (e.g. element_database_core)")
    pp.add_argument("--db_phys", required=True, help="Name of the phys schema (e.g. element_database_phys)")
    pp.add_argument("--mapping",  default="configs/phys_map.yml", help="Path to phys_map.yml")

    # Load-analysis subcommand
    pa = sub.add_parser("load-anal", help="Generate analysis layer from core & phys")
    pa.add_argument("--db_core", required=True, help="Name of the core schema (e.g. element_database_core)")
    pa.add_argument("--db_phys", required=True, help="Name of the phys schema (e.g. element_database_phys)")
    pa.add_argument("--db_anal", required=True, help="Name of the analysis schema (e.g. element_database_anal)")
    pa.add_argument("--mapping", default="configs/anal_map.yml", help="Path to anal_map.yml")

    args = parser.parse_args()

    #  Dispatch logic
    if args.cmd == "load-core":
        common = (args.host, args.port, args.user, args.password, args.db)
        {
            "wall":      lambda: load_wall(args.file, *common),
            "beam":      lambda: load_beam(args.file, *common),
            "column":    lambda: load_column(args.file, *common),
            "slab":      lambda: load_slab(args.file, *common),
            "hcs":       lambda: load_hcs(args.file, *common),
            "materials": lambda: load_materials(args.file, *common),
            "site":      lambda: load_site(args.file, *common),
        }[args.element]()

    elif args.cmd == "load-phys":
        # Build engines
        core_url = (f"mysql+mysqlconnector://{args.user}:{args.password}" f"@{args.host}:{args.port}/{args.db_core}")
        phys_url = (f"mysql+mysqlconnector://{args.user}:{args.password}" f"@{args.host}:{args.port}/{args.db_phys}")
        core_engine = create_engine(core_url)       
        phys_engine = create_engine(phys_url)

        loader = PhysLoader(core_engine, phys_engine, args.mapping, args.element)
        loader.run()

    else:  # load-analysis
        core_url = f"mysql+mysqlconnector://{args.user}:{args.password}@{args.host}:{args.port}/{args.db_core}"
        phys_url = f"mysql+mysqlconnector://{args.user}:{args.password}@{args.host}:{args.port}/{args.db_phys}"
        anal_url = f"mysql+mysqlconnector://{args.user}:{args.password}@{args.host}:{args.port}/{args.db_anal}"
        core_engine = create_engine(core_url)
        phys_engine = create_engine(phys_url)
        anal_engine = create_engine(anal_url)

        loader = AnalysisLoader(core_engine, phys_engine, anal_engine, args.mapping)
        loader.run()

if __name__ == "__main__":
    main()

