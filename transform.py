import os
import pandas as pd
import openpyxl
from read_mail import today, create_folder_if_not_exists
from extract import path, list_file_paths
import warnings

warnings.filterwarnings("ignore")

# CMDB Path
cmdb_path = 'C:/Users/svanruijven/PycharmProjects/ODW/data/stamdata/Areaal CMDB ODW-WNN v1.0.xlsx'

# Settings
source_path = path

# Directory
directory = f"MTM logfiles {today}"
# Parent directory path
parent_dir = 'C:/Users/svanruijven/PycharmProjects/ODW/data/clean/'
# Path
path = os.path.join(parent_dir, directory)


def load_clean_cmdb():
    """
    Load the CMDB dataset into a Pandas DataFrame and create an extra 'hm' column
    """
    df = pd.read_excel(cmdb_path, usecols=['entityid', 'ci-type', 'asset', 'bps-locatie', 'wegsoort', 'wegdeelletter',
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
    cols = ['entityid', 'asset', 'ci-type', 'beeld', 'fout', 'msi_type', 'vanaf', 'tijd', 'duur', 'wegsoort', 'weg', 'baanpositie', 'hm', 'baansoort', 'dvk', 'strooknummer_new', '_merge']
    df_final = df[cols]
    return df_final


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
    df_cmdb = load_clean_cmdb()
    print("[Transform] Filter CMDB data for lamp logfiles")
    df_cmdb_lamp = filter_cmdb(df_cmdb, 'VKS signaalgevers')
    print("[Transform] Create a list of paths per logfile")
    list_path = list_file_paths(source_path)
    print("[Transform] Creating new folder")
    create_folder_if_not_exists(path)
    print("[Transform] Load and clean the lamp logfile.CSV")
    df_log_lamp = load_clean_lamp_csv(list_path[0])
    print("[Transform] Performing Left Inner Join on lamp logfile and CMDB dataset")
    # print(df_log_lamp.info())
    # print(df_cmdb_lamp.info())
    lamp_left_join = merge_lamplog_cmdb(df_log_lamp, df_cmdb_lamp)
    print("[Transform] Left Inner Join successfully executed!")
    print("[Transform] Perform some final cleaning on the dataset")
    df_final = clean_merged_lamp_df(lamp_left_join)
    print("[Transform] Saving final dataset")
    save_final_dataset(df_final)
    print("[Transform] End")



