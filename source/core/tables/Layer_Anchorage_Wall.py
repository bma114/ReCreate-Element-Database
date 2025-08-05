# import connector and packages
import pandas as pd
import numpy as np
from utils.functions import skip_empty_sheet

@skip_empty_sheet
# Layer Anchorage table for wall longitudinal reinforcement -- data formatting function
def layer_anch_table(wallLongRF_wksh):

    anchor_indices = []
    layerID_anch = []

    layer_anch_data = wallLongRF_wksh.iloc[2:, [21, 22, 23, 24, 25, 26]]
    layer_anch_data.columns =["Anchorage_Type", "Angle_1", "Angle_2", 
                            "Hook_Length_1", "Hook_Length_2", "Notes"]

    # Find all anchorage indices
    for index, rows in layer_anch_data.iterrows():
        if not pd.isnull(rows["Anchorage_Type"]):
            anchor_indices.append(index)

    # Create unqiue IDs
    for index in anchor_indices:
        layerID = wallLongRF_wksh.iloc[index, 0] + "_" + wallLongRF_wksh.iloc[index, 1] + "_" + wallLongRF_wksh.iloc[index, 7]
        layerID_anch.append(layerID)


    # Remove empty rows and reset indices
    layer_anch_data = layer_anch_data.dropna(subset=["Anchorage_Type"])
    layer_anch_data.reset_index(drop=True, inplace=True)


    # Create (bent angle, bent length) arrays
    anchorage_start = layer_anch_data.apply(lambda row: ((row['Angle_1'], row['Hook_Length_1'])), axis=1) # left or bottom end.
    anchorage_end = layer_anch_data.apply(lambda row: ((row['Angle_2'], row['Hook_Length_2'])), axis=1) # left or bottom end.

    # Convert to dataframes
    layerID_anch = pd.DataFrame({"Layer_ID": layerID_anch})
    anchorage_start = pd.DataFrame({"Anchorage_Start": anchorage_start}).astype(str)
    anchorage_end = pd.DataFrame({"Anchorage_End": anchorage_end}).astype(str)


    # Concatenate dataframes
    layer_anch_rcds = pd.concat([layer_anch_data, layerID_anch, anchorage_start, anchorage_end], axis=1)

    # Rearrange columns to match MySQL ordering
    layer_anch_rcds = layer_anch_rcds.loc[:, ["Layer_ID", "Anchorage_Type", "Anchorage_Start", "Anchorage_End", "Notes"]]
    layer_anch_tuples = [tuple(row) for row in layer_anch_rcds.itertuples(index=False, name=None)]

    # Insert query
    layer_anch_insert = "INSERT INTO Layer_Anchorage (Wall_Layer_ID, Anchorage_Type, Anchor_Start, Anchor_End, Notes) \
        VALUES (%s, %s, %s, %s, %s)"
    
    return(layer_anch_rcds, layer_anch_tuples, layer_anch_insert)