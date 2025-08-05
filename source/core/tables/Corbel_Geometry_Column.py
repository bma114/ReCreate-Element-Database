# Import packages
import pandas as pd
from utils.functions import format_multipointz, format_tinz, convert_to_3d_element, skip_empty_sheet

@skip_empty_sheet
# Column-Corbel Geometry table data formatting function
def corbel_geom_table(columnGeom_wksh, columnGeom_rcds):

    corb_indices = []
    corb_front = []; corb_side = []; corb_plan = []
    extruded_plane = []
 
    # Find all corbel indices (each element could have multiple corbels)
    for idx in range(2, len(columnGeom_wksh)):
        val = columnGeom_wksh.iloc[idx, 21]
        if pd.notnull(val) and val != 0:
            corb_indices.append(idx)

    # Extract raw data from worksheet
    corb_data = columnGeom_wksh.loc[2:, ["Product ID", "Notes"]]
    corb_data = corb_data.loc[corb_indices,:]
    corb_data.reset_index(drop=True, inplace=True) # Reset indices

    # Fill all empty Product ID's with the previous ID (for columns with more than one corbel)
    last_prodID = None
    for index, row in corb_data.iterrows():
        if pd.isnull(row["Product ID"]):
            corb_data.at[index, "Product ID"] = last_prodID
        else:
            last_prodID = row["Product ID"]


    # Calculate corbel geometrical properties
    for i in range(len(corb_indices) - 1):
        start_index = corb_indices[i]
        end_index = corb_indices[i + 1]

        # Get the extrusion plane for the current corbel
        plane = columnGeom_wksh.iloc[start_index, 22]

        # Create geometry arrays
        coords_xz = []
        coords_yz = []
        coords_xy = []        

        for index in range(start_index, end_index):
            front_x, front_z = columnGeom_wksh.iloc[index, 23], columnGeom_wksh.iloc[index, 24]
            side_y, side_z = columnGeom_wksh.iloc[index, 26], columnGeom_wksh.iloc[index, 27]
            plan_x, plan_y = columnGeom_wksh.iloc[index, 29], columnGeom_wksh.iloc[index, 30]            

            # Skip empty cells
            if pd.notnull(front_x) and pd.notnull(front_z):
                coords_xz.append( (front_x, front_z) )
            if pd.notnull(side_y) and pd.notnull(side_z):
                coords_yz.append( (side_y, side_z) )
            if pd.notnull(plan_x) and pd.notnull(plan_y):
                coords_xy.append( (plan_x, plan_y) )

        # Extrude the remaining 2D plane.
        if plane == "XZ":
            # We have side and plan, need to infer front 
            x_side = sorted({x for x, _ in coords_xy})
            z_side = sorted({z for _, z in coords_yz})
            coords_xz = [(x, z) for x in x_side for z in z_side]

        elif plane == "XY":
            # We have front and plan, need to infer side 
            y_side = sorted({y for y, _ in coords_xy})
            z_side = sorted({z for _, z in coords_xz})
            coords_yz = [(y, z) for y in y_side for z in z_side]

        # else:
            # raise ValueError(f"Unexpected Extrusion Plane: {plane!r}")

        corb_front.append(coords_xz)
        corb_side.append(coords_yz)
        corb_plan.append(coords_xy)
        extruded_plane.append(plane)
            
                
    # Calculate corbel geometry for last entry in the worksheet
    last_corb_front, last_corb_side, last_corb_plan = [], [], []
    last_start_index = corb_indices[-1]
    last_end_index = len(columnGeom_wksh) - 1
    last_plane = columnGeom_wksh.iloc[start_index, 22]

    for index in range(last_start_index, last_end_index):
        front_x, front_z = columnGeom_wksh.iloc[index, 23], columnGeom_wksh.iloc[index, 24]
        side_y, side_z = columnGeom_wksh.iloc[index, 26], columnGeom_wksh.iloc[index, 27]
        plan_x, plan_y = columnGeom_wksh.iloc[index, 29], columnGeom_wksh.iloc[index, 30]
        
        # Skip empty cells
        if pd.notnull(front_x) and pd.notnull(front_z):
            last_corb_front.append( (front_x, front_z) )
        if pd.notnull(side_y) and pd.notnull(side_z):
            last_corb_side.append( (side_y, side_z) )
        if pd.notnull(plan_x) and pd.notnull(plan_y):
            last_corb_plan.append( (plan_x, plan_y) )

    # Extrude the remaining 2D plane.
    if plane == "XZ":
        # We have side and plan, need to infer front 
        x_side = sorted({x for x, _ in last_corb_plan})
        z_side = sorted({z for _, z in last_corb_side})
        last_corb_front = [(x, z) for x in x_side for z in z_side]

    elif plane == "XY":
        # We have front and plan, need to infer side 
        y_side = sorted({y for y, _ in last_corb_plan})
        z_side = sorted({z for _, z in last_corb_front})
        last_corb_side = [(y, z) for y in y_side for z in z_side]

    # else:
    #     raise ValueError(f"Unexpected Extrusion Plane: {plane!r}")

    # Append the last corbel geometry to the respective lists
    corb_front.append(last_corb_front)
    corb_side.append(last_corb_side)
    corb_plan.append(last_corb_plan)
    extruded_plane.append(last_plane)

    # Convert 2D orthographic coordinates in 3D coordinate attributes
    corb_3d_coords = convert_to_3d_element(corb_front, corb_side, corb_plan)
    coords_XYZ = format_multipointz(corb_3d_coords)
    shell_XYZ = format_tinz(corb_3d_coords)

    # Convert lists to dataframes
    extruded_plane = pd.DataFrame({"Extruded_Plane": extruded_plane})
    coords_XYZ = pd.DataFrame({"Corb_Coords_XYZ": coords_XYZ})
    shell_XYZ = pd.DataFrame({"Shell_XYZ": shell_XYZ})

    # Concatenate dataframes
    column_corb_rcds = pd.concat([corb_data, extruded_plane, coords_XYZ, shell_XYZ], axis=1)

    # Rearrange columns to match MySQL ordering
    column_corb_rcds = column_corb_rcds.loc[:, ["Product ID", "Extruded_Plane", "Corb_Coords_XYZ", "Shell_XYZ", "Notes"]]
    corb_tuples = [tuple(row) for row in column_corb_rcds.itertuples(index=False, name=None)]

    # Insert query
    corb_insert = "INSERT INTO Corbel_Geometry (Column_Product_ID, Extruded_Plane, Corb_Coords_XYZ, Shell_XYZ, Notes) \
          VALUES (%s, %s, %s, %s, %s)"
    
    return (column_corb_rcds, corb_tuples, corb_insert)