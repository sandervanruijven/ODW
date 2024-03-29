import os
import pandas as pd
import numpy as np
import openpyxl
import string
from read_mail import today, create_folder_if_not_exists
from extract import path, list_file_paths
import warnings

warnings.filterwarnings("ignore")

# CMDB dataset Path
cmdb_path = 'C:/Users/svanruijven/PycharmProjects/ODW/data/stamdata/Areaal CMDB ODW-WNN v1.0.xlsx'
# XY dataset Path
xy_path = 'C:/Users/svanruijven/PycharmProjects/ODW/data/stamdata/Hectometerborden.csv'
# Settings
source_path = path

# Directory
directory = f"MTM logfiles {today}"
# Parent directory path
parent_dir = 'C:/Users/svanruijven/PycharmProjects/ODW/data/clean/'
# Path
path = os.path.join(parent_dir, directory)


def load_clean_cmdb(path):
    """
    Load the CMDB dataset into a Pandas DataFrame and create an extra 'hm' column
    """
    df = pd.read_excel(path, usecols=['entityid', 'ci-type', 'asset', 'bps-locatie', 'wegsoort', 'wegdeelletter',
                            'wegnummer', 'hm-bord', 'afstand-tot-hm-bord', 'baannummer', 'baansoort',
                            'baanpositie', 'dvk-letter', 'strooknummer', 'rd-locatie-x', 'rd-locatie-y'])
    df['hm'] = df['hm-bord'].astype(str) + df['afstand-tot-hm-bord'].astype(str)
    df['hm'] = df['hm'].str.rstrip('.0')
    df['hm'] = pd.to_numeric(df['hm'], errors='coerce')
    return df


def filter_cmdb(df, ci_type):
    """
    Apply ci filter on CMDB DataFrame and return a filtered DataFrame
    """
    df = df.loc[df['ci-type'] == ci_type]
    df.reset_index(inplace=True)
    df['strooknummer_new'] = df['asset'].str[-1] # Only works on VKS Signaalgevers
    df['wegnummer'] = df['wegnummer'].astype(int)
    df['wegnummer'] = df['wegnummer'].astype(str)
    return df


def load_clean_lamp_csv(path):
    """
    Load the lamp.csv from path do some cleaning and return a DataFrame
    """
    df = pd.read_csv(path)
    df['strook'] = df['strook'].astype(str)
    df['weg'] = df['weg'] = df['weg'].str.replace(r'(A|N)', '', regex=True)
    df['zijde'] = df['zijde'].fillna('N')
    return df


def merge_lamplog_cmdb(df_lamp, df_cmdb):
    """
    Merge the lamp logfiles and CMDB data with a Left Inner Join.
    This returns a DataFrame "left_join" with only those rows that have common characteristics.
    If not it will return NaN values on the CMDB columns.
    """
    left_join = df_lamp.merge(df_cmdb,
                     how='left',
                     left_on=['km', 'weg', 'strook', 'zijde', 'dvk'],
                     right_on=['hm', 'wegnummer', 'strooknummer_new', 'baanpositie', 'dvk-letter'],
                     indicator=True)
    return left_join


def clean_merged_lamp_df(df):
    """
    Perform some final cleaning and return a final DataFrame "df_final"
    """
    list = []
    for index, row in df.iterrows():
        if row['wegsoort'] == 'RW':
            list.append(f"A{row['wegnummer']}")
        elif row['wegsoort'] == "PW":
            list.append(f"N{row['wegnummer']}")
        else:
            list.append(f"{row['wegnummer']}")
    df['weg'] = list
    df['strooknummer'] = df['strooknummer'].astype(str).str.rstrip('.0')
    df['dvk'] = df['dvk'].fillna('n.v.t.')
    df['baanpositie'] = df['baanpositie'].replace('N', '')
    cols = ['entityid', 'asset', 'ci-type', 'beeld', 'fout', 'msi_type', 'vanaf', 'tijd', 'duur', 'wegsoort', 'weg', 'baanpositie', 'hm', 'hm-bord', 'baansoort', 'dvk', 'strooknummer_new', '_merge']
    df_final = df[cols]
    return df_final


def load_clean_xy(path):
    """
    Load the Hectometerborden dataset from ESRI into a Pandas DataFrame and do some cleaning.
    Next add new column with correct rijrichting notations and return a DataFrame for merging with CMDB
    """
    df = pd.read_csv(path)
    df[['del', 'Wegnummer', 'del2']] = df['Label'].str.split(r'([A-Z]{1}[0-9]{1,3}\s)', expand=True)
    df['WegZijdeKort'] = df['WegZijdeKort'].fillna('N')
    df['HECTOLETTE'] = df['HECTOLETTE'].str.strip()
    df['HECTOLETTE'] = df['HECTOLETTE'].fillna('n.v.t.')
    df['HECTOLETTE'] = df['HECTOLETTE'].replace('', 'n.v.t.')
    dvk = list(string.ascii_lowercase)
    list2 = []
    for index, row in df.iterrows():
        if row['HECTOLETTE'] not in dvk:
            if row['WegZijdeKort'] == 'Li' or row['WegZijdeKort'] == 'Links':
                list2.append('L')
            elif row['WegZijdeKort'] == 'Re' or row['WegZijdeKort'] == 'Rechts':
                list2.append('R')
            else:
                list2.append('N')
        else:
            list2.append('N')
    df['rijrichting'] = list2
    df_xy = df[['AN1', 'RijkswegNr', 'Wegnummer', 'rijrichting', 'HectoWaard', 'HECTOLETTE', 'X', 'Y']]
    df_xy['Wegnummer'] = df_xy['Wegnummer'].str.strip()
    return df_xy


