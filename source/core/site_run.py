# import connector and packages
import mysql.connector
import pandas as pd
import numpy as np

from core.tables.Donor_Building import donor_building_table 
from core.tables.Circularity_Data import circul_data_table


# Connect to server host
def load_site(
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
    site = pd.read_excel(file_path, sheet_name="Building Data")

    # Clean NaNs
    site.replace({np.nan: None}, inplace=True)

    # Format records + SQL
    site_tuples, siteData_insert = donor_building_table(site)    # Donor Building Metadata table
    circul_tuples, circulData_insert = circul_data_table(site)      # Circularity Data table

    # Toggle between 0/1 to turn off/on Foreign Key restrictions.
    cur.execute("SET FOREIGN_KEY_CHECKS=0;")

    # Bulk INSERT in the correct order
    for insert, tups in [
        (siteData_insert, site_tuples),
        (circulData_insert, circul_tuples),
    ]:
        if tups and insert:                            # only run if non‐empty
            cur.executemany(insert, tups)
    conn.commit()
    conn.close()