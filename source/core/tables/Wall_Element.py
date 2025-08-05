# import connector and packages
import pandas as pd
import numpy as np
import uuid
from utils.functions import format_point

# Wall Element table data formatting function
def wall_elmt_table(wallMeta_wksh):

    element_id = []
    for id in range(len(wallMeta_wksh)):
        # Generate a unique ID for each element
        element_id.append(str(uuid.uuid4()))

    element_type = ['Wall'] * len(wallMeta_wksh)

    # Convert to dataframes
    element_id = pd.DataFrame({"Element_ID": element_id})
    element_type = pd.DataFrame({"Element_Type": element_type})

    # Records to be inserted into Element_Super table
    wallSuper_rcds = pd.concat([element_id, element_type], axis=1)
    wallSuper_tuples = [tuple(row) for row in wallSuper_rcds.itertuples(index=False, name=None)]

    # Records to be inserted into Wall_Element table (no manipulation required)
    wallMeta_rcds = wallMeta_wksh.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]]
    wallMeta_rcds.columns = ["Wall_ID", "Building_ID", "Product_ID", "Reinf_ID", "Wall_Type", "Wing", "Floor_Num", 
                             "Orientation", "Grid_Pos", "Coating_Protection", "Status", "Has Tests", "Has Damage", 
                             "Intervention Class", "Storage Lat", "Storage Long",  "Notes"]

    # Create Lat-Long POINT string for storage location
    coords = wallMeta_rcds[["Storage Lat", "Storage Long",]]
    coord_points = [ format_point([(row["Storage Lat"], row["Storage Long"])]) for _, row in coords.iterrows() ]
    
    # Insert element_ID and coord_points into wallMeta_rcds
    wallMeta_rcds.insert(0, "Element_ID", element_id)
    wallMeta_rcds.insert(12, "Location", coord_points)
    wallMeta_rcds = wallMeta_rcds.drop(columns=["Storage Lat", "Storage Long"])

    # Rearrange columns to match MySQL ordering
    wallMeta_rcds = wallMeta_rcds.loc[:, ["Element_ID", "Wall_ID", "Building_ID", "Product_ID", "Reinf_ID", "Wall_Type", "Wing", "Floor_Num", 
                                          "Orientation", "Grid_Pos", "Coating_Protection", "Status", "Intervention Class", 
                                          "Location",  "Notes", "Has Tests", "Has Damage"]]

    wallMeta_tuples = [tuple(row) for row in wallMeta_rcds.itertuples(index=False, name=None)]

    # Element_Super insert query
    wallSuper_insert = "INSERT INTO Element_Super (Element_ID, Element_Type) VALUES (%s, %s)"

    # Wall_Element insert query
    wallMeta_insert = "INSERT INTO Wall_element (Element_ID, Wall_ID, Building_ID, Product_ID, Reinf_ID, Wall_Type, Wing, \
        Floor_Num, Orientation, Grid_Pos, Coating_Protection, Status, Intervention_Class, Location, Notes, Has_Tests, Has_Damage) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s), %s, %s, %s)"
    
    return (wallSuper_tuples, wallSuper_insert, wallMeta_rcds, wallMeta_tuples, wallMeta_insert)