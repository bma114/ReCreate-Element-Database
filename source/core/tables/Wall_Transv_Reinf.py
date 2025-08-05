# import connector and packages
import pandas as pd
import numpy as np
from utils.functions import create_shape_arrays, format_multipointzm, skip_empty_sheet

@skip_empty_sheet
# Wall Longitudinal Reinforcement table data formatting function
def wall_transvReinf_table(wallTrnvRF_wksh):

    # Create unqiue zone ID
    zoneID_T = wallTrnvRF_wksh.iloc[1:, 0] + "_" + wallTrnvRF_wksh.iloc[1:, 1]
    zoneID_T = pd.DataFrame({"Zone_ID": zoneID_T})
    zoneID_T = zoneID_T.dropna() # Drop all empty rows
    zoneID_T.reset_index(drop=True, inplace=True)


    # Find indices of all unique reinforcement designs
    reinf_index = []
    for index, rows in wallTrnvRF_wksh.iterrows():
        if not pd.isnull(rows["Reinf ID"]):
            reinf_index.append(index)


    # Call function that creates arrays of shape coordinates
    shape_array = create_shape_arrays(wallTrnvRF_wksh, reinf_index)
    shape_array = format_multipointzm(shape_array)
    shape_coords = pd.DataFrame({"Shape_Coords": shape_array}).astype(str)


    # Spanned length array - e.g. (x1, x2)
    span_cols = wallTrnvRF_wksh.iloc[1:, [13, 14]]
    span_cols.columns = ["Start", "End"]
    span_cols = span_cols.dropna() # Drop all empty rows

    span_points = span_cols.apply(lambda row: (row['Start'], row['End']), axis=1)
    span_points = pd.DataFrame({"Spanned_Length": span_points}).astype(str)
    span_points.reset_index(drop=True, inplace=True)


    # Import raw transverse reinforcement data
    trvReinf_data = wallTrnvRF_wksh.iloc[1:, [0, 3, 4, 5, 6, 7, 12, 15, 17]]
    trvReinf_data.columns = ["Reinf_ID", "Description", "Diameter", "Spacing", "Num_Bends", 
                            "Bent_Plane", "Span_Axis", "Steel_Grade", "Notes"]
    trvReinf_data = trvReinf_data.dropna(subset=["Reinf_ID"]) # Drop all empty rows
    trvReinf_data.reset_index(drop=True, inplace=True) # Reset indices

    # Concatenate dataframes
    wallTrnsvRF_rcds = pd.concat([trvReinf_data, zoneID_T, shape_coords, span_points], axis=1)

    # Rearrange columns to match MySQL ordering
    wallTrnsvRF_rcds = wallTrnsvRF_rcds.loc[:, ["Reinf_ID", "Zone_ID", "Description", "Bent_Plane", "Num_Bends", 
                                            "Shape_Coords", "Span_Axis", "Spanned_Length", "Spacing", "Diameter", "Steel_Grade", "Notes"]]
    wallTrnsvRF_tuples = [tuple(row) for row in wallTrnsvRF_rcds.itertuples(index=False, name=None)]

    # Insert query
    wallTrnsvRF_insert = "INSERT INTO Wall_Transv_Reinf (Reinf_ID, Zone_ID, Description, Bent_Plane, Num_Bends, \
        Shape_Coords, Span_Axis, Spanned_Length, Spacing, Bar_Diameter, Steel_Grade, Notes) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    return (wallTrnsvRF_rcds, wallTrnsvRF_tuples, wallTrnsvRF_insert)