# import connector and packages
import mysql.connector
import pandas as pd
import numpy as np

from core.tables.HCS_Element import hcs_elmt_table
from core.tables.HCS_Geometry import hcs_geom_table
from core.tables.Structural_Topping import hcs_topping_table
from core.tables.HCS_Connections import hcs_conns_table
from core.tables.HCS_Prestressing import hcs_prestress_table


# Connect to server host
def load_hcs(
    file_path: str,
    host: str, port: int,
    user: str, password: str,
    database: str
):
    
    # Connect
    conn = mysql.connector.connect(
        host=host, port=port,
        user=user, password=password,
        database=database
    )
    cur = conn.cursor()

    # Read the sheets
    meta = pd.read_excel(file_path, sheet_name="Slab ID")
    geom = pd.read_excel(file_path, sheet_name="Geometry")
    conns = pd.read_excel(file_path, sheet_name="Connections")
    prestr = pd.read_excel(file_path, sheet_name="Prestressing")

    # Clean NaNs
    for df in (meta, geom, conns, prestr):
        df.replace({np.nan: None}, inplace=True)

    # Format records + SQL
    super_tups, super_insert, hcsMeta_rcds, hcsMeta_tuples, hcsMeta_insert = hcs_elmt_table(meta)  # Slab Element table
    hcsGeom_rcds, hcsGeom_tuples, hcsGeom_insert = hcs_geom_table(geom)                            # HCS Geometry table
    hcsTop_tuples, hcsTop_insert = hcs_topping_table(geom)                                         # HCS Structural Topping table
    hcsConn_rcds, hcsConn_tuples, hcsConn_insert = hcs_conns_table(conns)                          # HCS Connections table
    hcsPrestr_rcds, hcsPrestr_tuples, hcsPrestr_insert = hcs_prestress_table(prestr, geom)         # HCS Prestressing table

    # Toggle between 0/1 to turn off/on Foreign Key restrictions.
    cur.execute("SET FOREIGN_KEY_CHECKS=0;")

    # Bulk INSERT in the correct order
    for insert, tups in [
        (super_insert, super_tups),
        (hcsGeom_insert, hcsGeom_tuples),
        (hcsMeta_insert, hcsMeta_tuples),
        (hcsTop_insert, hcsTop_tuples),
        (hcsConn_insert, hcsConn_tuples),
        (hcsPrestr_insert, hcsPrestr_tuples),
    ]:
        if tups and insert:                             # only run if non‐empty
            cur.executemany(insert, tups)
    conn.commit()
    conn.close()