import pandas as pd

df = pd.read_csv("../Data/v3Clean_TypeCOnly.csv", engine = 'python', keep_default_na=False)

count = 0
for col in ['SQ 1', 'SQ 2', 'SQ 3', 'BP1', 'BP 2', 'BP 3', 'DL 1', 'DL 2', 'DL 3']:
    for i in range(df[col].size):
        temp = df[col][i].replace('.','')
        if not temp.isnumeric() and not temp == '' and not 'x' in temp:
            df[col][i] = df[col][i].split(' ')[0]
            
df.to_csv("../Data/v4Clean_TypeCOnly.csv", index_label = 'Index')