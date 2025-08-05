# import packages
import pandas as pd
import numpy as np
from utils.functions import skip_empty_sheet

@skip_empty_sheet
# HCS Connections table data formatting function
def hcs_conns_table(hcsConn_wksh):

    conn_index = []
    pos_SW = []
    pos_LW = []
    pos_SS = []

    hcsConn_data = hcsConn_wksh.iloc[2:, [0, 1, 3, 5, 7, 10]]
    hcsConn_data.columns = ["Product_ID", "Reinf_ID", "Shear_Wall", 
                            "Longitundal_Wall", "Shear_Slab", "Notes"]

    # Find indices of all unique product ID's (connection records)
    for index, rows in hcsConn_data.iterrows():
        if not pd.isnull(rows["Product_ID"]):
            conn_index.append(index)

    conn_index.append(len(hcsConn_wksh)) # Append last index

    # Iterate over indices in conn_index to derive position arrays
    for i in range(len(conn_index) - 1):
        start_index = conn_index[i]
        end_index = conn_index[i + 1]

        # Create arrays
        shear_wall = hcsConn_wksh.iloc[start_index:end_index, 4].dropna().to_list()
        long_wall = hcsConn_wksh.iloc[start_index:end_index, 6].dropna().to_list()
        shear_slab = hcsConn_wksh.iloc[start_index:end_index, 8].dropna().to_list()

        pos_SW.append(shear_wall)
        pos_LW.append(long_wall)
        pos_SS.append(shear_slab)
        

    # Convert to dataframes
    position_SW = pd.DataFrame({"Position_SW": pos_SW}).astype(str)
    position_LW = pd.DataFrame({"Position_LW": pos_LW}).astype(str)
    position_SS = pd.DataFrame({"Position_SS": pos_SS}).astype(str)


    # Format raw data
    hcsConn_data = hcsConn_data.dropna(subset=["Product_ID"]) # Drop all empty rows based on PK
    hcsConn_data.reset_index(drop=True, inplace=True) # Reset indices


    # Concatenate dataframes
    hcsConn_rcds = pd.concat([hcsConn_data, position_SW, position_LW, position_SS], axis=1)

    # Rearrange columns to match MySQL ordering
    hcsConn_rcds = hcsConn_rcds.loc[:, ["Product_ID", "Reinf_ID", "Shear_Wall", "Position_SW",
                                        "Longitundal_Wall", "Position_LW", "Shear_Slab", 
                                        "Position_SS", "Notes"]]
    hcsConn_tuples = [tuple(row) for row in hcsConn_rcds.itertuples(index=False, name=None)]

    # Insert query
    hcsConn_insert = "INSERT INTO HCS_connections (Product_ID, Reinf_ID, Shear_to_Wall, Position_SW, \
        Longitudinal_to_Wall, Position_LW, Shear_to_Slab, Position_SS, Notes) \
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    return (hcsConn_rcds, hcsConn_tuples, hcsConn_insert)