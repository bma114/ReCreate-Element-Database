# import connector and packages
import mysql.connector
import pandas as pd
import numpy as np

from core.tables.Wall_Element import wall_elmt_table
from core.tables.Wall_Geometry import wall_geom_table
from core.tables.Corbel_Geometry_Wall import corbel_geom_table
from core.tables.Wall_Voids import wall_voids_table
from core.tables.Additional_Panelling import add_panels_table
from core.tables.Wall_Connections import wall_conns_table
from core.tables.Wall_Long_Reinf import wall_longReinf_table
from core.tables.Zone_Anchorage_Wall import zone_anch_table
from core.tables.Layer_Anchorage_Wall import layer_anch_table
from core.tables.Wall_Transv_Reinf import wall_transvReinf_table


# Connect to server host
def load_wall(
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
    meta = pd.read_excel(file_path, sheet_name="Wall ID")
    geom = pd.read_excel(file_path, sheet_name="Geometry")
    panels = pd.read_excel(file_path, sheet_name="Extra Panels")
    longr = pd.read_excel(file_path, sheet_name="Long Reinf")
    transr= pd.read_excel(file_path, sheet_name="Transv Reinf")

    # Clean NaNs
    for df in (meta, geom, panels, longr, transr):
        df.replace({np.nan: None}, inplace=True)

    # Format records + SQL
    super_tups, super_insert, wallMeta_rcds, wallMeta_tups, wallMeta_insert = wall_elmt_table(meta)
    wallGeom_rcds, wallGeom_tups, wallGeom_insert = wall_geom_table(geom)
    wallCorb_rcds, corb_tups, corb_insert  = corbel_geom_table(geom, wallGeom_rcds)
    wallVoid_rcds, void_tups, void_insert = wall_voids_table(geom, wallGeom_rcds)
    panel_rcds, panel_tups, panel_insert = add_panels_table(panels)
    wallConn_tups, wallConn_insert = wall_conns_table(geom)
    wallLong_rcds, wallLong_tups, wallLong_insert = wall_longReinf_table(longr)
    zone_rcds, zone_tups, zone_insert = zone_anch_table(longr)
    layer_rcds, layer_tups, layer_insert = layer_anch_table(longr)
    wallTrnsvRF_rcds, wallTrans_tups, wallTrans_insert = wall_transvReinf_table(transr)

    # Toggle between 0/1 to turn off/on Foreign Key restrictions.
    cur.execute("SET FOREIGN_KEY_CHECKS=1;")

    # Bulk INSERT in the correct order
    for insert, tups in [
        (super_insert, super_tups),
        (wallGeom_insert, wallGeom_tups),
        (wallMeta_insert, wallMeta_tups),
        (corb_insert, corb_tups),
        (void_insert, void_tups),
        (panel_insert, panel_tups),
        (wallConn_insert, wallConn_tups),
        (wallLong_insert, wallLong_tups),
        (zone_insert, zone_tups),
        (layer_insert, layer_tups),
        (wallTrans_insert, wallTrans_tups),
    ]:
        if tups and insert:                              # only run if non‐empty
            cur.executemany(insert, tups)
    conn.commit()
    conn.close()