# SolarDataAnalysis

## Dependency

Pandas

```python
pip install pandas
```

## Running the script

Run the script using the command below:

```bash
python ./cleanup_data.py "path-to-folder-containing-folders-that-contain-csv-files"
```

The cleaned files are saved in the ```Data/``` directory in their respective folders.

### Next

Run the ```analyses.py``` file to calculate the averages of each column for the csv files for each month's set of data

```bash
python ./analyses.py
```
### Next

Run the ```plot.py``` file to plot the IV characteristics for the data for each month

```bash
python ./plots.py
```
