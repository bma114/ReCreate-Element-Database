# import packages
import pandas as pd
import numpy as np
from utils.functions import format_point


# HCS Geometry table data formatting function
def hcs_geom_table(hcsGeom_wksh):

    # Records to be inserted
    hcsGeom_data = hcsGeom_wksh.iloc[2:, [0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 19, 20, 21]]
    hcsGeom_data.columns = ["Product_ID", "Reinf_ID", "Count", "Height", "Length", "Width", 
                            "Voids_Count", "D_X", "D_Y", "Cover_top", "Cover_Bottom", 
                            "Ext_Web_Thickness", "Strength_Class", "Agg_Size", "Notes"]
    hcsGeom_data.reset_index(drop=True, inplace=True) # Reset indices


    # Create void dimension WKT POINT (x, y)
    raw_void_coords = hcsGeom_data[["D_X", "D_Y"]].values.tolist() # Get raw coordinates
    wrapped_void_coords = [[(x, y)] for x, y in raw_void_coords]   # Wrap coordinates in POINT format
    void_diameter = [format_point(coord_list) for coord_list in wrapped_void_coords]

    # Calculate internal web thickness
    int_web = []
    for index, row in hcsGeom_data.iterrows():
        int_web_row = (row["Width"] - (row["Voids_Count"] * row["D_X"]) - 
                    (2 * row["Ext_Web_Thickness"])) / (row["Voids_Count"] - 1)
        int_web.append(round(int_web_row, 2))

    # Convert to dataframes and align indeces with hcsGeom_data
    void_diameter = pd.DataFrame({"Void_Diameter_XY": void_diameter})
    int_web = pd.DataFrame({"Int_Web_Thickness": int_web}, index=hcsGeom_data.index) 

    # Check for structural topping
    has_Topping = hcsGeom_wksh.iloc[2:, 14].astype(bool).astype(int)
    has_Topping = pd.DataFrame({"has_Topping": has_Topping.values}, index=hcsGeom_data.index
)

    # Concatenate dataframes
    hcsGeom_rcds = pd.concat([hcsGeom_data, void_diameter, int_web, has_Topping], axis=1)

    # Rearrange columns to match MySQL ordering
    hcsGeom_rcds = hcsGeom_rcds.loc[:, ["Product_ID", "Reinf_ID", "Count", "Height", "Length", "Width", 
                                        "Voids_Count", "Void_Diameter_XY", "Cover_top", "Cover_Bottom", 
                                        "Ext_Web_Thickness", "Int_Web_Thickness", "Strength_Class", 
                                        "Agg_Size", "Notes", "has_Topping"]]
    hcsGeom_tuples = [tuple(row) for row in hcsGeom_rcds.itertuples(index=False, name=None)]

    # Insert query
    hcsGeom_insert = "INSERT INTO HCS_geometry (Product_ID, Reinf_ID, Count, Height, Length, Width, \
        Voids_Count, Void_Diameter_XY, Cover_Top, Cover_Bottom, ExtWeb_Thickness, IntWeb_Thickness, \
            Strength_Class, Agg_Size, Notes, Has_Topping) \
                VALUES (%s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s), %s, %s, %s, %s, %s, %s, %s, %s)"
    
    return (hcsGeom_rcds, hcsGeom_tuples, hcsGeom_insert)

