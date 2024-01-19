from pathlib import Path
import argparse
import sys
from typing import Generator
import pandas as pd
import numpy as np

import utils

columns_to_drop = ["Panel Ambient(°C)", "Floor Ambient(°C)", "Sys Temp(°C)", "Sys Hum(%)", "Vbat(V)"]
row_start = 173
row_end = 308

def parseCmdLineForCSVPath() -> str:
    parser = argparse.ArgumentParser(
        description='sum the integers at the command line')
    parser.add_argument(
        'csv_folder_path', metavar='str', type=str,
        help='an absolute path to the folder containing csv files')
    parser.add_argument(
        '--log', default=sys.stdout, type=argparse.FileType('w'),
        help='the file where the logs should be written')
    args = parser.parse_args()
    if utils.DEBUG:
        args.log.write('File path given %s\n' % args.csv_folder_path)
    return args.csv_folder_path

def processCSVFiles(folder_name:str, csv_glob: Generator[Path, None, None]):
    for csv_path in csv_glob:
        if folder_name is csv_path.name:
            continue
        if utils.DEBUG:
            print("Processing file:", csv_path.resolve())
        df = pd.read_csv(csv_path)

        if utils.DEBUG:
            print("Dropping columns specified......\n")
        columns_to_drop_exists = all([True if column in df.columns else False for column in columns_to_drop])
        if not columns_to_drop_exists:
            if utils.DEBUG:
                print(f"Skipping file {csv_path.resolve()} because columns: {columns_to_drop} does not exist in file")
            continue
        
        df.drop(columns_to_drop, axis=1, inplace=True)

        if utils.DEBUG:
            print("Selecting data range from 9am - 4pm .......\n")

        mask = ((df["Started"].values >= '09:00:00') & (df["Started"].values <= '16:05:00'))
        df = df.loc[mask]
        
        addDayparting(df)

        iv_column_names = [column for column in df.columns if column.startswith("IV")]
        for column in iv_column_names:
            splitIVdataIntoSeperateColumns(df, column)
        
        if utils.DEBUG:
            print("Writing modified data to another file in the /Data in the CWD...\n")

        # Save Modified Data
        df.to_csv(f"Data/{folder_name}/{csv_path.name}", index=False)
        if utils.DEBUG:
            print(f"Data/{folder_name}/{csv_path.name} DONE!!!\n--------------\n")
    

def splitIVdataIntoSeperateColumns(df: pd.DataFrame, column_name: str):
    iv_data_str_list = df[column_name].to_list()

    v_list = []
    i_list = []
    iv_pair_float_list = [[float(data.split(":")[0]), float(data.split(":")[1])]  for data in iv_data_str_list]

    for iv_pair in iv_pair_float_list:
        v_list.append(iv_pair[0])
        i_list.append(iv_pair[1])
    column_index = df.columns.tolist().index(column_name)
    
    df.insert(column_index, f"V{column_name[2:]}", v_list)
    df.insert(column_index+1, f"I{column_name[2:]}", i_list)
    df.drop([column_name], axis=1, inplace=True)

def addDayparting(df: pd.DataFrame):
    column_index = df.columns.tolist().index("Started")
    conditions = [(df["Started"] >= '09:00:00') & (df["Started"] < '12:00:00'),
                  (df["Started"] >= '12:00:00') & (df["Started"] < '15:00:00')]
    outputs = ["Morning", "Afternoon"]
    res = np.select(conditions, outputs, "Late Afternoon")
  
    df.insert(column_index+1, "Dayparting", res, True)


def main():
    path_str = parseCmdLineForCSVPath()
    folder_name, folder_glob = utils.resolveDataFolderPaths(path_str)

    data_dir_path = Path("Data")
    if not data_dir_path.exists():
        data_dir_path.mkdir()
    
    if folder_glob is not None:
        for folder_path in folder_glob:
            if folder_name is folder_path.name:
                continue
            new_path = Path(f"Data/{folder_path.name}")
            if not new_path.exists():
                new_path.mkdir()
            csv_file_glob = utils.resolveCSVFilePaths(folder_path)
            if csv_file_glob is None:
                continue
            processCSVFiles(folder_path.name, csv_file_glob)
    

if __name__ == "__main__":
    main()