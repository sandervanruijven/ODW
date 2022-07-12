import pandas as pd
import openpyxl
from read_mail import today

# CMDB Path
cmdb_path = 'C:/Users/svanruijven/PycharmProjects/ODW/data/stamdata/Areaal CMDB ODW-WNN v1.0.xlsx'

def load_clean_cmdb():
    """
    Load the CMDB dataset into a Pandas DataFrame and create an extra 'hm' column
    """
    df = pd.read_excel(cmdb_path, usecols=['entityid', 'ci-type', 'asset', 'bps-locatie', 'wegsoort', 'wegdeelletter',
                            'wegnummer', 'hm-bord', 'afstand-tot-hm-bord', 'baannummer', 'baansoort',
                            'baanpositie', 'dvk-letter', 'strooknummer', 'rd-locatie-x', 'rd-locatie-y'])
    df['hm'] = df['hm-bord'].astype(str) + df['afstand-tot-hm-bord'].astype(str)
    df['hm'] = df['hm'].str.rstrip('.0')
    return df


def filter_cmdb(df, ci_type):
    """
    Apply ci filter on CMDB DataFrame and return a filtered DataFrame
    """
    df = df.loc[df['ci-type'] == ci_type]
    df.reset_index(inplace=True)
    df['strooknummer_new'] = df['asset'].str[-1] # Only works on VKS Signaalgevers
    return df


def main():
    """
    Main function called inside the execute.py script
    """
    print("[Transform] Start")
    print("[Transform] Load and clean the CMDB dataset")
    df_cmdb = load_clean_cmdb()
    print("[Transform] Filter CMDB data for lamp logfiles")
    df_cmdb_lamp = filter_cmdb(df_cmdb, 'VKS signaalgevers')
