# Import packages
import pandas as pd
from utils.functions import format_polygon, convert_to_3d_element, format_multipointz, format_tinz



# Column Geometry table data formatting function
def column_geom_table(columnGeom_wksh):

    column_elmt = []
    front_array = []; side_array = []; plan_array = []
    rad_bev_array = []
    poly_array = []
    has_Connections = []
    has_Corbel = []

    # Find indices of all unique column elements
    for index, rows in columnGeom_wksh.iterrows():
        if not pd.isnull(rows["Product ID"]):
            column_elmt.append(index)
            
    # Iterate over the pairs of indices in elmt_index to derive geometry
    for i in range(len(column_elmt) - 1):
        start_index = column_elmt[i]
        end_index = column_elmt[i + 1]

        # Create geometry arrays
        coords_xz = []
        coords_yz = []
        coords_xy = []
        rad_bev_points = []      

        for index in range(start_index, end_index):
            front_x, front_z = columnGeom_wksh.iloc[index, 5], columnGeom_wksh.iloc[index, 6]
            side_y, side_z = columnGeom_wksh.iloc[index, 8], columnGeom_wksh.iloc[index, 9]
            plan_x, plan_y = columnGeom_wksh.iloc[index, 11], columnGeom_wksh.iloc[index, 12]

            rad_bev_x = columnGeom_wksh.iloc[index, 7]
            rad_bev_y = columnGeom_wksh.iloc[index, 10]
            rad_bev_z = columnGeom_wksh.iloc[index, 13]

            # Skip empty cells
            if pd.notnull(front_x) and pd.notnull(front_z):
                coords_xz.append( (front_x, front_z) )
            if pd.notnull(side_y) and pd.notnull(side_z):
                coords_yz.append( (side_y, side_z) )
            if pd.notnull(plan_x) and pd.notnull(plan_y):
                coords_xy.append( (plan_x, plan_y) )
            if pd.notnull(rad_bev_x) or pd.notnull(rad_bev_y) or pd.notnull(rad_bev_z):    
                rad_bev_points.append((rad_bev_x, rad_bev_y, rad_bev_z))

        front_array.append(coords_xz)
        side_array.append(coords_yz)
        plan_array.append(coords_xy)

        if rad_bev_points:
            rad_bev_array.append(rad_bev_points)

        # Append to poly_array only if poly_points is not empty
        if coords_xy:
            poly_ring = coords_xy + [coords_xy[0]] # Close the polygon
            poly_array.append(poly_ring)


    # Calculate geometry for the last element in the geometry worksheet
    last_coords_xz = []; last_coords_yz = []; last_coords_xy = []
    last_rad_bev_points = []
    last_start_index = column_elmt[-1]
    last_end_index = len(columnGeom_wksh) - 1

    # Create footprint polyline for the last element
    for index in range(last_start_index, last_end_index):
        front_x = columnGeom_wksh.iloc[index, 5]
        front_z = columnGeom_wksh.iloc[index, 6]
        side_y = columnGeom_wksh.iloc[index, 8]
        side_z = columnGeom_wksh.iloc[index, 9]
        plan_x = columnGeom_wksh.iloc[index, 11]
        plan_y = columnGeom_wksh.iloc[index, 12]

        rad_bev_x = columnGeom_wksh.iloc[index, 7]
        rad_bev_y = columnGeom_wksh.iloc[index, 10]
        rad_bev_z = columnGeom_wksh.iloc[index, 13]

        if front_x is not None and plan_x is not None:
            last_coords_xz.append((front_x, front_z))
            last_coords_yz.append((side_y, side_z))
            last_coords_xy.append((plan_x, plan_y))
            last_rad_bev_points.append((rad_bev_x, rad_bev_y, rad_bev_z))
            # last_poly_points.append((plan_x, plan_y))

    # Append the values for the last element to the respective lists
    front_array.append(last_coords_xz)
    side_array.append(last_coords_yz)
    plan_array.append(last_coords_xy)
    rad_bev_array.append(last_rad_bev_points)
    poly_array.append(last_coords_xy)

    # Convert 2D orthographic coordinates in 3D coordinates
    geom_coords = convert_to_3d_element(front_array, side_array, plan_array)

    # Convert 3D coordinates into MULITPOINTZ
    coords_XYZ = format_multipointz(geom_coords)

    # Convert radius or bevel coordinates into MULTIPOITNTZ
    rad_bev_XYZ = format_multipointz(rad_bev_array)

    # Convert 3D coordinates into TINZ
    shell_XYZ = format_tinz(geom_coords)

    # Convert footprintpolyline to POLYGON
    column_footprint = format_polygon(poly_array)

    # Convert lists to dataframes
    coords_XYZ = pd.DataFrame({"Coords_XYZ": coords_XYZ})
    shell_XYZ = pd.DataFrame({"Shell_XYZ": shell_XYZ})
    rad_bev_XYZ = pd.DataFrame({"Rad_Bev_XYZ": rad_bev_XYZ})
    column_footprint = pd.DataFrame({"FootprintPolyline": column_footprint})


    # Create boolean dataframes for subtables
    for index in column_elmt:
        # Connection check
        conn_count = columnGeom_wksh.iloc[index, 14]
        if pd.isnull(conn_count) or (isinstance(conn_count, (int, float)) and conn_count == 0):
            conn_check = False
        else:
            conn_check = True
        has_Connections.append(conn_check)

        # Corbel check
        corb_count = columnGeom_wksh.iloc[index, 21]
        if pd.isnull(corb_count) or (isinstance(corb_count, (int, float)) and corb_count == 0):
            corb_check = False
        else:
            corb_check = True
        has_Corbel.append(corb_check)        

    has_Connections = pd.DataFrame({"has_Connections": has_Connections})
    has_Corbel = pd.DataFrame({"has_Corbel": has_Corbel})


    # Add raw data to pd
    column_geom = columnGeom_wksh.iloc[:, [0, 1, 2, 3, 33, 34, 35, 36]]
    column_geom.columns = ["Product_ID", "Reinf_ID", "Cross-Section Type", "Count", 
                        "Concrete Strength Class", "Max Aggregate Size (mm)", "Concrete Type", "Notes"]
    column_geom = column_geom.dropna(subset=["Product_ID"]) # Drop all empty rows based on PK
    column_geom.reset_index(drop=True, inplace=True) # Reset indices
    

    # Concatenate dataframes
    columnGeom_rcds = pd.concat([column_geom, coords_XYZ, shell_XYZ, rad_bev_XYZ, column_footprint, has_Connections, has_Corbel], axis=1)

    # Rearrange columns to match MySQL ordering
    columnGeom_rcds = columnGeom_rcds.loc[:, ["Product_ID", "Reinf_ID", "Cross-Section Type", "Count", "Coords_XYZ", "Shell_XYZ", "Rad_Bev_XYZ", "FootprintPolyline",
                                            "Concrete Strength Class", "Concrete Type", "Max Aggregate Size (mm)", "Notes", "has_Connections", "has_Corbel"]]
    columnGeom_tuples = [tuple(row) for row in columnGeom_rcds.itertuples(index=False, name=None)]

    # Insert query
    columnGeom_insert = "INSERT INTO Column_geometry (Product_ID, Reinf_ID, Cross_Section, Count, Coords_XYZ, Rad_Bev_XYZ, Shell_XYZ, \
        FootprintPolyline, Strength_Class, Concrete_Type, Agg_Size, Notes, Has_Connections, Has_Corbel) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, ST_GeomFromText(%s), %s, %s, %s, %s, %s, %s)"
    
    return (columnGeom_rcds, columnGeom_tuples, columnGeom_insert)