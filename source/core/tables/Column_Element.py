# import connector and packages
import pandas as pd
import numpy as np
import uuid
from utils.functions import format_point


# Column Element table data formatting function
def column_elmt_table(columnMeta_wksh):

    element_id = []
    for id in range(len(columnMeta_wksh)):
        # Generate a unique ID for each element
        element_id.append(str(uuid.uuid4()))

    element_type = ['Column'] * len(columnMeta_wksh)

    # Convert to dataframes
    element_id = pd.DataFrame({"Element_ID": element_id})
    element_type = pd.DataFrame({"Element_Type": element_type})

    # Records to be inserted into Element_Super table
    columnSuper_rcds = pd.concat([element_id, element_type], axis=1)
    columnSuper_tuples = [tuple(row) for row in columnSuper_rcds.itertuples(index=False, name=None)]
    
    # Records to be inserted (no manipulation required)
    columnMeta_rcds = columnMeta_wksh.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]]
    columnMeta_rcds.columns = ["Column_ID", "Building_ID", "Product_ID", "Reinf_ID", "Column_Type", "Wing", "Floor_Num", 
                               "Grid_Position", "Coating Layer", "Status", "Has Tests", "Has Damage", "Intervention Class",
                                "Storage Lat", "Storage Long", "Notes"]
    
    # Create Lat-Long POINT string for storage location
    coords = columnMeta_rcds[["Storage Lat", "Storage Long",]]
    coord_points = [ format_point([(row["Storage Lat"], row["Storage Long"])]) for _, row in coords.iterrows() ]
    
    # Insert element_ID and coord_points into columnMeta_rcds
    columnMeta_rcds.insert(0, "Element_ID", element_id)
    columnMeta_rcds.insert(11, "Storage Location", coord_points)
    columnMeta_rcds = columnMeta_rcds.drop(columns=["Storage Lat", "Storage Long"])

    # Rearrange columns to match MySQL ordering
    columnMeta_rcds = columnMeta_rcds.loc[:, ["Element_ID", "Column_ID", "Building_ID", "Product_ID", "Reinf_ID", "Column_Type", "Wing", "Floor_Num", 
                                          "Grid_Position", "Coating Layer", "Status", "Intervention Class", "Storage Location",  "Notes", "Has Tests", "Has Damage"]]

    columnMeta_tuples = [tuple(row) for row in columnMeta_rcds.itertuples(index=False, name=None)]

    # Element_Super insert query
    columnSuper_insert = "INSERT INTO Element_Super (Element_ID, Element_Type) VALUES (%s, %s)"

    # Insert query
    columnMeta_insert = "INSERT INTO Column_element (Element_ID, Column_ID, Building_ID, Product_ID, Reinf_ID, \
        Column_Type, Wing, Floor_Num, Grid_Pos, Coating_Protection, Status, Intervention_Class, Location, Notes, Has_Tests, Has_Damage) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s), %s, %s, %s)"
    
    return (columnSuper_tuples, columnSuper_insert, columnMeta_rcds, columnMeta_tuples, columnMeta_insert)