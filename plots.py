import itertools
from pathlib import Path
import pandas as pd
# import numpy as np

# import seaborn as sns
import matplotlib.pyplot as plt

import utils

# TODO
# Find the data with appreciable amount of records that runs through all the months
# Pick time with peak hours
# Plot the IV characteristics for that peak hour 
# Add the relevant parameters: Panel temp, Ambient humi, Voc, Isc, Day, Month

MARKERS = itertools.cycle(('.','o','*','v','^','<','>','+'))
LINE_STYLE = itertools.cycle(('-', '--', '-.', ':'))
DAYPARTING = ["Morning", "Afternoon", "Late Afternoon"]

def subplots(df: pd.DataFrame, left_y: str, left_x:str, right_y:str, right_x:str):
    fig, ax1 = plt.subplots()
    ax2 = fig.add_subplot(111, label="second axes")
    ax2.set_facecolor("none")

    ax1.set_xlabel(left_x, color='red')
    ax1.set_ylabel(left_y, color='red')
    ax1.plot(df[left_x], df[left_y], color='red')
    ax1.tick_params(colors='red')

    ax2.set_xlabel(right_x, color='blue')
    ax2.set_ylabel(right_y, color='blue')
    ax2.plot(df[right_x], df[right_y], color='blue')
    ax2.xaxis.tick_top()
    ax2.xaxis.set_label_position('top') 
    ax2.yaxis.tick_right()
    ax2.yaxis.set_label_position('right')
    ax2.tick_params(colors='blue')

    for which in ["top", "right"]:
        ax2.spines[which].set_color("blue")
        ax1.spines[which].set_visible(False)
    for which in ["bottom", "left"]:
        ax1.spines[which].set_color("red")
        ax2.spines[which].set_visible(False)

    # fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show()


def plotSample():
    # df.plot(x="Started", y=["Panel Temp(°C)", "Ambient Hum(%)", "Irradience(W/m2)"],
    #     kind="line", title=f"Solar Irradience against Panel Temp & Ambient Humidity - Day {csv_path.stem}",
    #     xlabel="Time Started")
    # plt.savefig(f"Analyses/Figs/{csv_fig_folder.name}/panel_temp_humi_irradience.png")
    # plt.close()
    
    # df.plot(x="Started", y=["Voc(V)", "Isc(A)"], kind="line", title=f"Open Circuit Voltage & Short Circuit Current - Day {csv_path.name[:2]}", xlabel="Time Started")
    # plt.savefig(f"Analyses/Figs/{csv_fig_folder.name}/Voc_Isc.png")
    # plt.close()
    
    # df.plot(x="Started", y=["Wind Speed(m/s)", "Panel Temp(°C)"], kind="line", title=f"Wind Speed against Panel Temp - Day {csv_path.name[:2]}", xlabel="Time Started")
    # plt.savefig(f"Analyses/Figs/{csv_fig_folder.name}/wind_speed_panel_temp.png")
    # plt.close()
    
    # df.plot(x="Started", y=["Wind Speed(m/s)", "Ambient Hum(%)", "Irradience(W/m2)"], kind="line", title=f"Wind Speed against Ambient Humidity and Irradiance - Day {csv_path.name[:2]}", xlabel="Time Started")
    # plt.savefig(f"Analyses/Figs/{csv_fig_folder.name}/wind_speed_humi_irradience.png")
    # plt.close()
    pass

def plotParams():
    folder_name, folder_glob = utils.resolveDataFolderPaths("./Data")

    if folder_glob is None:
        print("Folder ./Data is empty")
        exit(1)
    
    fig_folder = Path(f"Analyses/Figs")
    if not fig_folder.exists():
        fig_folder.mkdir()
    
    for folder_path in folder_glob:
        if folder_path.name is folder_name:
            continue
        
        csv_fig_folder = Path(f"Analyses/Figs/{folder_path.name}")
        if not csv_fig_folder.exists():
            csv_fig_folder.mkdir()

        csv_paths = utils.resolveCSVFilePaths(folder_path)
        if csv_paths is None:
            continue

        for csv_path in csv_paths:
            df = pd.read_csv(csv_path)

            if df.shape[0] == 0:
                continue
            
            for timeofday in DAYPARTING:
                plotIVCharacteristics(df, csv_path, timeofday)
                savePlot(csv_fig_folder, f"IV_Characteristics_{csv_fig_folder.name}_{csv_path.name}_{timeofday}")


