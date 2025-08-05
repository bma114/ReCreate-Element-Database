# Import packages
import pandas as pd
from utils.functions import convert_to_3d_element, format_multipointz, format_tinz, skip_empty_sheet


@skip_empty_sheet
# Wall Voids table data formatting function
def add_panels_table(wallPanel_wksh):

    wall_panels = []
    extpanel_front_array = []; extpanel_side_array = []; extpanel_plan_array = []
    rad_bev_array = []
    insul_front_array = []; insul_side_array = []; insul_plan_array = []

    # Find all panel indices
    for index, rows in wallPanel_wksh.iloc[2:].iterrows():
        if not pd.isnull(rows["Product ID"]):
            wall_panels.append(index)
            
    # Iterate over the pairs of indices in wall_panels to derive coordinate vectors
    for i in range(len(wall_panels) - 1):
        start_index = wall_panels[i]
        end_index = wall_panels[i + 1]

        # Create external panel geometry arrays
        extpanel_xz = []
        extpanel_yz = []
        extpanel_xy = []
        rad_bev_points = []
        
        for index in range(start_index, end_index):
            extf_x, extf_z = wallPanel_wksh.iloc[index, 2], wallPanel_wksh.iloc[index, 3]
            exts_y, exts_z = wallPanel_wksh.iloc[index, 5], wallPanel_wksh.iloc[index, 6]
            extp_x, extp_y = wallPanel_wksh.iloc[index, 8], wallPanel_wksh.iloc[index, 9]

            rad_bev_x = wallPanel_wksh.iloc[index, 4]
            rad_bev_y = wallPanel_wksh.iloc[index, 7]
            rad_bev_z = wallPanel_wksh.iloc[index, 10]
                    
            # Skip empty cells
            if extf_x is not None and extf_z is not None:
                extpanel_xz.append((extf_x, extf_z))
            if exts_y is not None and exts_z is not None:
                extpanel_yz.append((exts_y, exts_z))
            if extp_x is not None and extp_y is not None:
                extpanel_xy.append((extp_x, extp_y))
            if pd.notnull(rad_bev_x) or pd.notnull(rad_bev_y) or pd.notnull(rad_bev_z):    
                rad_bev_points.append((rad_bev_x, rad_bev_y, rad_bev_z))

        # Append to array
        extpanel_front_array.append(extpanel_xz)
        extpanel_side_array.append(extpanel_yz)
        extpanel_plan_array.append(extpanel_xy)

        if rad_bev_points:
            rad_bev_array.append(rad_bev_points)

        # Create insulation layer geometry arrays
        insul_xz = []
        insul_yz = []
        insul_xy = []
        
        for index in range(start_index, end_index):
            ins_f_x, ins_f_z = wallPanel_wksh.iloc[index, 12], wallPanel_wksh.iloc[index, 13]          
            ins_s_y, ins_s_z = wallPanel_wksh.iloc[index, 14], wallPanel_wksh.iloc[index, 15]
            ins_p_x, ins_p_y = wallPanel_wksh.iloc[index, 16], wallPanel_wksh.iloc[index, 17]
             
            # Skip empty cells
            if ins_f_x is not None and ins_f_z is not None:
                insul_xz.append((ins_f_x, ins_f_z))
            if ins_s_y is not None and ins_s_z is not None:
                insul_yz.append((ins_s_y, ins_s_z))
            if ins_p_x is not None and ins_p_y is not None:
                insul_xy.append((ins_p_x, ins_p_y))

        # Append to array only if points are not empty
        insul_front_array.append(insul_xz)
        insul_side_array.append(insul_yz)
        insul_plan_array.append(insul_xy)


    # Calculate geometry for the last element in the panel worksheet
    last_extpanel_xz = []; last_extpanel_yz = []; last_extpanel_xy = []
    last_rad_bev_points = []
    last_insul_xz = []; last_insul_yz = []; last_insul_xy = []
    last_start_index = wall_panels[-1]
    last_end_index = len(wallPanel_wksh) - 1

    # Extract geometry coordinates for the last element
    for index in range(last_start_index, last_end_index + 1):

        # Final external panel array
        extf_x, extf_z = wallPanel_wksh.iloc[index, 2], wallPanel_wksh.iloc[index, 3]
        exts_y, exts_z = wallPanel_wksh.iloc[index, 5], wallPanel_wksh.iloc[index, 6]
        extp_x, extp_y = wallPanel_wksh.iloc[index, 8], wallPanel_wksh.iloc[index, 9]

        rad_bev_x = wallPanel_wksh.iloc[index, 4]
        rad_bev_y = wallPanel_wksh.iloc[index, 7]
        rad_bev_z = wallPanel_wksh.iloc[index, 10]
            
        # Skip empty cells
        if extf_x is not None and extf_z is not None:
            last_extpanel_xz.append((extf_x, extf_z))
        if exts_y is not None and exts_z is not None:
            last_extpanel_yz.append((exts_y, exts_z))
        if extp_x is not None and extp_y is not None:
            last_extpanel_xy.append((extp_x, extp_y))
        if pd.notnull(rad_bev_x) or pd.notnull(rad_bev_y) or pd.notnull(rad_bev_z):    
            last_rad_bev_points.append((rad_bev_x, rad_bev_y, rad_bev_z))

        # Final insulation layer array
        ins_f_x, ins_f_z = wallPanel_wksh.iloc[index, 12], wallPanel_wksh.iloc[index, 13]
        ins_s_y,ins_s_z = wallPanel_wksh.iloc[index, 14], wallPanel_wksh.iloc[index, 15]
        ins_p_x,ins_p_y = wallPanel_wksh.iloc[index, 16], wallPanel_wksh.iloc[index, 17]      
            
        # Skip empty cells
        if ins_f_x is not None and ins_f_z is not None:
            last_insul_xz.append((ins_f_x, ins_f_z))
        if ins_s_y is not None and ins_s_z is not None:
            last_insul_yz.append((ins_s_y, ins_s_z))
        if ins_p_x is not None and ins_p_y is not None:
            last_insul_xy.append((ins_p_x, ins_p_y))

    extpanel_front_array.append(last_extpanel_xz)
    extpanel_side_array.append(last_extpanel_yz)
    extpanel_plan_array.append(last_extpanel_xy)
    rad_bev_array.append(last_rad_bev_points)
    insul_front_array.append(last_insul_xz)
    insul_side_array.append(last_insul_yz)
    insul_plan_array.append(last_insul_xy)

    # Convert 2D orthographic coordinates in 3D coordinates
    extpanel_3d_coords = convert_to_3d_element(extpanel_front_array, extpanel_side_array, extpanel_plan_array)
    insul_3d_coords = convert_to_3d_element(insul_front_array, insul_side_array, insul_plan_array)

    # Convert 3D coordinates into MULITPOINTZ
    panel_coords = format_multipointz(extpanel_3d_coords)
    rad_bev_XYZ = format_multipointz(rad_bev_array)
    insul_coords = format_multipointz(insul_3d_coords)

    # Convert 3D coordinates into TINZ
    panel_shell = format_tinz(extpanel_3d_coords)
    insul_shell = format_tinz(insul_3d_coords)

    # Convert lists to dataframes
    panel_coords = pd.DataFrame({"Panel_Coords_XYZ": panel_coords})
    panel_shell = pd.DataFrame({"Panel_Shell_XYZ": panel_shell})
    rad_bev_XYZ = pd.DataFrame({"Rad_Bev_XYZ": rad_bev_XYZ})
    insul_coords = pd.DataFrame({"Insul_Coords_XYZ": insul_coords})
    insul_shell = pd.DataFrame({"Insul_Shell_XYZ": insul_shell})

    # Add raw data to pd
    wall_panels = wallPanel_wksh.loc[:, ["Product ID", "Void", "External Finish", "Notes", "Linked Resources"]]
    wall_panels = wall_panels.dropna(subset=["Product ID"]) # Drop all empty rows based on PK
    wall_panels.reset_index(drop=True, inplace=True) # Reset indices
    wall_panels["Void"] = wall_panels["Void"].astype(bool) # Keep boolean formatting

    # Concatenate dataframes
    wall_panel_rcds = pd.concat([wall_panels, panel_coords, panel_shell, rad_bev_XYZ, insul_coords, insul_shell], axis=1)

    # Rearrange columns to match MySQL ordering
    wall_panel_rcds = wall_panel_rcds.loc[:, ["Product ID", "Void", "Panel_Coords_XYZ", "Panel_Shell_XYZ", "Rad_Bev_XYZ", "External Finish", 
                                              "Insul_Coords_XYZ", "Insul_Shell_XYZ", "Notes", "Linked Resources"]]
    wallPanel_tuples = [tuple(row) for row in wall_panel_rcds.itertuples(index=False, name=None)]

    # Insert query
    wallPanel_insert = "INSERT INTO Additional_Panelling (Product_ID, Has_Void, Panel_Coords_XYZ, Panel_Shell_XYZ, Rad_Bev_XYZ, \
        Design_Finish, Insul_Coords_XYZ, Insul_Shell_XYZ, Notes, Links) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    return (wall_panel_rcds, wallPanel_tuples, wallPanel_insert)