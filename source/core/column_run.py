# import connector and packages
import mysql.connector
import pandas as pd
import numpy as np

from core.tables.Column_Element import column_elmt_table
from core.tables.Column_Geometry import column_geom_table
from core.tables.Corbel_Geometry_Column import corbel_geom_table
from core.tables.Column_Connections import column_conns_table
from core.tables.Column_Long_Reinf import column_longReinf_table
from core.tables.Zone_Anchorage_Column import zone_anch_table
from core.tables.Layer_Anchorage_Column import layer_anch_table
from core.tables.Column_Transv_Reinf import column_transvReinf_table

# Connect to server host
def load_column(
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
    meta = pd.read_excel(file_path, sheet_name="Column ID")
    geom = pd.read_excel(file_path, sheet_name="Geometry")
    longr = pd.read_excel(file_path, sheet_name="Long Reinf")
    transr= pd.read_excel(file_path, sheet_name="Transv Reinf")

    # Clean NaNs
    for df in (meta, geom, longr, transr):
        df.replace({np.nan: None}, inplace=True)

    # Format records + SQL
    super_tups, super_insert, columnMeta_rcds, columnMeta_tups, columnMeta_insert = column_elmt_table(meta)
    columnGeom_rcds, columnGeom_tups, columnGeom_insert = column_geom_table(geom)
    columnCorb_rcds, corb_tups, corb_insert  = corbel_geom_table(geom, columnGeom_rcds)
    columnConn_tups, columnConn_insert = column_conns_table(geom)
    columnLong_rcds, columnLong_tups, columnLong_insert = column_longReinf_table(longr)
    zone_rcds, zone_tups, zone_insert = zone_anch_table(longr)
    layer_rcds, layer_tups, layer_insert = layer_anch_table(longr)
    columnTrnsvRF_rcds, columnTrans_tups, columnTrans_insert = column_transvReinf_table(transr)

    # Toggle between 0/1 to turn off/on Foreign Key restrictions.
    cur.execute("SET FOREIGN_KEY_CHECKS=1;")

    # Bulk INSERT in the correct order
    for insert, tups in [
        (super_insert, super_tups),
        (columnGeom_insert, columnGeom_tups),
        (columnMeta_insert, columnMeta_tups),
        (corb_insert, corb_tups),
        (columnConn_insert, columnConn_tups),
        (columnLong_insert, columnLong_tups),
        (zone_insert, zone_tups),
        (layer_insert, layer_tups),
        (columnTrans_insert, columnTrans_tups),
    ]:
        if tups and insert:                            # only run if non‐empty
            cur.executemany(insert, tups)
    conn.commit()
    conn.close()