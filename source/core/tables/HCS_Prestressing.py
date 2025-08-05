# import packages
import pandas as pd
import numpy as np
import math
from utils.functions import format_point, skip_empty_sheet


@skip_empty_sheet
# HCS Prestressing table data formatting function
def hcs_prestress_table(hcsPrestr_wksh, hcsGeom_wksh):

    hcsPrestr_data = hcsPrestr_wksh.loc[1:, ["Reinf ID", "Strand ID", "Layer Num", "Num Wires","Strand Diameter (mm)", "Steel Grade", "Notes"]]
    hcsPrestr_data.reset_index(drop=True, inplace=True) # Reset indices

    # Define slab height from Geometry table
    hcs_geom = hcsGeom_wksh.iloc[2:, [1, 4]]
    hcs_geom.columns = ["Reinf_ID", "Height"]
    hcs_geom.reset_index(drop=True, inplace=True) # Reset indices

    # Create a dictionary for the heights to map
    height_dict = dict(zip(hcs_geom["Reinf_ID"], hcs_geom["Height"]))

    # Map the 'Height' values from hcs_geom to hcsPrestr_data based on 'Reinf ID'
    hcsPrestr_data["Height"] = hcsPrestr_data["Reinf ID"].map(height_dict)

    # Ensure we only add 'Height' values up to the length of hcsPrestr_data
    hcsPrestr_data = hcsPrestr_data.iloc[:len(hcsPrestr_data)]

    # Create coordinatre arrays
    p_x = hcsPrestr_wksh.iloc[1:, 3]
    p_x.reset_index(drop=True, inplace=True) # Reset indices
    p_y = hcsPrestr_wksh.iloc[1:, 4]
    p_y.reset_index(drop=True, inplace=True) # Reset indices

    # Create coordinate WKT POINT (x, y)
    prestr_coords = pd.concat([p_x, p_y], axis=1).values.tolist()
    wrapped_coords = [[(x, y)] for x, y in prestr_coords]     # Wrap coordinates in POINT format
    prestr_coords = [format_point(coord_list) for coord_list in wrapped_coords]
    prestr_coords = pd.DataFrame({"Strand_Coord_XY": prestr_coords})


    # Concatenate dataframes
    hcsPrestr_rcds = pd.concat([hcsPrestr_data, prestr_coords], axis=1)

    # Rearrange columns to match MySQL ordering
    hcsPrestr_rcds = hcsPrestr_rcds.loc[:, ["Strand ID", "Reinf ID", "Layer Num", "Strand_Coord_XY",
                                        "Num Wires", "Strand Diameter (mm)", "Steel Grade", "Notes"]]
    hcsPrestr_tuples = [tuple(row) for row in hcsPrestr_rcds.itertuples(index=False, name=None)]

    # Insert query
    hcsPrestr_insert = "INSERT INTO HCS_Prestressing (Strand_ID, Reinf_ID, Layer_Num, Strand_Coord_XY, \
        Num_Wires, Strand_Diameter, Steel_Grade, Notes) \
                VALUES (%s, %s, %s, ST_GeomFromText(%s), %s, %s, %s, %s)"
    
    return (hcsPrestr_rcds, hcsPrestr_tuples, hcsPrestr_insert)