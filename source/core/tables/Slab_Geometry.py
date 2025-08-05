# Import packages
import pandas as pd
from utils.functions import format_polygon, convert_to_3d_element, format_multipointz, format_tinz



# slab Geometry table data formatting function
def slab_geom_table(slabGeom_wksh):

    slab_elmt = []
    front_array = []; side_array = []; plan_array = []
    poly_array = []
    has_Void = []
    has_Connections = []

    # Find indices of all unique slab elements
    for index, rows in slabGeom_wksh.iterrows():
        if not pd.isnull(rows["Product ID"]):
            slab_elmt.append(index)
            
    # Iterate over the pairs of indices in elmt_index to derive geometry
    for i in range(len(slab_elmt) - 1):
        start_index = slab_elmt[i]
        end_index = slab_elmt[i + 1]

        # Create geometry arrays
        coords_xz = []
        coords_yz = []
        coords_xy = []
  

        for index in range(start_index, end_index):
            front_x, front_z = slabGeom_wksh.iloc[index, 4], slabGeom_wksh.iloc[index, 5]
            side_y, side_z = slabGeom_wksh.iloc[index, 7], slabGeom_wksh.iloc[index, 8]
            plan_x, plan_y = slabGeom_wksh.iloc[index, 10], slabGeom_wksh.iloc[index, 11]

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
    last_start_index = slab_elmt[-1]
    last_end_index = len(slabGeom_wksh) - 1

    # Create footprint polyline for the last element
    for index in range(last_start_index, last_end_index):
        front_x = slabGeom_wksh.iloc[index, 4]
        front_z = slabGeom_wksh.iloc[index, 5]
        side_y = slabGeom_wksh.iloc[index, 7]
        side_z = slabGeom_wksh.iloc[index, 8]
        plan_x = slabGeom_wksh.iloc[index, 10]
        plan_y = slabGeom_wksh.iloc[index, 11]

        if front_x is not None and plan_x is not None:
            last_coords_xz.append((front_x, front_z))
            last_coords_yz.append((side_y, side_z))
            last_coords_xy.append((plan_x, plan_y))
            # last_poly_points.append((plan_x, plan_y))

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
    slab_footprint = format_polygon(poly_array)

    # Convert lists to dataframes
    coords_XYZ = pd.DataFrame({"Coords_XYZ": coords_XYZ})
    shell_XYZ = pd.DataFrame({"Shell_XYZ": shell_XYZ})
    slab_footprint = pd.DataFrame({"FootprintPolyline": slab_footprint})


    # Create boolean dataframes for subtables
    for index in slab_elmt:
        # Void check
        void_count = slabGeom_wksh.iloc[index, 13]
        if pd.isnull(void_count) or (isinstance(void_count, (int, float)) and void_count == 0):
            void_check = False
        else:
            void_check = True
        has_Void.append(void_check)

        # Connection check
        conn_count = slabGeom_wksh.iloc[index, 17]
        if pd.isnull(conn_count) or (isinstance(conn_count, (int, float)) and conn_count == 0):
            conn_check = False
        else:
            conn_check = True
        has_Connections.append(conn_check)      

    has_Void = pd.DataFrame({"Has_Void": has_Void})
    has_Connections = pd.DataFrame({"Has_Connections": has_Connections})


    # Add raw data to pd
    slab_geom = slabGeom_wksh.iloc[:, [0, 1, 2, 25, 26, 27, 28]]
    slab_geom.columns = ["Product_ID", "Reinf_ID", "Count", "Concrete Strength Class", 
                         "Max Aggregate Size (mm)", "Concrete Type", "Notes"]
    slab_geom = slab_geom.dropna(subset=["Product_ID"]) # Drop all empty rows based on PK
    slab_geom.reset_index(drop=True, inplace=True) # Reset indices    

    # Concatenate dataframes
    slabGeom_rcds = pd.concat([slab_geom, coords_XYZ, shell_XYZ, slab_footprint, has_Connections, has_Void], axis=1)

    # Rearrange columns to match MySQL ordering
    slabGeom_rcds = slabGeom_rcds.loc[:, ["Product_ID", "Reinf_ID", "Count", 
                                            "Coords_XYZ", "Shell_XYZ", "FootprintPolyline",
                                            "Concrete Strength Class", "Concrete Type", "Max Aggregate Size (mm)",
                                            "Notes", "Has_Connections", "Has_Void"]]
    slabGeom_tuples = [tuple(row) for row in slabGeom_rcds.itertuples(index=False, name=None)]

    # Insert query
    slabGeom_insert = "INSERT INTO Slab_Geometry (Product_ID, Reinf_ID, Count, Coords_XYZ, Shell_XYZ, \
        FootprintPolyline, Strength_Class, Concrete_Type, Agg_Size, Notes, Has_Connections, Has_Void) \
            VALUES (%s, %s, %s, %s, %s, ST_GeomFromText(%s), %s, %s, %s, %s, %s, %s)"
    
    return (slabGeom_rcds, slabGeom_tuples, slabGeom_insert)