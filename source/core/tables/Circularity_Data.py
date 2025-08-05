# import packages
import pandas as pd
import numpy as np



# circulstruction Site Data table data formatting function
def circul_data_table(siteData_wksh):

    # Records to be inserted
    circul_data = siteData_wksh.iloc[2:, [0, 19, 20, 21, 22, 23, 24]]
    circul_data.columns = ["Building_ID", "Num_Facades", "Num_Internal_Walls", "Num_Columns", "Num_Beams", 
                        "Num_HCS", "Num_Solid_Slabs"]
    circul_data = circul_data.dropna(subset=["Building_ID"]) # Drop all empty rows based on PK
    circul_data.reset_index(drop=True, inplace=True)

    # Ensure numeric (coerce any stray non-numeric → NaN)
    facades = pd.to_numeric(circul_data["Num_Facades"], errors="coerce")
    internal = pd.to_numeric(circul_data["Num_Internal_Walls"],errors="coerce")
    hcs = pd.to_numeric(circul_data["Num_HCS"], errors="coerce")
    solid = pd.to_numeric(circul_data["Num_Solid_Slabs"], errors="coerce")

    # Calculate Num_Walls and Num_Slabs
    circul_data["Num_Walls"] = (facades.fillna(0) + internal.fillna(0)).astype(int)
    circul_data["Num_Slabs"] = (hcs.fillna(0) + solid.fillna(0)).astype(int)

    # Rearrange columns to match MySQL ordering
    circulData_rcds = circul_data[["Building_ID", "Num_Walls", "Num_Columns", "Num_Beams", "Num_Slabs"]]
    circul_tuples = [tuple(row) for row in circulData_rcds.itertuples(index=False, name=None)]

    # Insert query
    circulData_insert = "INSERT INTO Circularity_Data (Building_ID, Num_Walls, Num_Columns, Num_Beams, Num_Floor_Slabs) \
            VALUES (%s, %s, %s, %s, %s)"

    return (circul_tuples, circulData_insert)