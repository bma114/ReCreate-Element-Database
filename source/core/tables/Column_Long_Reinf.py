# import connector and packages
import pandas as pd
import numpy as np
from utils.functions import format_polygon, format_linestr, skip_empty_sheet

@skip_empty_sheet
# Column Longitudinal Reinforcement table data formatting function
def column_longReinf_table(columnLongRF_wksh):

    lngReinf_data = columnLongRF_wksh.iloc[2:, [0, 2, 8, 9, 10, 11, 16, 17, 18, 19, 20, 35]]
    lngReinf_data.columns = ["Reinf_ID", "Zone_Plane", "Cover_X", "Cover_Z", "Cover_Y", "Confidence_Margin", 
                            "Layer_Start", "Num_Bars", "Bar_Diameter", "Bar_Spacing", 
                            "Steel_Grade", "Notes"]


    # Extract the minimum layer cover over all directions for storage (most likely uniform anyway)
    lngReinf_data["Min_Cover"] = lngReinf_data[["Cover_X", "Cover_Z", "Cover_Y"]].min(axis=1, skipna=True)

    # Create unqiue IDs
    zoneID = columnLongRF_wksh.iloc[2:, 0] + "_" + columnLongRF_wksh.iloc[2:, 1]
    layerID = zoneID + "_" + columnLongRF_wksh.iloc[2:, 7]

    # Create zone polygon coordinate array (H = horizontal, V = vertical) relative to chosen plane
    zone_cols = columnLongRF_wksh.iloc[2:, [3, 4, 5, 6]]
    zone_cols.columns = ["H1", "H2", "V1", "V2"]
    zone_coords = zone_cols.apply(lambda row: ((row['H1'], row['V1']), (row['H1'], row['V2']), 
                                (row['H2'], row['V2']), (row['H2'], row['V1'])), axis=1)

    # Reformat zone coordinates in POLYGON WKT format
    zone_polygon = format_polygon(zone_coords)

    # Create layer coordinate array (H = horizontal position, V = vertical position)
    layer_cols = columnLongRF_wksh.iloc[2:, [12, 13, 14, 15]]
    layer_cols.columns = ["H1", "H2", "V1", "V2"]
    layer_cols = layer_cols.astype(int) # Clean coordinates into integers
    layer_coords = layer_cols.apply(lambda row: ((row['H1'], row['V1']), (row['H2'], row['V2'])), axis=1)

    # Reformat layer coordinates in LINESTRING WKT format
    layer_linestr = []
    for index, row in layer_coords.items():

        linestr_wkt = format_linestr(row)
        layer_linestr.append(linestr_wkt)

    # Convert to DataFrames 
    zoneID = pd.DataFrame({"Zone_ID": zoneID})
    layerID = pd.DataFrame({"Layer_ID": layerID})    
    zone_polygon = pd.DataFrame({"Zone_Coords": zone_polygon})
    layer_linestr = pd.DataFrame({"Layer_Coords": layer_linestr})

    # Anchorage Type
    anchor_raw = columnLongRF_wksh.iloc[2:, [21]]
    anchor_type = pd.DataFrame(index=anchor_raw.index, columns=["Anchorage_Type"])

    # Reclassify the anchorage type based on function (Zone/Layer)
    for index, row in anchor_raw.iterrows():

        if pd.isnull(row.iloc[0]) or row.iloc[0] == "HAIRPIN":
            anchor_type.at[index, 'Anchorage_Type'] = "ZONE"
        elif row.iloc[0] == "NONE":
            anchor_type.at[index, 'Anchorage_Type'] = "NONE"
        else:
            anchor_type.at[index, 'Anchorage_Type'] = "LAYER"

    # Reset indices in all dataframes to match
    lngReinf_data.reset_index(drop=True, inplace=True)
    zoneID.reset_index(drop=True, inplace=True)
    layerID.reset_index(drop=True, inplace=True)
    anchor_type.reset_index(drop=True, inplace=True)

    # Concatenate dataframes
    columnLongRF_rcds = pd.concat([lngReinf_data, zoneID, layerID, zone_polygon, layer_linestr, anchor_type], axis=1)

    # Rearrange columns to match MySQL ordering
    columnLongRF_rcds = columnLongRF_rcds.loc[:, ["Reinf_ID", "Zone_ID", "Zone_Plane", "Zone_Coords", "Layer_ID", "Layer_Coords", "Layer_Start", 
                                              "Num_Bars", "Bar_Diameter", "Bar_Spacing", "Anchorage_Type", "Steel_Grade", 
                                              "Min_Cover", "Confidence_Margin", "Notes"]]
    columnLongRF_tuples = [tuple(row) for row in columnLongRF_rcds.itertuples(index=False, name=None)]

    # Insert query
    columnLongRF_insert = "INSERT INTO Column_Long_Reinf (Reinf_ID, Zone_ID, Zone_Plane, Zone_Coords, Layer_ID, Layer_Coords, Layer_Start, \
        Num_Bars, Bar_Diameter, Bar_Spacing, Anchorage_Type, Steel_Grade, Cover_Depth, Confidence_Margin, Notes) \
            VALUES (%s, %s, %s, ST_GeomFromText(%s), %s, ST_GeomFromText(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    return (columnLongRF_rcds, columnLongRF_tuples, columnLongRF_insert)