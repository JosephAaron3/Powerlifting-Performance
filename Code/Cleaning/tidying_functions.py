import pandas as pd
import numpy as np

df = pd.read_csv("../../Data/Raw_Full.csv", engine = 'python')


def separate_links(df): # Separate comp link to remove redundency
     return df[["CompID", "Link"]].drop_duplicates(), df.drop(columns = ['Link'])

def full_split(df):
    return {k: v for k,v in df.groupby('CompID')}

def check_for_substrings(ls, df):
    Comps = []
    for col in df.drop(columns = ['CompID']):
        for substr in ls:
            Comps.extend(list(df[df[col].str.contains(substr, case = False,
                                                na = False)]['CompID'].values))
    return sorted(set(Comps))
    

if __name__ == "__main__":
    #Read data
    df = pd.read_csv("../../Data/Raw_Full.csv", engine = 'python')
    
    #Separate links and save as separated CSV
    comp_links, df = separate_links(df)
    comp_links.to_csv("../../Data/Comp_Links.csv", index = False)
    
    
    #Split df into dictionary of dfs for each competition
    dfdict = full_split(df)
    
    #Remove school competitions
    df = df[df['CompID'].isin(check_for_substrings(["School"], comp_links))]
    
    #Find comps with equipped lifters
    Eqp_Words = ["EQD", "EQP", "Equip", "EQUP"]
    Equipped_Comps = check_for_substrings(Eqp_Words, df)
    
    