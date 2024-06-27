import csv

import pandas as pd

def get_names_from_csv_pandas(filename, chunksize=1000):
  names_list = []
  for chunk in pd.read_csv(filename, chunksize=chunksize):
    names_list.extend(chunk.iloc[:, 0].tolist())  # Assuming names are in first column
  return names_list



