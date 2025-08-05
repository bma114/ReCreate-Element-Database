# Import packages
import pandas as pd
import numpy as np
from utils.functions import format_pointz, skip_empty_sheet

@skip_empty_sheet
def column_conns_table(columnGeom_wksh):
    column_elmt = []

    conn_data = columnGeom_wksh.iloc[2:, [0, 15, 16, 17, 18, 19, 20, 36]]
    conn_data.columns = ["Product_ID", "X", "Z", "Y", "Depth", "Diameter", "Connection_Type", "Notes"]

    # Find indices of all unique column elements
    for index, rows in columnGeom_wksh.iterrows():
        if not pd.isnull(rows["Product ID"]):
            column_elmt.append(index)

    # Fill all NaN values in Product_Type column with previous Product ID
    for i, start_index in enumerate(column_elmt):
        end_index = conn_data.index[-1] if i == len(column_elmt) - 1 else column_elmt[i + 1] - 1  # Ending index

        # Fill the gap between start_index and end_index with the most recent non-null value
        prev_value = None
        for index in range(start_index, end_index + 1):
            if pd.notnull(conn_data.loc[index, 'Product_ID']):
                prev_value = conn_data.loc[index, 'Product_ID']
            else:
                conn_data.loc[index, 'Product_ID'] = prev_value

    # For the final index in column_elmt, repeat the final non-null value until the end of conn_data
    final_index = column_elmt[-1]
    final_value = conn_data.loc[final_index, 'Product_ID']
    conn_data.loc[final_index + 1:, 'Product_ID'] = final_value

    # Create location strings
    conn_data['Position_XYZ'] = conn_data.apply(lambda row: (row['X'], row['Y'], row['Z']), axis=1)

    # Convert location coordinates into POINTZ format
    conn_data['Position_XYZ'] = format_pointz(conn_data['Position_XYZ'])


    # Drop all empty rows
    conn_data = conn_data.dropna(subset=["Connection_Type"]) # Drop all empty rows based on PK

    # Rearrange columns to match MySQL table order
    columnConn_rcds = conn_data.loc[:, ["Product_ID", "Connection_Type", "Position_XYZ", "Depth", "Diameter", "Notes"]]
    columnConn_tuples = [tuple(row) for row in columnConn_rcds.itertuples(index=False, name=None)]

    # Insert query
    columnConn_insert = "INSERT INTO Column_Connections (Product_ID, Connection_Type, Position_XYZ, Depth, Diameter, Notes) \
        VALUES (%s, %s, %s, %s, %s, %s)"
    
    return (columnConn_tuples, columnConn_insert)
