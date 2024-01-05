from pathlib import Path
import pandas as pd

import utils

# TODO 1
# Average all the data for each column for a single CSV file into a single row in a df
# Do same for all the CSV files in a single folder
# Save the new df to a single csv file
# Do same for all the folders

# TODO Breakdown #1 - Average each column
# - Read the csv file into a df
# - Get the column names in a list
# - Use the column names to find the average each column


def calculateMeanOfEachColumn(df: pd.DataFrame) -> pd.Series:
    df.drop(["Started", "Ended"], axis=1, inplace=True)
    df = replaceINFwithZero(df)
    series = df.mean()
    return series
 
def replaceINFwithZero(df: pd.DataFrame):
    return df.replace(to_replace=["  INF", "ERR"], value=0.0).astype(float)
    # return df.replace(to_replace="ERR", value=0.0).astype(float)

def save_to_file(filename: str, df: pd.DataFrame):
    df.to_csv(filename, index=False)


def main():
    folder_name, folder_glob = utils.resolveDataFolderPaths("./Data")
    
    if folder_glob is None:
        print("Folder ./Data is empty")
        exit(1)
    
    new_folder_path = Path("Analyses")
    if not new_folder_path.exists():
        new_folder_path.mkdir()

    for folder_path in folder_glob:
        if folder_path.name is folder_name:
            continue
        
        csv_paths = utils.resolveCSVFilePaths(folder_path)
        if csv_paths is None:
            continue
        data = []
        columns = ["Day"]
        for csv_path in csv_paths:
            datum = [csv_path.name[:2]]
            df = pd.read_csv(csv_path)
            series = calculateMeanOfEachColumn(df)
            datum[1:] = series.values
            data.append(datum)
            if len(columns) <= 1:
                columns[1:] = series.index

        df = pd.DataFrame(data, columns=columns)
        save_to_file(f"Analyses/{folder_path.name}.csv", df)

    # print(df)

if __name__ == "__main__":
    main()