# import connector and packages
import mysql.connector
import pandas as pd
import numpy as np


# Connect to server host
def load_materials(
    file_path: str,
    host: str, port: int,
    user: str, password: str,
    database: str
):
    
    # Connect
    conn = mysql.connector.connect(
        host=host, port=port,
        user=user, password=password,
        database=database
    )
    cur = conn.cursor()

    # Read the sheets
    conc = pd.read_excel(file_path, sheet_name="Concrete")
    steel = pd.read_excel(file_path, sheet_name="Steel")

    # Clean NaNs
    for df in (conc, steel):
        df.replace({np.nan: None}, inplace=True)

    # Strip whitespaces and prefix country code to Class/Grade
    conc['Strength Class'] = (
        conc['Country'].str.upper()
        + '_'
        + conc['Strength Class']
            .astype(str)
            .str.replace(r'\s+', '', regex=True)
    )
    steel['Steel Grade'] = (
        steel['Country'].str.upper()
        + '_'
        + steel['Steel Grade']
            .astype(str)
            .str.replace(r'\s+', '', regex=True)
    )

    # Format Concrete & Steel Material Properties table + SQL
    conc_props = conc.loc[:, ["Strength Class", "Original Standard", "Year", "Country", "Characteristic Compressive Strength, fck (MPa)",
                                "Mean Compressive Strength, fcm (MPa)", "Measurement Method", "Characterisitic Tensile Strength, fctk (MPa)", 
                                "Mean Tensile Strength, fctm (MPa)", "Elastic Modulus, Ecm (GPa)", "Ultimate Crushing Strain, εcu1", 
                                "Thermal Expansion Coefficient (K-1)", "Density (kg/m3)", "Poisson Ratio", "Notes"]]
    
    steel_props = steel.loc[:, ["Steel Grade", "Original Standard", "Year", "Country", "Characteristic Yield Strength, fyk (MPa)",
                                "Characteristic Tensile Strength, fsu (MPa)", "Modulus of Elasticity, Es (GPa)", 
                                "Ultimate Strain, εsu", "Fracture strain,  εsf", "Measurement Length",
                                "Delivery", "Ductility Class", "Surface Profile", "Thermal Expansion Coefficient (K-1)", "Notes"]]
    
    conc_props_tups = [tuple(row) for row in conc_props.itertuples(index=False, name=None)]
    steel_props_tups = [tuple(row) for row in steel_props.itertuples(index=False, name=None)]

    # Insert queries
    conc_props_insert = "INSERT INTO Concrete_Props(Strength_Class, Original_Standard, Publication_Year, \
    Country, f_ck, f_cm, Measurement_Method, f_ctk, f_ctm, Elastic_Modulus, Ultimate_Strain, \
        Coefficient_Thermal_Exp, Density, Poisson_Ratio, Notes) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    steel_props_insert = "INSERT INTO Steel_Props(Steel_Grade, Original_Standard, Publication_Year, \
        Country, f_yk, f_su, Elastic_Modulus, Ultimate_Strain, Fracture_Strain, Measurement_Length, \
            Delivery, Ductility_Class, Surface_Profile, Coefficient_Thermal_Exp, Notes) \
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"


    # Toggle between 0/1 to turn off/on Foreign Key restrictions.
    cur.execute("SET FOREIGN_KEY_CHECKS=1;")

    # Bulk INSERT in the correct order
    for insert, tups in [
        (conc_props_insert, conc_props_tups),
        (steel_props_insert, steel_props_tups),
    ]:
        if tups and insert:
            cur.executemany(insert, tups)
    conn.commit()
    conn.close()