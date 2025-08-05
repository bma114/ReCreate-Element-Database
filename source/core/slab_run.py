# import connector and packages
import mysql.connector
import pandas as pd
import numpy as np

from core.tables.Slab_Element import slab_elmt_table
from core.tables.Slab_Geometry import slab_geom_table
from core.tables.Slab_Voids import slab_voids_table
from core.tables.Slab_Connections import slab_conns_table
from core.tables.Slab_Long_Reinf import slab_longReinf_table
from core.tables.Zone_Anchorage_Slab import zone_anch_table
from core.tables.Layer_Anchorage_Slab import layer_anch_table
from core.tables.Slab_Transv_Reinf import slab_transvReinf_table

# Connect to server host
def load_slab(
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
    longr = pd.read_excel(file_path, sheet_name="Long Reinf")
    transr= pd.read_excel(file_path, sheet_name="Transv Reinf")

    # Clean NaNs
    for df in (meta, geom, longr, transr):
        df.replace({np.nan: None}, inplace=True)

    # Format records + SQL
    super_tups, super_insert, slabMeta_rcds, slabMeta_tups, slabMeta_insert = slab_elmt_table(meta)
    slabGeom_rcds, slabGeom_tups, slabGeom_insert = slab_geom_table(geom)
    slabVoid_rcds, void_tups, void_insert = slab_voids_table(geom, slabGeom_rcds)
    slabConn_tups, slabConn_insert = slab_conns_table(geom)
    slabLong_rcds, slabLong_tups, slabLong_insert = slab_longReinf_table(longr)
    zone_rcds, zone_tups, zone_insert = zone_anch_table(longr)
    layer_rcds, layer_tups, layer_insert = layer_anch_table(longr)
    slabTrnsvRF_rcds, slabTrans_tups, slabTrans_insert = slab_transvReinf_table(transr)

    # Toggle between 0/1 to turn off/on Foreign Key restrictions.
    cur.execute("SET FOREIGN_KEY_CHECKS=0;")

    # Bulk INSERT in the correct order
    for insert, tups in [
        (super_insert, super_tups),
        (slabGeom_insert, slabGeom_tups),
        (slabMeta_insert, slabMeta_tups),
        (void_insert, void_tups),
        (slabConn_insert, slabConn_tups),
        (slabLong_insert, slabLong_tups),
        (zone_insert, zone_tups),
        (layer_insert, layer_tups),
        (slabTrans_insert, slabTrans_tups),
    ]:
        if tups and insert:                             # only run if non‐empty
            cur.executemany(insert, tups)
    conn.commit()
    conn.close()