def plotIVCharacteristics(df: pd.DataFrame, data_path: Path, timeofday: str):
    # columns_to_drop = ["Floor Temp(°C)", "Wind Speed(m/s)", "North LDR(kΩ)", "East LDR(kΩ)", "South LDR(kΩ)", "West LDR(kΩ)", "Dust(µg/m3)", "Ended"]

    # df.drop(columns_to_drop, axis=1, inplace=True)

    df_iv = df.loc[:, "V1":"I20"]

    v_columns = [column for column in df_iv.columns if column.startswith("V")]
    i_columns = [column for column in df_iv.columns if column.startswith("I")]

    v_df = df_iv.drop(i_columns, axis=1)
    i_df = df_iv.drop(v_columns, axis=1)
    v_df_transposed = v_df.transpose()
    i_df_transposed = i_df.transpose()
    # columns_for_transposed_df = pd.to_datetime(df["Started"], format='%H:%M:%S').dt.time
    columns_for_transposed_df = df["Started"]
    v_df_transposed.columns = columns_for_transposed_df
    i_df_transposed.columns = columns_for_transposed_df

    fig, axis = plt.subplots()
    fig.set_size_inches(12.80, 6.60)
    axis.set_xlabel("Voltage (V)")
    axis.set_ylabel("Current (A)")
    
    dayparting = df["Dayparting"]
    trimmed_columns = [(columns_for_transposed_df[i], i) for i in columns_for_transposed_df.index if i%10 == 0] # select with intervals of 5

    columns_timeofday = [col for col in trimmed_columns if dayparting[col[1]] == timeofday]
    
    for column in columns_timeofday:
        axis.plot(v_df_transposed[column[0]], i_df_transposed[column[0]], label=column[0], marker=next(MARKERS), linestyle=next(LINE_STYLE))

    handles, _ = axis.get_legend_handles_labels()
    time_legend = plt.legend(title="Time", loc=(0.91,0.70)) #, bbox_to_anchor=(0.91,0.70))

    panel_temp_legend = plt.legend(handles, [
       df["Panel Temp(°C)"][col[1]] for col in columns_timeofday 
    ], title="Panel Temp(°C)", loc=(0.79,0.70)) #, bbox_to_anchor=(0.79,0.70))

    ambient_humi_legend = plt.legend(handles, [
       df["Ambient Hum(%)"][col[1]] for col in columns_timeofday 
    ], title="Ambient Hum(%)", loc=(0.655,0.70)) #, bbox_to_anchor=(0.655,0.70))

    isc_voc_legend = plt.legend(handles, [
       (df["Voc(V)"][col[1]], df["Isc(A)"][col[1]]) for col in columns_timeofday 
    ], title="Voc(V) | Isc(A)", loc=(1.025,0.70)) #, bbox_to_anchor=(1.025,0.70))

    axis.add_artist(time_legend)
    axis.add_artist(panel_temp_legend)
    axis.add_artist(ambient_humi_legend)

    fig.subplots_adjust(left=0.078, right=0.838)

    figtext_args = (0.5, 0.95, 
                f"Recorded Date: {data_path.stem}-{data_path.parts[-2]}-2023 | {timeofday}") 
  
    figtext_kwargs = dict(horizontalalignment ="center",  
                        fontsize = 12, color ="green",  
                        style ="italic", wrap = True)
    
    plt.figtext(*figtext_args, **figtext_kwargs)
    plt.title("Solar Panel IV Characteristics Under Varying Load")


def savePlot(path: Path, filename: str):
    plt.savefig(f"Analyses/Figs/{path.name}/{filename}.png", dpi=200)
    plt.close()


def main():
    plotParams()

    # df = pd.read_csv("Data/AUG/01.csv")
    # plotIVCharacteristics(df, Path("Data/AUG/01.csv"), "Afternoon")
    # savePlot(Path("Analyses/Figs/AUG"), "iv_AUG_01_afternoon2")
    # # mng = plt.get_current_fig_manager()
    # # mng.frame.Maximize(True)


if __name__ == "__main__":
    main()
   
