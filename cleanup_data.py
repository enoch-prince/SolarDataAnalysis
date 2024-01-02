from pathlib import Path
import argparse
import sys
from typing import Generator
import pandas as pd

DEBUG = True
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
    if DEBUG:
        args.log.write('File path given %s\n' % args.csv_folder_path)
    return args.csv_folder_path


def resolveDataFolderPaths(path_str: str):
    path = Path(path_str)

    path_exists = path.exists()
    if DEBUG:
        print("\nDoes path exist: ", path_exists, "\n")

    if path_exists:
        return path.glob("**")

def resolveCSVFilePaths(folder_path: Path) -> Generator[Path, None, None] | None:
    return folder_path.glob("*.csv")


def processCSVFiles(folder_name:str, csv_glob: Generator[Path, None, None]):
    for csv_path in csv_glob:
        if DEBUG:
            print("Processing file:", csv_path.resolve())
        df = pd.read_csv(csv_path)
        if DEBUG:
            print("Dropping columns specified......\n")
        columns_to_drop_exists = all([True if column in df.columns else False for column in columns_to_drop])
        if not columns_to_drop_exists:
            if DEBUG:
                print(f"Skipping file {csv_path.resolve()} because columns: {columns_to_drop} does not exist in file")
            continue
        
        df.drop(columns_to_drop, axis=1, inplace=True)

        if DEBUG:
            print("Selecting data range from 9am - 4pm .......\n")
        df = df.iloc[row_start:row_end]
        if DEBUG:
            print("Writing modified data to another file in the /Data in the CWD...\n")
        
        # Save Modified Data
        df.to_csv(f"Data/{folder_name}/{csv_path.name}", index=False)
        if DEBUG:
            print(f"Data/{folder_name}/{csv_path.name} DONE!!!\n--------------\n")
    


def main():
    path_str = parseCmdLineForCSVPath()
    folder_glob = resolveDataFolderPaths(path_str)
    
    if folder_glob is not None:
        for folder_path in folder_glob:
            new_path = Path(f"Data/{folder_path.name}")
            if not new_path.exists():
                new_path.mkdir()
            csv_file_glob = resolveCSVFilePaths(folder_path)
            if csv_file_glob is None:
                continue
            processCSVFiles(folder_path.name, csv_file_glob)
    

if __name__ == "__main__":
    main()