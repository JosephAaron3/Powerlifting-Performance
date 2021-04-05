import pandas as pd
import numpy as np

df = pd.read_csv("./Data/v4Clean_TypeCOnly.csv", index_col = 0, na_filter = '')

for col in ['SQ 1', 'SQ 2', 'SQ 3', 'BP1', 'BP 2', 'BP 3', 'DL 1', 'DL 2', 'DL 3']:
    df[col + ' outcome'] = ~df[col].str.contains("x|^$", regex = True).astype(bool)
    df[col] = df[col].str.replace('x', '')

df = df.replace(r'^\s*$', np.NaN, regex=True)
for col in ['SQ 1', 'SQ 2', 'SQ 3', 'BP1', 'BP 2', 'BP 3', 'DL 1', 'DL 2', 'DL 3']:
    df[col] = df[col].astype(float)

df.to_csv("./Data/v5Clean_TypeCOnly.csv", index_label = 'Index')