def merge_cmdb_lamp_xy(df_cmdb_lamp, df_xy):
    """
    Merge the CMDB lamp DataFrame with the XY DataFrame with a Left Inner Join.
    """
    left_join3 = df_cmdb_lamp.merge(df_xy,
                           how='left',
                           left_on=['weg', 'baanpositie', 'hm-bord', 'dvk'],
                           right_on=['Wegnummer', 'rijrichting', 'HectoWaard', 'HECTOLETTE'],
                           indicator=False)
    return left_join3


def add_cat(df):
    """
    This function adds a new column to the Logging DataFrame with
    the Category of failure mapping conform conversation with
    Boonsong Dekker and Jan Eikelenboom on 26-07-2022
    """
    list = []
    df2 = df.groupby('asset', axis=0) # Group the DataFrame by asset
    assets = df['asset'].unique().tolist() # Create a list with unique assets
    assets.remove(np.nan) # Remove nan values from list
    assets.sort()
    for name, group in df2:
        if 'PR' in group['beeld'].values or 'PL' in group['beeld'].values:
            list.append('cat 2')
        elif 'LAMPX1' in group['beeld'].values and 'LAMPX2' in group['beeld'].values:
            list.append('cat 2')
        elif 'LAMPX1' in group['beeld'].values and 'LAMPX2' in group['beeld'].values and 'LAMPX3' in group['beeld'].values:
            list.append('cat 2')
        elif 'LAMPX1' in group['beeld'].values or 'LAMPX2' in group['beeld'].values or 'LAMPX3' in group['beeld'].values:
            list.append('cat 4')
        else:
            list.append('cat 4')
    dict = {'asset':assets,'categorie':list} # Combine lists to dict
    df_cat = pd.DataFrame(dict)
    return df_cat


def merge_cat_clean(df_lamp, df_cat):
    """
    Merge the lamp logfiles and category DataFrame with a Left Inner Join
    This returns a DataFrame "left_join2" with only those rows that have common characteristics.
    If not it will return NaN values on the Category columns.
    """
    left_join2 = df_lamp.merge(df_cat,
                              how='left',
                              left_on=['asset'],
                              right_on=['asset'],
                              indicator=False)
    return left_join2


def save_final_dataset(df):
    """
    Save the final dataset
    """
    df.to_csv(f"{path}/clean_lamp_{today}.csv")


def main():
    """
    Main function called inside the execute.py script
    """
    print("[Transform] Start")
    print("[Transform] Load and clean the CMDB dataset")
    df_cmdb = load_clean_cmdb(cmdb_path)
    print("[Transform] Filter CMDB data for lamp logfiles")
    df_cmdb_lamp = filter_cmdb(df_cmdb, 'VKS signaalgevers')
    print("[Transform] Create a list of paths per logfile")
    list_path = list_file_paths(source_path)
    print("[Transform] Creating new folder")
    create_folder_if_not_exists(path)
    print("[Transform] Load and clean the lamp logfile.CSV")
    df_log_lamp = load_clean_lamp_csv(list_path[0])
    print("[Transform] Performing Left Inner Join on lamp logfile and CMDB dataset")
    lamp_left_join = merge_lamplog_cmdb(df_log_lamp, df_cmdb_lamp)
    print("[Transform] Left Inner Join successfully executed!")
    print("[Transform] Perform some final cleaning on the merged dataset")
    df_merge_clean = clean_merged_lamp_df(lamp_left_join)
    print("[Transform] Load and clean the XY ESRI dataset")
    df_xy = load_clean_xy(xy_path)
    print("[Transform] Performing Left Inner Join on Filtered lamp CMDB dataset and XY ESRI dataset")
    df_cmdb_lamp_xy = merge_cmdb_lamp_xy(df_merge_clean, df_xy)
    print("[Transform] Define the right Failure category per Asset")
    df_cat = add_cat(df_cmdb_lamp_xy)
    print("[Transform] Performing Left Inner Join on Clean Merged dataset and Failure Category dataset")
    df_final = merge_cat_clean(df_cmdb_lamp_xy, df_cat)
    print("[Transform] Left Inner Join successfully executed!")
    print("[Transform] Saving final dataset")
    save_final_dataset(df_final)
    print("[Transform] End")



