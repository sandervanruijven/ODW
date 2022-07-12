import os
import pandas as pd
import datetime
from read_mail import today, path, create_folder_if_not_exists

# Variable date of today
today = today

# Settings
source_path = path

# Directory
directory = f"MTM logfiles {today}"
# Parent directory path
parent_dir = 'C:/Users/svanruijven/PycharmProjects/ODW/data/raw/'
# Path
path = os.path.join(parent_dir, directory)


def read_log_file(file_path):
    """
    Read the logfile per line and create Pandas DataFrame
    """
    with open(file_path, 'r') as f:
        data = f.readlines()
    df = pd.DataFrame(data)
    return df


def list_file_paths():
    """
    Get all specific file paths for each logfile and save as a list
    """
    for file in os.listdir(source_path):
        # Check whether filename contains 'lamp'
        if file.startswith('lamp'):
            file_path_lamp = f"{source_path}/{file}"
        elif file.startswith('det'):
            file_path_det = f"{source_path}/{file}"
        elif file.startswith('msi'):
            file_path_msi = f"{source_path}/{file}"
        else:
            print(f'File: {file} not found!')
    return file_path_lamp, file_path_det, file_path_msi


def clean_save_raw_lamp_data(df):
    """
    Clean the lamp logging data and save the result as a .csv file
    """
    df = df[0].str.split('|', expand=True)
    df.drop([0, 11], axis=1, inplace=True)
    df.drop([0], axis=0, inplace=True)
    cols = {1: 'weg', 2: 'zijde', 3: 'dvk', 4: 'km', 5: 'strook',
            6: 'vanaf', 7: 'tijd', 8: 'beeld', 9: 'fout', 10: 'msi_type'}
    df.rename(columns=cols, inplace=True)
    for i in df.columns:
        if df[i].dtype == 'object':
            df[i] = df[i].map(str.strip)
    df['vanaf'] = pd.to_datetime(df['vanaf'])
    df['maand'] = pd.DatetimeIndex(df['vanaf']).month
    df['dag'] = pd.DatetimeIndex(df['vanaf']).day
    df['bps'] = df['weg'] + " " + df['zijde'] + " " + \
                df['dvk'] + " " + df['km'] + " " + df['strook']
    df['bps'] = df['bps'].replace(r'\s+', ' ', regex=True)

    today = datetime.datetime.now()
    today_string = today.strftime("%d-%m-%Y")

    def numOfDays(today, vanaf):
        return (today - vanaf).days

    duur = []
    for row in df['vanaf']:
        value = numOfDays(today, row)
        duur.append(value)

    df['duur'] = duur
    column_names = ['duur', 'vanaf', 'tijd', 'maand', 'dag', 'bps',
                    'weg', 'zijde', 'dvk', 'km', 'strook', 'beeld', 'fout', 'msi_type']
    df = df.reindex(columns=column_names)
    df.to_csv(f"{path}/lamp_{today_string}.csv")


def main():
    """
    Main function called inside the execute.py script
    """
    print("[Extract] Start")
    print("[Extract] Create a list of paths per logfile")
    list_path = list_file_paths()
    print("[Extract] Creating new folder")
    create_folder_if_not_exists(path)
    print("[Extract] Create Pandas DataFrame with data per logfile")
    df_lamp = read_log_file(list_path[0])
    df_det = read_log_file(list_path[1])
    df_msi = read_log_file(list_path[2])
    print(f"[Extract] Cleaning data")
    print(f"[Extract] Saving data")
    clean_save_raw_lamp_data(df_lamp)
    print(f"[Extract] End")