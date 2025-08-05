# import connector and packages
import pandas as pd
import numpy as np
import uuid
from utils.functions import format_point

# Beam Element table data formatting function
def beam_elmt_table(beamMeta_wksh):

    element_id = []
    for id in range(len(beamMeta_wksh)):
        # Generate a unique ID for each element
        element_id.append(str(uuid.uuid4()))

    element_type = ['Beam'] * len(beamMeta_wksh)

    # Convert to dataframes
    element_id = pd.DataFrame({"Element_ID": element_id})
    element_type = pd.DataFrame({"Element_Type": element_type})

    # Records to be inserted into Element_Super table
    beamSuper_rcds = pd.concat([element_id, element_type], axis=1)
    beamSuper_tuples = [tuple(row) for row in beamSuper_rcds.itertuples(index=False, name=None)]
    
    # Records to be inserted (no manipulation required)
    beamMeta_rcds = beamMeta_wksh.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]]
    beamMeta_rcds.columns = ["Beam_ID", "Building_ID", "Product_ID", "Reinf_ID", "Beam_Type", "Wing", "Floor_Num", 
                             "Grid_Position", "Coating Layer", "Status", "Has Tests", "Has Damage", "Intervention Class", 
                             "Storage Lat", "Storage Long", "Notes"]
    
    # Create Lat-Long POINT string for storage location
    coords = beamMeta_rcds[["Storage Lat", "Storage Long",]]
    coord_points = [ format_point([(row["Storage Lat"], row["Storage Long"])]) for _, row in coords.iterrows() ]
    
    # Insert element_ID and coord_points into beamMeta_rcds
    beamMeta_rcds.insert(0, "Element_ID", element_id)
    beamMeta_rcds.insert(11, "Storage Location", coord_points)
    beamMeta_rcds = beamMeta_rcds.drop(columns=["Storage Lat", "Storage Long"])

    # Rearrange columns to match MySQL ordering
    beamMeta_rcds = beamMeta_rcds.loc[:, ["Element_ID", "Beam_ID", "Building_ID", "Product_ID", "Reinf_ID", "Beam_Type", "Wing", "Floor_Num", 
                                          "Grid_Position", "Coating Layer", "Status", "Intervention Class", "Storage Location",  "Notes", "Has Tests", "Has Damage"]]

    beamMeta_tuples = [tuple(row) for row in beamMeta_rcds.itertuples(index=False, name=None)]

    # Element_Super insert query
    beamSuper_insert = """INSERT INTO Element_Super (Element_ID, Element_Type) VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE Element_Type = VALUES(Element_Type)"""


    # Insert query
    beamMeta_insert = "INSERT INTO beam_element (Element_ID, Beam_ID, Building_ID, Product_ID, Reinf_ID, Beam_Type, Wing, Floor_Num, \
        Grid_Pos, Coating_Protection, Status, Intervention_Class, Location, Notes, Has_Tests, Has_Damage) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s), %s, %s, %s)"
    
    # beamMeta_insert = """
    # INSERT INTO beam_element (
    #     Element_ID, Beam_ID, Building_ID, Product_ID, Reinf_ID, Beam_Type, Wing, Floor_Num, 
    #     Grid_Pos, Coating_Protection, Status, Intervention_Class, Location, Notes, Has_Tests, Has_Damage
    # ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s), %s, %s, %s)
    # ON DUPLICATE KEY UPDATE
    #     Building_ID         = VALUES(Building_ID),
    #     Product_ID          = VALUES(Product_ID),
    #     Reinf_ID            = VALUES(Reinf_ID),
    #     Beam_Type           = VALUES(Beam_Type),
    #     Wing                = VALUES(Wing),
    #     Floor_Num           = VALUES(Floor_Num),
    #     Grid_Pos            = VALUES(Grid_Pos),
    #     Coating_Protection  = VALUES(Coating_Protection),
    #     Status              = VALUES(Status),
    #     Intervention_Class  = VALUES(Intervention_Class),
    #     Location            = VALUES(Location),
    #     Notes               = VALUES(Notes);
    #     Has_Tests           = VALUES(Has_Tests),
    #     Has_Damage          = VALUES(Has_Damage)
    # """
    
    return (beamSuper_tuples, beamSuper_insert, beamMeta_rcds, beamMeta_tuples, beamMeta_insert)