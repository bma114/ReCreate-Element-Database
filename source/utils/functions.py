# Import packages
import pandas as pd
import numpy as np
from scipy.spatial import ConvexHull # For TIN Z triangulation



#----------------------------------------------------------------------------------------#
#                                      FUNCTIONS
#----------------------------------------------------------------------------------------#

def skip_empty_sheet(fn):
    """
    If the first DataFrame argument is empty or has no non-null rows,
    return ([], [], None) so the caller 'if tuples:' skips it.
    """
    def wrapper(df, *args, **kwargs):
        try:                          # Quick skip if truly empty
            if df is None or df.empty or df.dropna(how="all").empty:
                return [], [], None
        except Exception:             # df might not be a DataFrame, ignore
            pass
        try:                          # Otherwise run and catch IndexError
            return fn(df, *args, **kwargs)
        except IndexError:
            return [], [], None
    return wrapper

# Reformat coordinates into WKT POINT datatype
def format_point(coords):
    # Construct the POINT string
    point_str = "POINT("
    for coord in coords:
        point_str += f"{coord[0]} {coord[1]}, "

    # Remove the trailing comma and space, then close the POINT
    point_str = point_str[:-2] + ")"
    return point_str


# Reformat coordinates into WKT POINTZ datatype
def format_pointz(coords):
    # Construct the POINTZ strings for each coordinate
    pointz_list = []
    for coord in coords:
        pointz_str = f"POINT Z ({coord[0]} {coord[1]} {coord[2]})"
        pointz_list.append(pointz_str)
    
    return pointz_list


# Reformat coordinates into WKT LINESTRING datatype
def format_linestr(coords):
    # Construct the LINESTRING string
    linestring_str = "LINESTRING("
    for coord in coords:
        linestring_str += f"{coord[0]} {coord[1]}, "

    # Remove the trailing comma and space, then close the LINESTRING
    linestring_str = linestring_str[:-2] + ")"
    return linestring_str


# Reformat coordinates into WKT MULTIPOINTM datatype
def format_multipointzm(coords_list):
    multipointzm_list = []
    for coords in coords_list:
        pt_str = "MULTIPOINT ZM ("
        for x, y, z, m in coords:
            pt_str += f"({x} {y} {z} {m}), "
        pt_str = pt_str[:-2] + ")"
        multipointzm_list.append(pt_str)
    return multipointzm_list


# Reformat coordinates into WKT MULTIPOINTZ datatype
def format_multipointz(coords_list):
    multipointz_list = []
    for coords in coords_list:
        point_str = "MULTIPOINT Z ("
        for coord in coords:
            point_str += f"({coord[0]} {coord[1]} {coord[2]}), "
        point_str = point_str[:-2] + ")"  # Remove the trailing comma and space, then close the MULTIPOINTZ
        multipointz_list.append(point_str)
    return multipointz_list


# Reformat coordinates into WKT POLYGON datatype
def format_polygon(coords):
    # Construct the WKT POLYGON strings for each row
    wkt_polygons = []
    for row_coords in coords:
        polygon_str = "POLYGON(("
        for coord in row_coords:
            polygon_str += f"{coord[0]} {coord[1]}, "
        # Close the polygon by repeating the first coordinate
        first_coord = row_coords[0]
        polygon_str += f"{first_coord[0]} {first_coord[1]}))"
        wkt_polygons.append(polygon_str)
    return wkt_polygons


# Reformat coordinates into WKT TIN Z strings
def format_tinz(coords_list):
    tinz_list = []
    # print(coords_list) # For debugging
    for pts in coords_list:
        pts_arr = np.array(pts)
        
        
        hull = ConvexHull(pts_arr)
        triangles = []
        for simplex in hull.simplices:
            # simplex is a triple of indices into pts_arr
            tri = pts_arr[simplex]
            # close the ring by repeating the first point
            coords = list(tri) + [tuple(tri[0])]
            ring = ", ".join(f"{x} {y} {z}" for x, y, z in coords)
            triangles.append(f"(({ring}))")
        wkt = "TIN Z (" + ", ".join(triangles) + ")"
        tinz_list.append(wkt)
    return tinz_list


