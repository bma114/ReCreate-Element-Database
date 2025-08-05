# Import packages
import pandas as pd
import numpy as np
from utils.functions import format_pointz, skip_empty_sheet

@skip_empty_sheet
def slab_conns_table(slabGeom_wksh):
    slab_elmt = []

    conn_data = slabGeom_wksh.iloc[2:, [0, 18, 19, 20, 21, 22, 23, 28]]
    conn_data.columns = ["Product_ID", "X", "Z", "Y", "Depth", "Diameter", "Connection_Type", "Notes"]

    # Find indices of all unique slab elements
    for index, rows in slabGeom_wksh.iterrows():
        if not pd.isnull(rows["Product ID"]):
            slab_elmt.append(index)

    # Fill all NaN values in Product_Type column with previous Product ID
    for i, start_index in enumerate(slab_elmt):
        end_index = conn_data.index[-1] if i == len(slab_elmt) - 1 else slab_elmt[i + 1] - 1  # Ending index

        # Fill the gap between start_index and end_index with the most recent non-null value
        prev_value = None
        for index in range(start_index, end_index + 1):
            if pd.notnull(conn_data.loc[index, 'Product_ID']):
                prev_value = conn_data.loc[index, 'Product_ID']
            else:
                conn_data.loc[index, 'Product_ID'] = prev_value

    # For the final index in slab_elmt, repeat the final non-null value until the end of conn_data
    final_index = slab_elmt[-1]
    final_value = conn_data.loc[final_index, 'Product_ID']
    conn_data.loc[final_index + 1:, 'Product_ID'] = final_value

    # Create location strings
    conn_data['Position_XYZ'] = conn_data.apply(lambda row: (row['X'], row['Y'], row['Z']), axis=1)

    # Convert location coordinates into POINTZ format
    conn_data['Position_XYZ'] = format_pointz(conn_data['Position_XYZ'])


    # Drop all empty rows
    conn_data = conn_data.dropna(subset=["Connection_Type"]) # Drop all empty rows based on PK

    # Rearrange columns to match MySQL table order
    slabConn_rcds = conn_data.loc[:, ["Product_ID", "Connection_Type", "Position_XYZ", "Depth", "Diameter", "Notes"]]
    slabConn_tuples = [tuple(row) for row in slabConn_rcds.itertuples(index=False, name=None)]

    # Insert query
    slabConn_insert = "INSERT INTO Slab_Connections (Product_ID, Connection_Type, Position_XYZ, Depth, Diameter, Notes) \
        VALUES (%s, %s, %s, %s, %s, %s)"
    
    return (slabConn_tuples, slabConn_insert)
