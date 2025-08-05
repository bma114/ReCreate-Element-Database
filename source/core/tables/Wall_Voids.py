# Import packages
import pandas as pd
import numpy as np
from utils.functions import format_multipointz, format_tinz, skip_empty_sheet


@skip_empty_sheet
# Wall Voids table data formatting function
def wall_voids_table(wallGeom_wksh, wallGeom_rcds):

    void_indices = []
    void_array = []

    # Find all void indices (different to wall indices)
    for index, rows in wallGeom_wksh.iloc[2:].iterrows():
        if not pd.isnull(rows.iloc[15]) and rows.iloc[15] != 0:
            void_indices.append(index)

    # Add raw data to pd
    void_data = wallGeom_wksh.iloc[:, [0, 42]]
    void_data.columns = ["Product_ID", "Notes"]
    void_data = void_data.loc[void_indices,:]
    void_data.reset_index(drop=True, inplace=True) # Reset indices

    # Fill all empty Product ID's with the previous ID (for walls with more than one void)
    last_prodID = None
    for index, row in void_data.iterrows():
        if pd.isnull(row["Product_ID"]):
            void_data.at[index, "Product_ID"] = last_prodID
        else:
            last_prodID = row["Product_ID"]

    # Iterate over the void indices to derive geometric properties
    for i in range(len(void_indices) - 1):
        start_index = void_indices[i]
        end_index = void_indices[i + 1]

        # Create coordinate array
        void_points = []
        for index in range(start_index, end_index):
            x = wallGeom_wksh.iloc[index, 16]
            y = wallGeom_wksh.iloc[index, 18]
            z = wallGeom_wksh.iloc[index, 17]

            # Skip empty cells
            if x is not None and z is not None and y is not None:
                void_points.append((x, y, z))

        # Append to void_array only if void_points is not empty
        if void_points:
            void_array.append(void_points)

    # Determine records for the last element in the geometry worksheet
    last_start_index = void_indices[-1]
    last_end_index = len(wallGeom_wksh) - 1

    # Find void coordinates for the last element
    last_void_points = []
    for index in range(last_start_index, last_end_index):
        x = wallGeom_wksh.iloc[index, 16]
        y = wallGeom_wksh.iloc[index, 18]
        z = wallGeom_wksh.iloc[index, 17]

        if x is not None and z is not None and y is not None:
            last_void_points.append((x, y, z))

    # Append the values for the last element to the respective lists
    void_array.append(last_void_points)

    # Convert 3D void coordinates into MULITPOINTZ
    void_coords = format_multipointz(void_array)

    # Convert 3D coordinates into TINZ
    void_shell = format_tinz(void_array)

    # Convert lists to dataframes
    void_coords = pd.DataFrame({"Void_Coords_XYZ": void_coords})
    void_shell = pd.DataFrame({"Void_Shell_XYZ": void_shell})

    # Concatenate dataframes
    wallVoid_rcds = pd.concat([void_data, void_coords, void_shell], axis=1)

    # Rearrange columns to match MySQL ordering
    wallVoid_rcds = wallVoid_rcds.loc[:, ["Product_ID", "Void_Coords_XYZ", "Void_Shell_XYZ", "Notes"]]

    # Drop all rows that have null coordinates (walls with no voids)
    wallVoid_rcds.replace({"": np.nan, " ": np.nan}, inplace=True)
    wallVoid_rcds = wallVoid_rcds.dropna(subset=["Void_Coords_XYZ"])

    wallVoid_tuples = [tuple(row) for row in wallVoid_rcds.itertuples(index=False, name=None)]

    # Insert query
    wallVoid_insert = "INSERT INTO wall_voids (Product_ID, Void_Coords_XYZ, Void_Shell_XYZ, Notes) \
            VALUES (%s, %s, %s, %s)"
    
    return (wallVoid_rcds, wallVoid_tuples, wallVoid_insert)