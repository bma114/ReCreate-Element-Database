# Import packages
import yaml
import pandas as pd
from sqlalchemy import text
from utils.formulas import FORMULA_REGISTRY
import inspect

class PhysLoader:
    def __init__(self, core_engine, phys_engine, mapping_path: str, element: str):
        self.core_engine = core_engine
        self.phys_engine = phys_engine
        self.element = element.lower()  # e.g. "wall","beam","column","slab"
        # Load the YAML once
        with open(mapping_path, 'r') as f:
            self.mapping = yaml.safe_load(f)

    # Pulls data from core layer for a given table. Can use SELECT * or a view
    def _fetch_core(self, table: str) -> pd.DataFrame:
        sql = f"SELECT * FROM {table}"
        return pd.read_sql(sql, self.core_engine)   

    # For each phys column in mapping[table], apply the registered formula
    def _apply_formulas(self, df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
        phys_df = df.copy()
        for col_name, col_cfg in cfg["columns"].items():
            func = FORMULA_REGISTRY[col_cfg["formula"]]
            arg_names = col_cfg.get("args", [])
            
            # Check if func expects an 'element' parameter
            sig = inspect.signature(func)
            needs_element = "element" in sig.parameters

            def apply_fn(row):
                vals = []
                for name in arg_names:
                    if name in row.index:
                        vals.append(row[name])
                    else: # otherwise a literal constant
                        vals.append(name)
                if needs_element:
                    vals.insert(1, self.element)
                return func(*vals)

            # def apply_fn(row):
            #     # Positional args from DataFrame columns
            #     vals = [row[name] for name in arg_names]
            #     # If the function needs the `element`, append it last
            #     if needs_element:
            #         vals.insert(1, self.element)
            #     return func(*vals)

            phys_df[col_name] = phys_df.apply(apply_fn, axis=1)
        return phys_df
    
    # Upsert the new phys df into the phys table using INSERT ... ON DUPLICATE KEY UPDATE.
    def _upsert_phys(self, df: pd.DataFrame, table: str, pk: str):
        tmp = f"_tmp_{table}"
        with self.phys_engine.begin() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS `{tmp}`;"))
            # Write to temp
            df.to_sql(f"_tmp_{table}", conn, schema="element_database_phys", if_exists="fail", index=False)
            cols = ", ".join(df.columns)
            updates = ", ".join([f"{c}=VALUES({c})" for c in df.columns if c!=pk])
            # Upsert into the phys layer from that temp table
            conn.execute(text(f"""
                INSERT INTO `element_database_phys`.`{table}` ({cols})
                SELECT {cols} FROM `element_database_phys`.`_tmp_{table}`
                ON DUPLICATE KEY UPDATE {updates};
            """))
            # Clean up: drop the temp table once done
            conn.execute(text(f"DROP TABLE `{tmp}`;"))

    # Create the dataframes by looping over every table in phys_map and load in dependency order.
    def run(self):

        core_db = self.core_engine.url.database
        phys_db = self.phys_engine.url.database

        # normalize element name for building tables
        if self.element.lower() == "hcs":
            elt_name = "HCS"
        else:
            elt_name = self.element.capitalize()

        # Geometry tables (without volume)
        if self.element != "hcs":
            geom_table = f"{elt_name}_Geometry"
            if geom_table in self.mapping:
                full_cfg = self.mapping[geom_table]
                df_core = self._fetch_core(geom_table)

                if df_core.empty: # no rows to process, skip this table
                    print(f"[skip] no geometry for {self.element}, skipping {geom_table}")
                else:
                    # Chose columns that are not formulas for volume or mass
                    basic_cols = {
                        k: v
                        for k, v in full_cfg["columns"].items()
                        if v["formula"] not in ("element_volume_m3", "element_mass_kg")
                    }
                    init_cfg = {"pk": full_cfg["pk"], "columns": basic_cols}
                    df_basic = self._apply_formulas(df_core, init_cfg)

                    # Distinguish between column cross-section type for correct dimension names.
                    if geom_table == "Column_Geometry":
                        section = df_core["Cross_Section"].str.lower()

                        # For rectangular columns: null out diameters
                        is_rect = section == "rectangular"
                        df_basic.loc[is_rect, ["diameter_a_mm","diameter_b_mm"]] = None

                        # For elliptical columns: null out depth & width
                        is_ell = section == "elliptical"
                        df_basic.loc[is_ell, ["total_depth_mm","total_width_mm"]] = None

                    # Placeholder zeros for the NOT NULL volume & mass fields
                    df_basic["element_volume_m3"] = 0.0
                    df_basic["element_mass_kg"]   = 0.0
                    keep = ([init_cfg["pk"]] + list(basic_cols.keys()) + ["element_volume_m3", "element_mass_kg"]) # trim to PK + basic phys + placeholders
                    df_basic = df_basic[keep]
                    self._upsert_phys(df_basic, geom_table, pk=init_cfg["pk"])
            

        # Additional_Panelling for walls
        if self.element == "wall" and "Additional_Panelling" in self.mapping:
            cfg = self.mapping["Additional_Panelling"]
            df_core = self._fetch_core("Additional_Panelling")

            if df_core.empty: # no rows to process, skip this table
                print(f"[skip] no geometry for {self.element}, skipping Additional_Panelling")
            else:
                df_phys = self._apply_formulas(df_core, cfg)
                keep = [cfg["pk"]] + list(cfg["columns"].keys()) # Keep only pk + all mapped phys columns
                df_phys = df_phys[keep]
                self._upsert_phys(df_phys, "Additional_Panelling", pk=cfg["pk"])


        # Zone tables are new to phys layer
        zone_table = f"{elt_name}_Zone_Geometry"
        if zone_table in self.mapping:
            cfg = self.mapping[zone_table]
            df_core = self._fetch_core(f"{elt_name}_Long_Reinf")

            if df_core.empty:
                print(f"[skip] no zones for {self.element}, skipping {zone_table}")
            else:
                # Load the zone definitions from the core (no Product_ID yet)
                core_zone = pd.read_sql(
                    f""" SELECT Zone_ID, Reinf_ID, ST_AsText(Zone_Coords) AS Zone_Coords, Zone_Plane
                    FROM `{core_db}`.`{elt_name}_Long_Reinf` """,
                    con=self.core_engine)
                # Pull Product_ID out of the core element geometry via Reinf_ID
                parent_core = pd.read_sql(
                    f"SELECT Product_ID, Reinf_ID "
                    f"  FROM {core_db}.`{elt_name}_Geometry`",
                    con=self.core_engine
                )
                core_zone = core_zone.merge(parent_core, on="Reinf_ID", how="left")

                # Dynamically pull whichever “total” column exists
                total_width_col = (
                    "total_thickness_mm"
                    if f"{elt_name}_Geometry" in self.mapping and
                    "total_thickness_mm" in pd.read_sql(
                        f"SHOW COLUMNS FROM `{phys_db}`.`{elt_name}_Geometry`",
                        con=self.phys_engine
                    )["Field"].tolist()
                    else
                    "total_width_mm"
                )
                # Get the calculated phys dimensions
                phys_dims = pd.read_sql(
                    f"SELECT Product_ID, total_height_mm, total_length_mm, `{total_width_col}` "
                    f"  FROM `{phys_db}`.`{elt_name}_Geometry`",
                    con=self.phys_engine
                )
                
                df_zone = core_zone.merge(phys_dims, on="Product_ID", how="left", validate="many_to_one")
                df_zone_phys = self._apply_formulas(df_zone, cfg) # compute phys columns
                keep = ["Zone_ID", "Reinf_ID", "Product_ID"] + list(cfg["columns"].keys())
                df_zone_phys = df_zone_phys[keep]
                self._upsert_phys(df_zone_phys, zone_table, pk=cfg["pk"])

        # Voids geometry
        void_table = f"{elt_name}_Voids"
        if void_table in self.mapping:
            cfg = self.mapping[void_table]
            # Load core void coords
            df_core = pd.read_sql(f"""SELECT Void_ID, Product_ID, Void_Coords_XYZ
                                  FROM `{core_db}`.`{void_table}` """, con=self.core_engine)

            if df_core.empty: # no rows to process, skip this table
                print(f"[skip] no geometry for {self.element}, skipping {void_table}")
            else:
                # Pull total_length_mm from phys parent
                phys_geom = pd.read_sql(f"""SELECT Product_ID, total_length_mm
                                        FROM `{phys_db}`.`{elt_name}_Geometry` """, con=self.phys_engine)

                # Normalize & merge
                for df in (df_core, phys_geom):
                    df["Product_ID"] = df["Product_ID"].astype(str).str.strip()
                df_core = df_core.merge(phys_geom, on="Product_ID", how="left")

                df_phys = self._apply_formulas(df_core, cfg)
                keep = ["Void_ID", "Product_ID"] + list(cfg["columns"].keys())
                df_phys = df_phys[keep]
                self._upsert_phys(df_phys, void_table, pk=cfg["pk"])


        # Corbel_Geometry
        fk_col = f"{elt_name}_Product_ID"
        if self.element in ("wall", "beam", "column") and "Corbel_Geometry" in self.mapping:
            cfg = self.mapping["Corbel_Geometry"]
            df_core = self._fetch_core("Corbel_Geometry")

            if df_core.empty: # no rows to process, skip this table
                print(f"[skip] no geometry for {self.element}, skipping Corbel_Geometry")
            else:
                # JOIN in parent Coords_XYZ from the element Geometry table
                core_parent_geom = (self._fetch_core(f"{elt_name}_Geometry")
                            [["Product_ID","Coords_XYZ"]].rename(columns={"Product_ID": fk_col}))
                df_core = df_core.merge(core_parent_geom, on=fk_col, how="left")

                # Filter out any rows without a parent (NaN in fk_col)
                df_core = df_core[df_core[fk_col].notna()]
                if df_core.empty:
                    print(f"[skip] no corbels for {self.element}, skipping Corbel_Geometry")
                else:
                    # Merge phys total_length_mm from the parent phys geometry
                    phys_parent_geom = pd.read_sql(
                        f"SELECT Product_ID, total_length_mm, density_kgm3 "
                        f"FROM `{phys_db}`.`{elt_name}_Geometry`",
                        con=self.phys_engine
                    ).rename(columns={"Product_ID": fk_col})

                    # Depending on element, populate the correct FK column
                    for col in ("Wall_Product_ID","Beam_Product_ID","Column_Product_ID"):
                        if col not in df_core.columns:
                            df_core[col] = None

                    # Normalize the key
                    df_core[fk_col] = df_core[fk_col].astype(str).str.strip()
                    phys_parent_geom[fk_col] = phys_parent_geom[fk_col].astype(str).str.strip()

                    # Merge once with an indicator
                    df_core = df_core.merge(
                        phys_parent_geom,
                        on=fk_col,
                        how="left",
                        indicator="match",
                        suffixes=("", "_drop")
                    )
                    # Clean up drops and indicator, merge and upsert
                    df_core = df_core.drop(columns=[c for c in df_core.columns if c.endswith("_drop")] + ["match"])
                    df_phys = self._apply_formulas(df_core, cfg)
                    keep = [cfg["pk"]] + list(cfg["columns"].keys()) # Keep only pk + all mapped phys columns
                    df_phys = df_phys[keep]
                    self._upsert_phys(df_phys, "Corbel_Geometry", pk=cfg["pk"])


        # Longitudinal Reinforcement
        long_table = f"{elt_name}_Long_Reinf"
        if long_table in self.mapping:
            cfg = self.mapping[long_table]
            # pull core data, including WKT for Layer_Coords
            df_core = pd.read_sql(
                f"""SELECT Long_ID, Zone_ID, Zone_Plane, ST_AsText(Layer_Coords) AS Layer_Coords, Bar_Diameter, Num_Bars
                  FROM `{core_db}`.`{long_table}`""", con=self.core_engine)
            
            if df_core.empty: # no rows to process, skip this table
                print(f"[skip] no geometry for {self.element}, skipping {long_table}")
            else:
                # Retrieve zone_height_mm
                phys_zone = pd.read_sql(
                    f""" SELECT Zone_ID, Reinf_ID, zone_height_mm 
                    FROM `{phys_db}`.`{elt_name}_Zone_Geometry`""", con=self.phys_engine)
                df_core = df_core.merge(phys_zone, on="Zone_ID", how="left")

                df_phys = self._apply_formulas(df_core, cfg) # apply formulas
                keep = [cfg["pk"], "Reinf_ID"] + list(cfg["columns"].keys())
                df_phys = df_phys[keep]
                self._upsert_phys(df_phys, long_table, pk=cfg["pk"])


        # Transverse reinforcement
        transv_table = f"{elt_name}_Transv_Reinf"
        if transv_table in self.mapping:
            cfg = self.mapping[transv_table]
            # Pull core data with WKT for Shape_Coords
            df_core = pd.read_sql(
                f""" SELECT Transv_ID, Zone_ID, Reinf_ID, Shape_Coords, Bent_Plane, Bar_Diameter, Spacing
                  FROM `{core_db}`.`{transv_table}`""", con=self.core_engine)
            if df_core.empty: # no rows to process, skip this table
                print(f"[skip] no geometry for {self.element}, skipping {transv_table}")
            else:
                # bring in zone_width_mm
                phys_zone = pd.read_sql(
                    f""" SELECT Zone_ID, zone_thickness_mm AS zone_width_mm
                    FROM `{phys_db}`.`{elt_name}_Zone_Geometry`""", con=self.phys_engine)
                df_core = df_core.merge(phys_zone, on="Zone_ID", how="left")

                if "zone_thickness_mm" in df_core.columns:
                    df_core["zone_width_mm"] = df_core["zone_thickness_mm"]
                elif "zone_width_mm" in df_core.columns:
                    pass
                else:
                    raise RuntimeError("No zone width column found for transverse reinf")

                # First compute num_legs via the generic path on its own
                simple_cols = {k:v for k,v in cfg["columns"].items() if k!="volumetric_ratio_mm3"}
                simple_cfg = {"pk":cfg["pk"], "columns": simple_cols}
                df_phys = self._apply_formulas(df_core, simple_cfg)

                # Then compute volumetric_ratio_mm3 manually
                f_vol = FORMULA_REGISTRY["volumetric_ratio_mm3"]
                def compute_vol(row):
                    return f_vol(row["Shape_Coords"], row["Bent_Plane"], self.element, None, row["Bar_Diameter"], row["Spacing"], row["zone_width_mm"])
                df_phys["volumetric_ratio_mm3"] = df_core.apply(compute_vol, axis=1)
                keep = [cfg["pk"], "Reinf_ID", "Zone_ID"] + list(cfg["columns"].keys())
                df_phys = df_phys[keep]
                self._upsert_phys(df_phys, transv_table, pk=cfg["pk"])


        # Prestressing
        if self.element == "hcs" and "HCS_Prestressing" in self.mapping:
            cfg = self.mapping["HCS_Prestressing"]
            # Load the prestress core table
            df_core = pd.read_sql(
                f""" SELECT Strand_ID, Reinf_ID, Strand_Diameter, Num_Wires, ST_AsText(Strand_Coord_XY) AS Strand_Coord_XY
                FROM `{core_db}`.`HCS_Prestressing` """, con=self.core_engine )

            # Pull height from the parent geometry
            df_geom = pd.read_sql(
                f""" SELECT Reinf_ID, Height
                FROM `{core_db}`.`HCS_Geometry`""", con=self.core_engine)

            # Merge 
            df_core = df_core.merge(df_geom, on="Reinf_ID", how="left")

            if df_core.empty: # no rows to process, skip this table
                print(f"[skip] no geometry for {self.element}, skipping HCS_Prestressing")
            else:
                df_phys = self._apply_formulas(df_core, cfg)
                keep = [cfg["pk"], "Reinf_ID"] + list(cfg["columns"].keys()) # Keep only pk + all mapped phys columns
                df_phys = df_phys[keep]
                self._upsert_phys(df_phys, "HCS_Prestressing", pk=cfg["pk"])


        # Element volume & mass (depends on corbels and voids) 
        if self.element != "hcs": 
            geom_table = f"{elt_name}_Geometry"
            df_core = self._fetch_core(geom_table)
            full_cfg  = self.mapping[geom_table]
            pk        = full_cfg["pk"]

            if df_core.empty: # no rows to process, skip this table
                    print(f"[skip] no geometry for {self.element}, skipping {geom_table}")
            else:
                # Read the phys geometry base DataFrame
                df_phys_geom = pd.read_sql(f"SELECT * FROM {phys_db}.{geom_table}", self.phys_engine)

                # Pull Coords_XYZ + Has_Corbel/Has_Void flags from the core geometry if they exist
                cols_to_pull = ["Product_ID", "Coords_XYZ"]
                core_cols = pd.read_sql(
                    f"SHOW COLUMNS FROM `{core_db}`.`{geom_table}`", con=self.core_engine)["Field"].tolist()
                if "Has_Corbel" in core_cols:
                    cols_to_pull.append("Has_Corbel")
                if "Has_Void" in core_cols:
                    cols_to_pull.append("Has_Void")

                df_core_geom = pd.read_sql(
                    f"SELECT {', '.join(cols_to_pull)} " f" FROM `{core_db}`.`{geom_table}`", con=self.core_engine)

                # Pull corbel volumes
                if self.element in ("wall", "beam", "column"):
                    # Read corbel volumes keyed by product_id
                    df_corb = pd.read_sql(f"SELECT `{fk_col}` AS Product_ID, volume_m3 AS corb_volume_m3 "
                                        f"FROM `{phys_db}`.`Corbel_Geometry`", con=self.phys_engine )
                else:
                    df_corb = pd.DataFrame(columns=["Product_ID", "corb_volume_m3"]) # no corbels for slabs = empty DF

                # Read void volumes for this element
                void_table = f"{elt_name}_Voids"
                if void_table in self.mapping:
                    df_void = pd.read_sql(f"SELECT Product_ID, volume_m3 AS void_volume_m3 \
                                        FROM {phys_db}.{void_table}", con=self.phys_engine)
                else:
                    df_void = pd.DataFrame(columns=["Product_ID","void_volume_m3"])

                # Merge everything onto a single DF
                for d in (df_phys_geom, df_core_geom, df_corb, df_void):
                    d["Product_ID"] = d["Product_ID"].astype(str).str.strip()
                df = (
                    df_phys_geom
                    .merge(df_core_geom, on="Product_ID", how="left")
                    .merge(df_corb,      on="Product_ID", how="left")
                    .merge(df_void,      on="Product_ID", how="left")
                    .fillna({
                        "corb_volume_m3": 0.0,
                        "void_volume_m3": 0.0,
                        "Has_Corbel": False,
                        "Has_Void": False
                    })
                )

                # Call the formulas for *only* volume & mass
                vol_col_cfg = full_cfg["columns"]["element_volume_m3"].copy()
                vol_col_cfg["args"] = full_cfg["columns"]["element_volume_m3"]["args"] # Keep the original args (including 'element')
                mini_cfg = {
                    "pk": full_cfg["pk"],
                    "columns": {
                        "element_volume_m3": vol_col_cfg,
                        "element_mass_kg":   full_cfg["columns"]["element_mass_kg"],
                    }
                }
                df_full_phys = self._apply_formulas(df, mini_cfg)

                # Subset & upsert
                keep = [pk] + list(full_cfg["columns"].keys())
                df_up = df_full_phys[keep]

                with self.phys_engine.begin() as conn:
                    tmp = f"_tmp_{geom_table}"

                    # Drop old temp table if it exists
                    conn.execute(text(f"DROP TABLE IF EXISTS `{tmp}`;"))

                    # Create fresh temp table without reflection
                    df_up.to_sql(tmp, conn, if_exists="fail", index=False)

                    # Build INSERT
                    keep = [pk] + list(full_cfg["columns"].keys())
                    cols   = ", ".join(f"`{c}`" for c in keep)
                    updates = ", ".join(f"`{c}`=VALUES(`{c}`)" for c in keep if c != pk)
                    conn.execute(text(f"""
                        INSERT INTO `{geom_table}` ({cols})
                        SELECT {cols} FROM `{tmp}`
                        ON DUPLICATE KEY UPDATE {updates};
                    """))
                    conn.execute(text(f"DROP TABLE IF EXISTS `{tmp}`;")) # Clean up
        