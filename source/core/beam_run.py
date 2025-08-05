# import connector and packages
import mysql.connector
import pandas as pd
import numpy as np

from core.tables.Beam_Element import beam_elmt_table
from core.tables.Beam_Geometry import beam_geom_table
from core.tables.Corbel_Geometry_Beam import corbel_geom_table
from core.tables.Beam_Connections import beam_conns_table
from core.tables.Beam_Long_Reinf import beam_longReinf_table
from core.tables.Zone_Anchorage_Beam import zone_anch_table
from core.tables.Layer_Anchorage_Beam import layer_anch_table
from core.tables.Beam_Transv_Reinf import beam_transvReinf_table


# Connect to server host
def load_beam(
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
    meta = pd.read_excel(file_path, sheet_name="Beam ID")
    geom = pd.read_excel(file_path, sheet_name="Geometry")
    longr = pd.read_excel(file_path, sheet_name="Long Reinf")
    transr= pd.read_excel(file_path, sheet_name="Transv Reinf")

    # Clean NaNs
    for df in (meta, geom, longr, transr):
        df.replace({np.nan: None}, inplace=True)

    # Format records + SQL
    super_tups, super_insert, beamMeta_rcds, beamMeta_tups, beamMeta_insert = beam_elmt_table(meta)
    beamGeom_rcds, beamGeom_tups, beamGeom_insert = beam_geom_table(geom)
    beamCorb_rcds, corb_tups, corb_insert  = corbel_geom_table(geom, beamGeom_rcds)
    beamConn_tups, beamConn_insert = beam_conns_table(geom)
    beamLong_rcds, beamLong_tups, beamLong_insert = beam_longReinf_table(longr)
    zone_rcds, zone_tups, zone_insert = zone_anch_table(longr)
    layer_rcds, layer_tups, layer_insert = layer_anch_table(longr)
    beamTrnsvRF_rcds, beamTrans_tups, beamTrans_insert = beam_transvReinf_table(transr)

    # Toggle between 0/1 to turn off/on Foreign Key restrictions.
    cur.execute("SET FOREIGN_KEY_CHECKS=1;")

    # Bulk INSERT in the correct order
    for insert, tups in [
        (super_insert, super_tups),
        (beamGeom_insert, beamGeom_tups),
        (beamMeta_insert, beamMeta_tups),
        (corb_insert, corb_tups),
        (beamConn_insert, beamConn_tups),
        (beamLong_insert, beamLong_tups),
        (zone_insert, zone_tups),
        (layer_insert, layer_tups),
        (beamTrans_insert, beamTrans_tups),
    ]:
        if tups and insert:                              # only run if non‐empty
            cur.executemany(insert, tups)
    conn.commit()
    conn.close()