# Convert 2D system into 3D coordinates - returns list of (x,y,z) tuples covering every implied surface junction
def convert_to_3d(front_view, side_view, plan_view):
    # Initialize an empty list to store 3D coordinates
    all_coordinates_3d = []

    # Drop any None’s up front
    F = [(x,z) for x,z in front_view if x is not None and z is not None]
    S = [(y,z) for y,z in  side_view if y is not None and z is not None]
    P = [(x,y) for x,y in  plan_view if x is not None and y is not None]

    # Unique coordinate lists
    xs = sorted({x for x,_ in F} | {x for x,_ in P})
    ys = sorted({y for y,_ in S} | {y for _,y in P})
    zs = sorted({z for _,z in F} | {z for _,z in S})

    pts_3d = set()
    # Extrude front (x,z) across all y
    for x,z in F:
        for y in ys:
            pts_3d.add((x,y,z))
    # Extrude side (y,z) across all x
    for y,z in S:
        for x in xs:
            pts_3d.add((x,y,z))
    # Extrude plan (x,y) across all z
    for x,y in P:
        for z in zs:
            pts_3d.add((x,y,z))
    
    # return as sorted list
    return sorted(pts_3d)


def convert_to_3d_element(front_array, side_array, plan_array):
    all_elements = []
    for F, S, P in zip(front_array, side_array, plan_array):
        all_elements.append(convert_to_3d(F, S, P))
    return all_elements


# Define the transverse reinforcement shape by creating lists of arrays
def create_shape_arrays(wallTrnvRF_wksh, reinf_index):
    shape_array = []

    # Iterate over each pair of indices in reinf_index
    for i in range(len(reinf_index) - 1):
        start_index = reinf_index[i]
        end_index = reinf_index[i + 1]

        # Get the Bent_Plane value for the start_index
        bent_plane = wallTrnvRF_wksh.at[start_index, 'Bent Plane']

        # Determine the columns based on the Bent_Plane value
        if bent_plane == 'YZ':
            cols = [10, 11, 8]
        elif bent_plane == 'XY':
            cols = [9, 10, 8]
        elif bent_plane == 'XZ':
            cols = [9, 11, 8]
        else:
            raise ValueError(f"Invalid Bent_Plane value '{bent_plane}'")

        raw = []
        for idx in range(start_index, end_index):
            raw.append(tuple(wallTrnvRF_wksh.iloc[idx, cols]))  # (a, b, theta)

        # inject the missing coord → (x,y,z,m)
        zm = []
        for a, b, theta in raw:
            if bent_plane == 'YZ':
                x, y, z = 0, a, b
            elif bent_plane == 'XY':
                x, y, z = a, b, 0
            else:  # 'XZ'
                x, y, z = a, 0, b
            zm.append((x, y, z, theta))

        shape_array.append(zm)

    final_index = reinf_index[-1]
    bent_plane  = wallTrnvRF_wksh.at[final_index, 'Bent Plane']
    if bent_plane == 'YZ':
        cols = [10, 11, 8]
    elif bent_plane == 'XY':
        cols = [9,  10, 8]
    elif bent_plane == 'XZ':
        cols = [9,  11, 8]
    else:
        raise ValueError(f"Invalid Bent_Plane value '{bent_plane}'")

    raw = []
    for idx in range(final_index, len(wallTrnvRF_wksh)):
        raw.append(tuple(wallTrnvRF_wksh.iloc[idx, cols]))

    zm = []
    for a, b, theta in raw:
        if bent_plane == 'YZ':
            x, y, z = 0, a, b
        elif bent_plane == 'XY':
            x, y, z = a, b, 0
        else:
            x, y, z = a, 0, b
        zm.append((x, y, z, theta))

    shape_array.append(zm)

    return shape_array