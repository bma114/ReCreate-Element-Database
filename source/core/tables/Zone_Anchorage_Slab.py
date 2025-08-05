# import connector and packages
import pandas as pd
import numpy as np
from utils.functions import skip_empty_sheet

@skip_empty_sheet
# Zone Anchorage table for slab longitudinal reinforcement -- data formatting function
def zone_anch_table(slabLongRF_wksh):

    anchor_indices = []
    bent_angles = []
    zoneID_anch = []

    zone_anch_data = slabLongRF_wksh.iloc[2:, [26, 29, 30, 31, 32, 36]]
    zone_anch_data.columns =["Anchorage_Type", "Diameter", "Spacing", 
                            "Num_Pins", "Pin_Span", "Notes"]


    # Find all anchorage indices
    for index, rows in zone_anch_data.iterrows():
        anchorage_type = rows["Anchorage_Type"]
        if isinstance(anchorage_type, str) and "HAIRPIN" in anchorage_type:
            anchor_indices.append(index)

    # Create unqiue IDs
    for index in anchor_indices:
        zoneID = slabLongRF_wksh.iloc[index, 0] + "_" + slabLongRF_wksh.iloc[index, 1]
        zoneID_anch.append(zoneID)
        
    zoneID_anch = pd.DataFrame({"Zone_ID": zoneID_anch})

    # Create bent_angle lists
    for i in range(len(anchor_indices) - 1):
        start_index = anchor_indices[i]
        end_index = anchor_indices[i + 1]
        
        # Extract Bent Angles
        bentAngle_vals = slabLongRF_wksh.iloc[start_index:end_index, 27].values
        
        # Append the values to arrays_list as an array
        bent_angles.append(tuple(bentAngle_vals))

    # Extract final record from worksheet
    last_index = anchor_indices[-1]
    bentAngle_last = slabLongRF_wksh.iloc[last_index:, 27].values
    bent_angles.append(tuple(bentAngle_last))

    # Filter out tuples containing None values
    bent_angles_cleaned = [tuple(filter(None, angle_tuple)) for angle_tuple in bent_angles]
    bent_angles_cleaned = [(angle[0] if len(angle) == 1 else angle) for angle in bent_angles_cleaned] # remove trailing comma

    bent_angles = pd.DataFrame({"Bent_Angle": bent_angles_cleaned}).astype(str)


    # Drop all empty rows from worksheet
    zone_anch_data = zone_anch_data.dropna(subset=["Anchorage_Type"])
    zone_anch_data.reset_index(drop=True, inplace=True)

    # Concatenate dataframes
    zone_anch_rcds = pd.concat([zone_anch_data, zoneID_anch, bent_angles], axis=1)

    # Rearrange columns to match MySQL ordering
    zone_anch_rcds = zone_anch_rcds.loc[:, ["Zone_ID", "Anchorage_Type", "Bent_Angle", "Diameter", "Spacing", 
                                            "Num_Pins", "Pin_Span", "Notes"]]
    zone_anch_tuples = [tuple(row) for row in zone_anch_rcds.itertuples(index=False, name=None)]

    # Insert query
    zone_anch_insert = "INSERT INTO Zone_Anchorage (Slab_Zone_ID, Anchorage_Type, Bent_Angle, Diameter, Spacing, \
        Num_Pins, Span, Notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    
    return (zone_anch_rcds, zone_anch_tuples, zone_anch_insert)