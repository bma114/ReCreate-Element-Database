# Import packages
import pandas as pd
from utils.functions import format_polygon, convert_to_3d_element, format_multipointz, format_tinz



# Beam Geometry table data formatting function
def beam_geom_table(beamGeom_wksh):

    beam_elmt = []
    front_array = []; side_array = []; plan_array = []
    poly_array = []
    has_Connections = []
    has_Corbel = []

    # Find indices of all unique beam elements
    for index, rows in beamGeom_wksh.iterrows():
        if not pd.isnull(rows["Product ID"]):
            beam_elmt.append(index)
            
    # Iterate over the pairs of indices in elmt_index to derive geometry
    for i in range(len(beam_elmt) - 1):
        start_index = beam_elmt[i]
        end_index = beam_elmt[i + 1]

        # Create geometry arrays
        coords_xz = []
        coords_yz = []
        coords_xy = []    

        for index in range(start_index, end_index):
            front_x, front_z = beamGeom_wksh.iloc[index, 5], beamGeom_wksh.iloc[index, 6]
            side_y, side_z = beamGeom_wksh.iloc[index, 8], beamGeom_wksh.iloc[index, 9]
            plan_x, plan_y = beamGeom_wksh.iloc[index, 11], beamGeom_wksh.iloc[index, 12]

            # Skip empty cells
            if pd.notnull(front_x) and pd.notnull(front_z):
                coords_xz.append( (front_x, front_z) )
            if pd.notnull(side_y) and pd.notnull(side_z):
                coords_yz.append( (side_y, side_z) )
            if pd.notnull(plan_x) and pd.notnull(plan_y):
                coords_xy.append( (plan_x, plan_y) )

        front_array.append(coords_xz)
        side_array.append(coords_yz)
        plan_array.append(coords_xy)

        # Append to poly_array only if poly_points is not empty
        if coords_xy:
            poly_ring = coords_xy + [coords_xy[0]] # Close the polygon
            poly_array.append(poly_ring)


    # Calculate geometry for the last element in the geometry worksheet
    last_coords_xz = []; last_coords_yz = []; last_coords_xy = []
    last_start_index = beam_elmt[-1]
    last_end_index = len(beamGeom_wksh) - 1

    # Create footprint polyline for the last element
    for index in range(last_start_index, last_end_index):
        front_x = beamGeom_wksh.iloc[index, 5]
        front_z = beamGeom_wksh.iloc[index, 6]
        side_y = beamGeom_wksh.iloc[index, 8]
        side_z = beamGeom_wksh.iloc[index, 9]
        plan_x = beamGeom_wksh.iloc[index, 11]
        plan_y = beamGeom_wksh.iloc[index, 12]

        if front_x is not None and plan_x is not None:
            last_coords_xz.append((front_x, front_z))
            last_coords_yz.append((side_y, side_z))
            last_coords_xy.append((plan_x, plan_y))

    # Append the values for the last element to the respective lists
    front_array.append(last_coords_xz)
    side_array.append(last_coords_yz)
    plan_array.append(last_coords_xy)
    poly_array.append(last_coords_xy)

    # Convert 2D orthographic coordinates in 3D coordinates
    geom_coords = convert_to_3d_element(front_array, side_array, plan_array)

    # Convert 3D coordinates into MULITPOINTZ
    coords_XYZ = format_multipointz(geom_coords)

    # Convert 3D coordinates into TINZ
    shell_XYZ = format_tinz(geom_coords)

    # Convert footprintpolyline to POLYGON
    beam_footprint = format_polygon(poly_array)

    # Convert lists to dataframes
    coords_XYZ = pd.DataFrame({"Coords_XYZ": coords_XYZ})
    shell_XYZ = pd.DataFrame({"Shell_XYZ": shell_XYZ})
    beam_footprint = pd.DataFrame({"FootprintPolyline": beam_footprint})


    # Create boolean dataframes for subtables
    for index in beam_elmt:
        # Connection check
        conn_count = beamGeom_wksh.iloc[index, 14]
        if pd.isnull(conn_count) or (isinstance(conn_count, (int, float)) and conn_count == 0):
            conn_check = False
        else:
            conn_check = True
        has_Connections.append(conn_check)

        # Corbel check
        corb_count = beamGeom_wksh.iloc[index, 21]
        if pd.isnull(corb_count) or (isinstance(corb_count, (int, float)) and corb_count == 0):
            corb_check = False
        else:
            corb_check = True
        has_Corbel.append(corb_check)        

    has_Connections = pd.DataFrame({"has_Connections": has_Connections})
    has_Corbel = pd.DataFrame({"has_Corbel": has_Corbel})


    # Add raw data to pd
    beam_geom = beamGeom_wksh.iloc[:, [0, 1, 2, 3, 33, 34, 35, 36]]
    beam_geom.columns = ["Product_ID", "Reinf_ID", "Mirrored", "Count", 
                        "Concrete Strength Class", "Max Aggregate Size (mm)", "Concrete Type", "Notes"]
    beam_geom = beam_geom.dropna(subset=["Product_ID"]) # Drop all empty rows based on PK
    beam_geom.reset_index(drop=True, inplace=True) # Reset indices
    

    # Concatenate dataframes
    beamGeom_rcds = pd.concat([beam_geom, coords_XYZ, shell_XYZ, beam_footprint, has_Connections, has_Corbel], axis=1)

    # Rearrange columns to match MySQL ordering
    beamGeom_rcds = beamGeom_rcds.loc[:, ["Product_ID", "Reinf_ID", "Mirrored", "Count", 
                                            "Coords_XYZ", "Shell_XYZ", "FootprintPolyline",
                                            "Concrete Strength Class", "Concrete Type", "Max Aggregate Size (mm)",
                                            "Notes", "has_Connections", "has_Corbel"]]
    beamGeom_tuples = [tuple(row) for row in beamGeom_rcds.itertuples(index=False, name=None)]

    # Insert query
    beamGeom_insert = """
    INSERT INTO Beam_geometry (Product_ID, Reinf_ID, Mirrored, Count, Coords_XYZ,
        Shell_XYZ, FootprintPolyline, Strength_Class, Concrete_Type, Agg_Size, Notes, Has_Connections, Has_Corbel)
        VALUES (%s, %s, %s, %s, %s, %s, ST_GeomFromText(%s), %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        Reinf_ID            = VALUES(Reinf_ID),
        Mirrored            = VALUES(Mirrored),
        Count               = VALUES(Count),
        Coords_XYZ          = VALUES(Coords_XYZ),
        Shell_XYZ           = VALUES(Shell_XYZ),
        FootprintPolyline   = VALUES(FootprintPolyline),
        Strength_Class      = VALUES(Strength_Class),
        Concrete_Type       = VALUES(Concrete_Type),
        Agg_Size            = VALUES(Agg_Size),
        Notes               = VALUES(Notes),
        Has_Connections     = VALUES(Has_Connections),
        Has_Corbel          = VALUES(Has_Corbel);
    """
    
    return (beamGeom_rcds, beamGeom_tuples, beamGeom_insert)