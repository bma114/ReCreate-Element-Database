#----------------------------------------------------------------------------------------#
#                                      PREAMBLE
#----------------------------------------------------------------------------------------#

# import connector and packages
from __future__ import annotations
from typing import List, Tuple, Optional, Any, Callable, Dict
from shapely import wkt
from shapely.errors import DimensionError
import re, math
from collections import Counter


# Registry for dynamic formula lookup
FORMULA_REGISTRY: Dict[str, Callable[..., Any]] = {}

def register_formula(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to register a formula under a given name."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        FORMULA_REGISTRY[name] = func
        return func
    return decorator


#----------------------------------------------------------------------------------------#
#                                  HELPER FUNCTIONS
#----------------------------------------------------------------------------------------#

# Convert a POINT WKT string to a list of (x, y, z) tuples
def parse_pointz(wkt_str: str) -> List[Tuple[float, float, float]]:
    # Shapley interprets all 2D and 3D POINTs the same, so a third empty dim must be added.
    geom = wkt.loads(wkt_str)
    if geom.geom_type.lower() != "point":
        raise ValueError("Expected POINT geometry.")
    try:
        z = geom.z
    except DimensionError:
        z = 0.0
    return [(geom.x, geom.y, z)]    

# Convert a MULTIPOINT Z WKT string to a list of (x, y, z) tuples
def parse_multipointz(wkt_str: str) -> List[Tuple[float, float, float]]:
    # Shapley normalizes any mulitpoint with extra dims (Z, M, or ZM) the same way

    geom = wkt.loads(wkt_str)
    if geom.geom_type.lower() != "multipoint":
        raise ValueError("Expected MULTIPOINTZ geometry.")
    return [(pt.x, pt.y, getattr(pt, "z", 0.0)) for pt in geom.geoms]

# Parse MULTIPOINT ZM WKT into list of (x, y, z, m=theta)
def parse_multipointzm(wkt_str: str) -> List[Tuple[float, float, float, float]]:
    _RE_NUM = r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?"
    nums = re.findall(_RE_NUM, wkt_str)
    if len(nums) % 4 != 0:
        raise ValueError("Expected quadruples (x y z m) in the WKT.")
    vals = list(map(float, nums))
    return [(vals[i], vals[i+1], vals[i+2], vals[i+3]) for i in range(0, len(vals), 4)]

# Parse a 2D POLYGON WKT and embed it into 3D coords based on the plane (XY, XZ, or YZ)
def parse_polygon_zones(polygon_wkt: str, zone_plane: str) -> list[tuple[float,float,float]]:
    geom = wkt.loads(polygon_wkt)
    if geom.geom_type.lower() != "polygon":
        raise ValueError("Expected POLYGON geometry.")
    coords2d = list(geom.exterior.coords)
    plane = zone_plane.upper()
    triples = []
    # Shapley treats every vertex as (x, y) with no z - so convert to a triple
    for x2, y2 in coords2d:
        if plane == "XY":
            triples.append((x2, y2, 0.0))
        elif plane == "XZ":
            triples.append((x2, 0.0, y2))
        elif plane == "YZ":
            triples.append((0.0, x2, y2))
        else:
            raise ValueError(f"Unknown zone_plane: {zone_plane}")
    return triples

# Parse 2D LINESTRING and embed it into 3D coords based on the plane (XY, XZ, or YZ)
def parse_linestring_zones(linestring_wkt: str, zone_plane: str) -> List[Tuple[float, float, float]]:
    geom = wkt.loads(linestring_wkt)
    if geom.geom_type.lower() != "linestring":
        raise ValueError("Expected LINESTRING geometry.")
    coords2d = list(geom.coords)
    plane = zone_plane.upper()
    triples: List[Tuple[float, float, float]] = []
    # Shapley treats all linestrings (2D or 3D) the same (e.g. including Z or ZM).
    for x2, y2 in coords2d:
        if plane == "XY":
            triples.append((x2, y2, 0.0))
        elif plane == "XZ":
            triples.append((x2, 0.0, y2))
        elif plane == "YZ":
            triples.append((0.0, x2, y2))
        else:
            raise ValueError(f"Unknown zone_plane: {zone_plane}")
    return triples

# Get the max-min span along 'x', 'y', or 'z'
def extent_along_axis(coords: List[Tuple[float, float, float]], axis: str) -> float:
    idx = {"x": 0, "y": 1, "z": 2}[axis.lower()]
    vals = [c[idx] for c in coords]
    return max(vals) - min(vals)

# Get the dimensions of a polygon along a specified axis
def zone_extent(polygon_wkt: str, zone_plane: str, axis: str) -> float:
    coords3d = parse_polygon_zones(polygon_wkt, zone_plane)
    idx = {"x":0,"y":1,"z":2}[axis.lower()]
    vals = [c[idx] for c in coords3d]
    return max(vals) - min(vals)

# Typical density values for common concrete types in kg/m^3
DENSITY_MAP: Dict[str, float] = {
    "Normal": 2400,
    "Lightweight": 1800,
    "Insulating ultralight": 1000,
    "UHPC": 2500,
    "Heavyweight": 3250,
    "Pervious": 2000,
}


#----------------------------------------------------------------------------------------#
#                                  GEOMETRIC PROPERTIES
#----------------------------------------------------------------------------------------#

# Total element height in mm
@register_formula("total_height_mm")
def total_height_mm(wkt_str: str) -> float:
    coords = parse_multipointz(wkt_str)
    return extent_along_axis(coords, "z")

# Total element length in mm
@register_formula("total_length_mm")
def total_length_mm(wkt_str: str) -> float:
    coords = parse_multipointz(wkt_str)
    return extent_along_axis(coords, "x")

# Total element width in mm - all elements except walls
@register_formula("total_width_mm")
def total_width_mm(wkt_str: str) -> Optional[float]:
    coords = parse_multipointz(wkt_str)
    return extent_along_axis(coords, "y")

# Total wall thickness in mm - used for wall elements only
@register_formula("total_thickness_mm")
def total_thickness_mm(wkt_str: str, element: str) -> Optional[float]:
    if element.lower() != "wall":
        return None
    coords = parse_multipointz(wkt_str)
    return extent_along_axis(coords, "y")

# First 'a' diameter of an elliptical column
@register_formula("d_a_mm")
def d_a_mm(wkt_str: str, element: str) -> Optional[float]:
    if element.lower() != "column":
        return None
    coords = parse_multipointz(wkt_str)
    return extent_along_axis(coords, "x")

# Second 'b' diameter of an elliptical column
@register_formula("d_b_mm")
def d_b_mm(wkt_str: str, element: str) -> Optional[float]:
    if element.lower() != "column":
        return None
    coords = parse_multipointz(wkt_str)
    return extent_along_axis(coords, "y")

# Density in kg/m^3 based on concrete type
@register_formula("density_kgm3")
def density_kgm3(concrete_type: str) -> float:
    return DENSITY_MAP.get(concrete_type, 2400)  # default to Normal if missing

# Total element volume in m3, accounting for corbels (+) and voids (-)
@register_formula("element_volume_m3")
def element_volume_m3(wkt_str: str, element: str, corb_volume_m: float = 0.0, void_volume_m3: float = 0.0, 
                      has_corbel: bool = False, has_void: bool = False) -> float:
    # Compute base volume in cubic meters from extents (or ellipse for column)
    h = FORMULA_REGISTRY["total_height_mm"](wkt_str) / 1000
    elem = element.lower()
    if elem == "column":
        a = FORMULA_REGISTRY["d_a_mm"](wkt_str, element) / 1000
        b = FORMULA_REGISTRY["d_b_mm"](wkt_str, element) / 1000
        base_vol = math.pi * a * b * h / 4
    else:
        L = FORMULA_REGISTRY["total_length_mm"](wkt_str) / 1000
        if elem == "wall":
            T = FORMULA_REGISTRY["total_thickness_mm"](wkt_str, element) / 1000
        else:
            T = FORMULA_REGISTRY["total_width_mm"](wkt_str) / 1000
        base_vol = L * T * h

    if has_corbel and elem in ("wall", "beam", "column"): # Add corbel volume if present
        base_vol += corb_volume_m
    if has_void and elem in ("wall", "slab"): #  Subtract void volume if present
        base_vol -= void_volume_m3

    return base_vol
    
# Total element mass in kg
@register_formula("element_mass_kg")
def element_mass_kg(volume: float, density: float) -> float:
    return volume * density

# Zone length in mm - if zone_plane includes X, use polygon extent along X; otherwise use total_length_mm
@register_formula("zone_length_mm")
def zone_length_mm(polygon_wkt: str, zone_plane: str, total_length_mm: float) -> float:
    if "X" in zone_plane.upper():
        return zone_extent(polygon_wkt, zone_plane, "x")
    return total_length_mm

# Zone height in mm - if zone_plane includes Z, use polygon extent along z; otherwise use total_height_mm
@register_formula("zone_height_mm")
def zone_height_mm(polygon_wkt: str, zone_plane: str, total_height_mm: float) -> float:
    if "Z" in zone_plane.upper():
        return zone_extent(polygon_wkt, zone_plane, "z")
    return total_height_mm

# Zone width in mm - if zone_plane includes Y, use polygon extent along Y; otherwise use total_width_mm
@register_formula("zone_width_mm")
def zone_width_mm(polygon_wkt: str, zone_plane: str, total_width_mm: float) -> float:
    if "Y" in zone_plane.upper():
        return zone_extent(polygon_wkt, zone_plane, "y")
    return total_width_mm


#----------------------------------------------------------------------------------------#
#                              CORBEL GEOMETRIC PROPERTIES
#----------------------------------------------------------------------------------------#

# Corbel depth in mm
@register_formula("corb_depth_mm")
def corb_depth_mm(corb_wkt: str) -> float:
    # Corbel depth (out-of-plane thickness) = Y-extent of corbel multipoint.
    coords = parse_multipointz(corb_wkt)
    return extent_along_axis(coords, "y")

# Corbel length in mm
@register_formula("corb_length_mm")
def corb_length_mm(corb_wkt: str, extruded_plane: str) -> float: 
    coords = parse_multipointz(corb_wkt)
    axis = "x" if extruded_plane.upper() == "XZ" else "y"
    return extent_along_axis(coords, axis)

# Corbel midpoint along X in mm
@register_formula("corb_midpoint_mm")
def corb_midpoint_mm(corb_wkt: str, extruded_plane: str) -> float:
    coords = parse_multipointz(corb_wkt)
    axis = "x" if extruded_plane.upper() == "XZ" else "y"
    idx = {"x": 0, "y": 1}[axis]
    values = [c[idx] for c in coords]
    length = max(values) - min(values)
    return max(values) - (length / 2)

# Distance from top of element to corbel bottom in mm
@register_formula("corb_dist_from_top_mm")
def corb_dist_from_top_mm(parent_wkt: str, corb_wkt: str) -> float:
    parent_height = total_height_mm(parent_wkt)
    coords = parse_multipointz(corb_wkt)
    zmax = max(c[2] for c in coords)
    return parent_height - zmax

# Height of rectangular block component in mm
@register_formula("rect_blk_height_mm")
def rect_blk_height_mm(corb_wkt: str) -> float:
    coords = parse_multipointz(corb_wkt)
    zs = sorted({z for (_, _, z) in coords}, reverse=True)
    if len(zs) < 2:
        return 0.0
    return zs[0] - zs[1]

# Height of triangular block component in mm
@register_formula("tri_blk_height_mm")
def tri_blk_height_mm(corb_wkt: str) -> float:
    coords = parse_multipointz(corb_wkt)
    zs = sorted({z for (_, _, z) in coords}, reverse=True)
    if len(zs) < 2:
        return 0.0
    bottom_of_rect = zs[1]
    min_z = zs[-1]
    return bottom_of_rect - min_z

# Horizontal offset of corbel midpoint from element centerline in mm
@register_formula("centerHoffset_mm")
def centerHoffset_mm(midpoint_mm: float, total_length_mm: float) -> float:
    return midpoint_mm - (total_length_mm / 2)


# Corbel volume in m3 - specifically for a rectangular+triangular geometry
@register_formula("corb_volume_m3")
def corb_volume_m3(corb_depth_mm: float, corb_length_mm: float, rect_blk_height_mm: float, tri_blk_height_mm: float,) -> float:
    # Simplified approximation - does not account for recesses. 
    # Alternatively, use the TIN Z shell attribute to calculate volume.
    tri_volume = 0.5 * (corb_depth_mm/1000) * (tri_blk_height_mm/1000) * (corb_length_mm/1000)
    rect_volume = (corb_depth_mm/1000) * (rect_blk_height_mm/1000) * (corb_length_mm/1000)
    return tri_volume + rect_volume


# Corbel mass in kg
@register_formula("corb_mass_kg")
def corb_mass_kg(corb_volume_m3: float, density_kgm3: float) -> float:
    return corb_volume_m3 * density_kgm3



#----------------------------------------------------------------------------------------#
#                          VOID PROPERTIES - WALLS AND SOLID SLABS
#----------------------------------------------------------------------------------------#

# Void base vertical offset in mm - min Z
@register_formula("baseVoffset_mm")
def baseVoffset_mm(void_wkt: str) -> float:
    coords = parse_multipointz(void_wkt)
    return min(z for (_, _, z) in coords)

# Void horizontal center in mm
@register_formula("void_center_mm")
def void_center_mm(void_wkt: str) -> float:
    # Voids in both walls and solid slabs run horizontally in x 
    coords = parse_multipointz(void_wkt)
    xs = [x for (x, _, _) in coords]
    return (min(xs) + max(xs)) / 2

# Void height in mm
@register_formula("void_height_mm")
def void_height_mm(void_wkt: str, element: str) -> float:
    coords = parse_multipointz(void_wkt)
    elem = element.lower()
    if elem == "wall":
        return extent_along_axis(coords, "z")
    elif elem == "slab":
        return extent_along_axis(coords, "y")
    else: # Other element types don't have voids
        raise ValueError(f"Unknown element type: {elem}")

# Void length in mm
@register_formula("void_length_mm")
def void_length_mm(void_wkt: str) -> float:
    # Voids in both walls and solid slabs run horizontally in x 
    coords = parse_multipointz(void_wkt)
    return extent_along_axis(coords, "x")

# Void depth in mm
@register_formula("void_depth_mm")
def void_depth_mm(void_wkt: str, element: str) -> Optional[float]:
    coords = parse_multipointz(void_wkt)
    elem = element.lower()
    if elem == "wall":
        return extent_along_axis(coords, "y")
    elif elem == "slab":
        return extent_along_axis(coords, "z")
    else: # Other element types don't have voids
        raise ValueError(f"Unknown element type: {elem}")

# Void volume in m3 - approximated as a uniform rectangular prism
@register_formula("void_volume_m3")
def void_volume_m3(length_mm: float, depth_mm: float, height_mm: float) -> float:
    return (length_mm / 1000) * (depth_mm / 1000) * (height_mm / 1000)



#----------------------------------------------------------------------------------------#
#                          ADDITIONAL PANEL PROPERTIES - WALLS
#----------------------------------------------------------------------------------------#

"""
Overall panel dimensions use the same registered formulas as the structural elements.
Geometries are simplified to rectangular prisms in this version.
"""
# Panel or insulation layer volume in m3
@register_formula("extra_layer_volume_m3")
def extra_layer_volume_m3(length_mm: float, thickness_mm: float, height_mm: float) -> float:
    return (length_mm / 1000.0) * (thickness_mm / 1000.0) * (height_mm / 1000.0)



#----------------------------------------------------------------------------------------#
#                          LONGITUDINAL REINFORCEMENT PROPERTIES
#----------------------------------------------------------------------------------------#

# Bar lengths per layer in mm 
@register_formula("bar_length_mm")
def bar_length_mm(linestring_wkt: str, zone_plane: str) -> float:
    """
    Total length of a rebar layer: sum of segment lengths in mm.
    """
    pts = parse_linestring_zones(linestring_wkt, zone_plane)
    length = 0.0
    for p0, p1 in zip(pts, pts[1:]):
        length += math.dist(p0, p1) 
    return length

# Total cross-sectional area of all bars in the layer in mm2
@register_formula("bar_area_mm2")
def bar_area_mm2(bar_diam_mm: float, num_bars: int) -> float:
    area_single = math.pi * (bar_diam_mm ** 2) / 4
    return area_single * num_bars

# Effective depth of each layer, relative to the zone height in mm
@register_formula("effective_depth_mm")
def effective_depth_mm(linestring_wkt: str, zone_plane: str, zone_height_mm: float) -> float:
    pts = parse_linestring_zones(linestring_wkt, zone_plane)
    plane = zone_plane.upper()
    # Layer height coords
    if plane in ("XZ", "YZ"):
        coords = [z for (_, _, z) in pts] # Z-axis is height
    else:
        coords = [y for (_, y, _) in pts] # Y-axis is height in XY plane
    avg_coord = sum(coords) / len(coords) if coords else 0.0 # average height
    return zone_height_mm - avg_coord



#----------------------------------------------------------------------------------------#
#                           TRANSVERSE REINFORCEMENT PROPERTIES
#----------------------------------------------------------------------------------------#

"""
Estimate number of legs along both axes of the bent plane. Returns a string "(n1,n2)".
This estimate uses the bent angle 'theta' to determine if a segment is anchored or not, 
and counts the number of anchored segments along each axis in the plane. 
"""
@register_formula("num_legs")
def num_legs(stirrup_wkt: str, bent_plane: str) -> str:
    pts = parse_multipointzm(stirrup_wkt)
    plane = bent_plane.upper()
    if len(plane) != 2 or any(c not in "XYZ" for c in plane):
        raise ValueError("Invalid bent_plane.")
    axis_idx = {"X": 0, "Y": 1, "Z": 2}
    idxA = axis_idx[plane[0]]
    idxB = axis_idx[plane[1]]
    n = len(pts)
    legsA = 0
    legsB = 0

    for i in range(n):
        p = pts[i]
        q = pts[(i+1) % n]  # next, the closing loop
        theta_p = p[3]
        theta_q = q[3]
        # check anchored: both theta != 0
        anchored = (theta_p != 0 and theta_q != 0)
        # compute absolute deltas along A and B for diagonal segments
        deltaA = abs(p[idxA] - q[idxA])
        deltaB = abs(p[idxB] - q[idxB])
        if deltaA > deltaB: # oriented along A axis
            if anchored:
                legsA += 1
        else:
            if anchored: # oriented along B axis
                legsB += 1

    legsA = max(1, legsA) # ensure at least one leg
    legsB = max(1, legsB)
    return f"({legsA},{legsB})"

"""
Compute the transverse volumetric ratio for both axes of the stirrup using the number of legs for rectangular sections,
and the hoop formula for elliptical cross-sections, returning (rho1,rho2).
"""
@register_formula("volumetric_ratio_mm3")
def volumetric_ratio_mm3(stirrup_wkt: str, bent_plane: str, element: str, cross_section: Optional[str], 
                         stirrup_diam_mm: float, stirrup_spacing_mm: float, zone_width_mm: float, 
                         da_mm: Optional[float] = None, db_mm: Optional[float] = None) -> float: 
    legs_str = FORMULA_REGISTRY["num_legs"](stirrup_wkt, bent_plane)  # e.g. "(2,3)"
    m = re.match(r"\(\s*(\d+)\s*,\s*(\d+)\s*\)", legs_str)
    if not m:
        raise ValueError(f"Invalid num_legs format: {legs_str}")
    legsA, legsB = int(m.group(1)), int(m.group(2))

    # Elliptical cross-sections
    elem = element.lower()
    if elem == "column" and cross_section and cross_section.lower() == "elliptical":
        if da_mm is None or db_mm is None:
            raise ValueError("Elliptical column needs da_mm and db_mm.")
        P_e = math.pi * (
            3*(da_mm/2 + db_mm/2)
            - math.sqrt((3*da_mm/2 + db_mm)*(da_mm/2 + 3*db_mm))
        )
        rho = (stirrup_diam_mm**2 * P_e) / (stirrup_spacing_mm * da_mm * db_mm)
        return f"({rho:.6f},{rho:.6f})" # single rho for elliptical section and duplicate

    # Rectangular cross-sections
    area_leg = math.pi * (stirrup_diam_mm**2) / 4         # mm2 per leg
    steel_per_mm = area_leg                               # mm3 of steel per mm of one leg
    steelA = legsA * steel_per_mm                         # axis‐wise steel volume per mm
    steelB = legsB * steel_per_mm
    concrete_per_mm = zone_width_mm * stirrup_spacing_mm  # mm3 per mm length

    rhoA = steelA / concrete_per_mm
    rhoB = steelB / concrete_per_mm
    return f"({rhoA:.6f},{rhoB:.6f})"


#----------------------------------------------------------------------------------------#
#                           PRESTRESSING REINFORCEMENT PROPERTIES
#----------------------------------------------------------------------------------------#

# Prestressing tendon area in mm2
@register_formula("tendon_area_mm2")
def tendon_area_mm2(strand_diam: float, num_wires: float) -> float:
    d_wire = strand_diam / 3
    A_wire = math.pi * (d_wire ** 2) / 4
    return A_wire * num_wires

@register_formula("tendon_eff_depth_mm")
def tendon_eff_depth_mm(tendon_wkt: float, slab_height: float) -> float:
    pts = parse_pointz(tendon_wkt)
    _, y, _ = pts[0]
    return slab_height - y



#----------------------------------------------------------------------------------------#
#                                BEAM CAPACITY CALCULATIONS
#----------------------------------------------------------------------------------------#

# Eurocode 2 bending resistance (positive sagging) of a rectangular beam. Returns M_rd in kN·m.
@register_formula("beam_bending_pos_kN")
def beam_bending_pos_kN(
    fck_MPa: float,                    # concrete characteristic strength [MPa]
    fyk_MPa: float,                    # steel characteristic yield strength [MPa]
    b_mm: float,                       # beam width [mm]
    d_mm: float,                       # effective depth to tensile steel [mm]
    As1_mm2: float,                    # area of tensile reinforcement [mm²]
    dp_mm: float,                      # effective depth to compressive steel [mm]
    As2_mm2: Optional[float] = 0.0,    # area of compressive reinforcement [mm²]
    gamma_c: Optional[float] = 1.5,    # Partial factor for concrete
    gamma_s: Optional[float] = 1.15,   # Partial factor for steel
    xi_max: Optional[float] = 0.45,    # Max neutral‐axis ratio x/d, defaults to 0.45
) -> float:

    # Design strengths
    alpha_cc = 0.85
    f_cd = alpha_cc * fck_MPa / gamma_c  
    f_yd = fyk_MPa / gamma_s            

    # Internal steel forces
    T_steel = As1_mm2 * f_yd
    C_steel = As2_mm2 * f_yd # assume yielding

    if T_steel <= 0:         # Section over‐reinforced or no tension steel
        return 0.0

    # Neutral‐axis depth x
    x = (T_steel - C_steel) / (0.68 * b_mm * f_cd)   # Cc = 0.68 f_cd b x   and   Cc + Cs = T
    x_lim = xi_max * d_mm
    if x > x_lim:
        x = x_lim

    # Lever arms
    z_c = d_mm - 0.32 * x
    z_s = d_mm - dp_mm

    # Moment capacity [N·mm] → [kN·m]
    M_Rd_Nmm = 0.68 * f_cd * b_mm * x * z_c + (C_steel * z_s)
    return round(M_Rd_Nmm / 1e6, 3)




# EXAMPLE INPUTS
# wall_wkt = "MULTIPOINT Z ((0 0 0), (0 0 3480), (0 175 0), (0 175 3480), (3584 0 0), (3584 0 3480), (3584 175 0), (3584 175 3480))"
# zone_poly_wkt = "POLYGON((0 0, 0 880, 3584 880, 3584 0, 0 0))"
# void_wkt = "MULTIPOINT Z ((592 0 880), (592 0 2650), (2992 0 2650), (2992 0 880), (577 175 880), (577 175 2665), (3007 175 2665), (3007 175 880))"
# layer_line_wkt = "LINESTRING(25 35, 3559 35)"
# stirrup_shape_wkt = "MULTIPOINT ZM((0 25 2000 79.695), (0 25 2200 90), (0 300 2200 90), (0 300 2050 100.305))"
# bent_plane = 'YZ'
# strand_diam = 12.5
# num_wires = 7

# print("Tendon area:", tendon_area_mm2(strand_diam, num_wires))