# import connector and packages
import pandas as pd
import numpy as np
import uuid
from utils.functions import format_point

# slab Element table data formatting function
def slab_elmt_table(slabMeta_wksh):

    element_id = []
    for id in range(len(slabMeta_wksh)):
        # Generate a unique ID for each element
        element_id.append(str(uuid.uuid4()))

    element_type = ['Slab'] * len(slabMeta_wksh)

    # Convert to dataframes
    element_id = pd.DataFrame({"Element_ID": element_id})
    element_type = pd.DataFrame({"Element_Type": element_type})

    # Records to be inserted into Element_Super table
    slabSuper_rcds = pd.concat([element_id, element_type], axis=1)
    slabSuper_tuples = [tuple(row) for row in slabSuper_rcds.itertuples(index=False, name=None)]
    
    # Records to be inserted (no manipulation required)
    slabMeta_rcds = slabMeta_wksh.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]]
    slabMeta_rcds.columns = ["Slab_ID", "Building_ID", "Product_ID", "Reinf_ID", "Slab_Type", "Wing", "Floor_Num", 
                             "Grid_Position", "Coating Layer", "Status", "Has Tests", "Has Damage", "Intervention Class", 
                             "Storage Lat", "Storage Long", "Notes"]
    
    # Create Lat-Long POINT string for storage location
    coords = slabMeta_rcds[["Storage Lat", "Storage Long",]]
    coord_points = [ format_point([(row["Storage Lat"], row["Storage Long"])]) for _, row in coords.iterrows() ]

    # Insert element_ID and coord_points into slabMeta_rcds
    slabMeta_rcds.insert(0, "Element_ID", element_id)
    slabMeta_rcds.insert(11, "Storage Location", coord_points)
    slabMeta_rcds = slabMeta_rcds.drop(columns=["Storage Lat", "Storage Long"])

    # Rearrange columns to match MySQL ordering
    slabMeta_rcds = slabMeta_rcds.loc[:, ["Element_ID", "Slab_ID", "Building_ID", "Product_ID", "Reinf_ID", "Slab_Type", "Wing", "Floor_Num", 
                                          "Grid_Position", "Coating Layer", "Status", "Intervention Class", "Storage Location",  "Notes", "Has Tests", "Has Damage"]]

    slabMeta_tuples = [tuple(row) for row in slabMeta_rcds.itertuples(index=False, name=None)]

    # Element_Super insert query
    slabSuper_insert = "INSERT INTO Element_Super (Element_ID, Element_Type) VALUES (%s, %s)"

    # Insert query
    slabMeta_insert = "INSERT INTO Slab_element (Element_ID, Slab_ID, Building_ID, Slab_Product_ID, Reinf_ID, \
        Slab_Type, Wing, Floor_Num, Grid_Pos, Coating_Protection, Status, Intervention_Class, Location, Notes, Has_Tests, Has_Damage) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s), %s, %s, %s)"
    
    return (slabSuper_tuples, slabSuper_insert, slabMeta_rcds, slabMeta_tuples, slabMeta_insert)