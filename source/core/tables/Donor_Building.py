# import packages
import pandas as pd
import numpy as np
from utils.functions import format_point



# Donor Buidling Metadata table data formatting function
def donor_building_table(siteData_wksh):

    # Records to be inserted (no manipulation required)
    site_data = siteData_wksh.iloc[2:, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 27]]
    site_data.columns = ["Building_ID", "Name", "Building_Type", "Latitude", "Longitude", "Country", "City", 
                         "Construction", "Deconstruction", "Deconstruction_Company", "Consequence_Class", "Exposure_Class", 
                            "Floor_Area", "Num_Wings", "Notes"]
    site_data = site_data.dropna(subset=["Building_ID"]) # Drop all empty rows based on PK
    site_data.reset_index(drop=True, inplace=True)

    # Create Lat-Long POINT string
    coords = site_data[["Latitude", "Longitude"]]
    coords = coords.apply(lambda row: ((row['Latitude'], row['Longitude'])), axis=1)
    coord_points = format_point(coords)


    # Create Num_Storeys array
    last_index = siteData_wksh.index[-1]
    storeys = siteData_wksh.iloc[2 : last_index + 1, 15].values

    storeys_str = [str(x) for x in storeys]
    storey_array = "(" + ", ".join(storeys_str) + ")"


    # Convert to dataframes
    coord_points = pd.DataFrame({"Coords_LatLong": [coord_points]})
    num_storeys = pd.DataFrame({"Num_Storeys": [storey_array]})


    # Concatenate dataframes
    siteData_rcds = pd.concat([site_data, coord_points, num_storeys], axis=1)

    # Rearrange columns to match MySQL ordering
    siteData_rcds = siteData_rcds.loc[:, ["Building_ID", "Name", "Building_Type", "Coords_LatLong",
                                        "Country", "City", "Construction", "Deconstruction", "Deconstruction_Company", "Consequence_Class", 
                                        "Exposure_Class", "Floor_Area", "Num_Wings", "Num_Storeys", "Notes"]]
    site_tuples = [tuple(row) for row in siteData_rcds.itertuples(index=False, name=None)]

    # Insert query
    siteData_insert = "INSERT INTO Donor_Building (Building_ID, Name, Building_Type, Coords_LatLong, Country, \
        City, Construction, Deconstruction, Deconstruction_Company, Consequence_Class, Exposure_Class, Total_Floor_Area, Num_Wings, Num_Storeys, Notes) \
            VALUES (%s, %s, %s, ST_GeomFromText(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    return (site_tuples, siteData_insert)