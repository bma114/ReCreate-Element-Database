# Import packages
import yaml
import pandas as pd
from sqlalchemy import text
from utils.formulas import FORMULA_REGISTRY
import inspect


class AnalysisLoader:
    def __init__(self, core_engine, phys_engine, anal_engine, mapping_path: str):
        self.core_engine = core_engine      # element_database_core
        self.phys_engine = phys_engine      # element_database_phys
        self.anal_engine = anal_engine      # element_database_anal
        with open(mapping_path, 'r') as f:
            self.mapping = yaml.safe_load(f)

    def _fetch_core(self, table: str) -> pd.DataFrame:
        return pd.read_sql(f"SELECT * FROM `{table}`", self.core_engine)

    def _fetch_phys(self, table: str) -> pd.DataFrame:
        return pd.read_sql(f"SELECT * FROM `{table}`", self.phys_engine)

    # Copy the DataFrame and for each column in cfg, apply its formula.
    def _apply_formulas(self, df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
        out = df.copy()
        for col, col_cfg in cfg["columns"].items():
            func     = FORMULA_REGISTRY[col_cfg["formula"]]
            args     = col_cfg.get("args", [])

            # Build a row-wise call
            def apply_fn(row, func=func, args=args):
                vals = []
                for a in args:
                    vals.append(row[a])
                return func(*vals)

            out[col] = out.apply(apply_fn, axis=1)

        return out
    
    # Insert or update into element_database_anal.<table> using a temp table.
    def _upsert_anal(self, df: pd.DataFrame, table: str, pk: str):
        tmp = f"_tmp_{table}"
        with self.anal_engine.begin() as conn:
            # drop old temp
            conn.execute(text(f"DROP TABLE IF EXISTS `{tmp}`;"))
            # create it
            df.to_sql(tmp, conn, if_exists="fail", index=False)
            # build upsert
            cols    = ", ".join(f"`{c}`" for c in df.columns)
            updates = ", ".join(f"`{c}`=VALUES(`{c}`)"
                                for c in df.columns if c != pk)
            conn.execute(text(f"""
                INSERT INTO `{table}` ({cols})
                SELECT {cols} FROM `{tmp}`
                ON DUPLICATE KEY UPDATE {updates};
            """))
            # clean up
            conn.execute(text(f"DROP TABLE `{tmp}`;"))

    def run(self):
        # Only implement Beam_Capacity here for this version; other tables can be empty passes
        if "Beam_Capacity" in self.mapping:
            cfg = self.mapping["Beam_Capacity"]

            # Pull geometry + concrete strength from core
            df_geom = pd.read_sql(
                "SELECT Product_ID, Reinf_ID, Strength_Class FROM Beam_Geometry",
                self.core_engine
            )
            df_ck = pd.read_sql(
                "SELECT Strength_Class, f_ck AS fck_MPa FROM Concrete_Props",
                self.core_engine
            )
            df_geom = df_geom.merge(df_ck, on="Strength_Class", how="left")

            # Pull reinforcement grade from core, and check uniformity
            df_r = pd.read_sql(
                "SELECT Reinf_ID, Steel_Grade FROM Beam_Long_Reinf",
                self.core_engine
            )
            # Warn if any Reinf_ID has >1 grade
            bad = df_r.groupby("Reinf_ID")["Steel_Grade"].nunique()
            varying = bad[bad>1]
            if not varying.empty:
                print(f"[warn] Reinf_IDs with multiple steel grades: {list(varying.index)}")
            # Reduce to one grade per Reinf_ID
            df_r = df_r.drop_duplicates(["Reinf_ID"]) 

            # Map to f_yk
            df_sy = pd.read_sql(
                "SELECT Steel_Grade, f_yk AS fyk_MPa FROM Steel_Props",
                self.core_engine
            )
            df_r = df_r.merge(df_sy, on="Steel_Grade", how="left")

            # Pull areas & depth layer‐wise from phys
            df_lp = pd.read_sql(
                "SELECT Reinf_ID, bar_area_mm2, effective_depth_mm "
                "  FROM Beam_Long_Reinf",
                self.phys_engine
            ).sort_values("effective_depth_mm", ascending=False)

            # Pivot to get first row = tensile (As1) and second = compressive (As2)
            def pivot_layers(grp):
                a1 = grp.iloc[0]["bar_area_mm2"]
                a2 = grp.iloc[1]["bar_area_mm2"] if len(grp)>1 else 0.0
                d  = grp.iloc[0]["effective_depth_mm"]
                dp = grp.iloc[1]["effective_depth_mm"]
                return pd.Series({"As1_mm2": a1, "As2_mm2": a2, "d_mm": d, "dp_mm": dp})

            df_lp2 = df_lp.groupby("Reinf_ID").apply(pivot_layers).reset_index()

            # Assemble into one table keyed by Reinf_ID
            df = (
                df_r
                .merge(df_lp2, on="Reinf_ID", how="inner")
                .merge(df_geom, on="Reinf_ID", how="inner")  # brings in Product_ID & fck
            )

            # Pull b_mm from phys layer and merge on Product_ID
            df_b = pd.read_sql(
                "SELECT Product_ID, total_width_mm AS b_mm "
                "  FROM Beam_Geometry",
                self.phys_engine
            )
            df = df.merge(df_b, on="Product_ID", how="left")

            # Compute bending capacities
            df_cap = self._apply_formulas(df, cfg)

            # Prune & upsert
            keep = [cfg["pk"], "Reinf_ID"] + list(cfg["columns"].keys())
            df_cap = df_cap[keep]
            self._upsert_anal(df_cap, "Beam_Capacity", pk=cfg["pk"])

        # Repeat similar empty stubs for the other capacity tables --
        for tbl in ("Wall_Capacity","Column_Capacity",
                    "1W_Slab_Capacity","2W_Slab_Capacity","HCS_Capacity"):
            if tbl in self.mapping:
                print(f"[skip] no formulas for {tbl} in this proof-of-concept")