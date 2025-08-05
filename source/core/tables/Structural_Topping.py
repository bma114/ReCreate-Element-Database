# import packages
import pandas as pd
import numpy as np
from utils.functions import skip_empty_sheet

@skip_empty_sheet
# HCS Structural Topping table data formatting function
def hcs_topping_table(hcsGeom_wksh):

    # Records to be inserted
    hcsTopping_data = hcsGeom_wksh.iloc[2:, [0, 15, 16, 17, 21]]
    hcsTopping_data.columns = ["Product_ID", "Thickness", "Mesh_Diameter", "Mesh_Spacing", "Notes"]
    hcsTopping_data.reset_index(drop=True, inplace=True) # Reset indices

    hcsTop_tuples = [tuple(row) for row in hcsTopping_data.itertuples(index=False, name=None)]

    # Insert query
    hcsTop_insert = "INSERT INTO structural_topping (Product_ID, Thickness, Mesh_Diameter, Mesh_Spacing, Notes) \
                VALUES (%s, %s, %s, %s, %s)"
    
    return (hcsTop_tuples, hcsTop_insert)