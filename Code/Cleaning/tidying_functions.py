import pandas as pd
import numpy as np
import math

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
    
def remove_bad_rowscols(dfd):
    for i, cdf in dfd.items():
        dfd[i] = cdf.dropna(axis = 1, how = 'all')
        for j, k in cdf.iterrows():
            if len(set(k.values)) <= 3:
                dfd[i] = dfd[i].drop(j)
    to_del = [i for i in dfd if len(dfd[i].columns) == 1]
    for key in to_del:
        del dfd[key]
    
def find_header_exceptions(dfd):
    substrings = ['NAME', 'Name']
    ls = []
    for i, cdf in dfd.items():
        try:
            if not any(y in x for x in cdf.drop(columns="CompID").iloc[0].to_numpy(na_value = '') for y in substrings):
                ls.append(cdf.iloc[0].values[0])
        except TypeError as e:
            print(e)
    return ls

def fix_headers_custom(bad_heads, dfd):
    #Lingering superfluous top row - 24, 74, 75, 95, 97, 177, 195, 463(x2), 
    #nan where name should be - 36, 187, 214(and sex)
    #Separate rows for lifts and attempt# - 45, 61, 72, 166
    #Name column called something else (e.g. "Lifter") - 59, 107, 129, 201
    #Header row completely missing - 706
    #Strange format - 829
    #CompID is just the compId number - All
    for compid in bad_heads:
        if compid in [24, 74, 75, 95, 97, 177, 195, 463]:
            dfd[compid] = dfd[compid].iloc[1:]
            if compid == 463:
                dfd[compid] = dfd[compid].iloc[1:]
        elif compid in [36, 187, 214]:
            dfd[compid].iat[0, 1] = "NAME"
            if compid == 214:
                dfd[compid].iat[0, 2] = "SEX"
        elif compid in [45, 61, 72, 166]:
            dfd[compid] = dfd[compid].iloc[1:]
        elif compid in [59, 107, 129, 201]:
            dfd[compid].iat[0, 1] = "NAME"
        elif compid in [706]:
            new_row = pd.DataFrame({'CompID': 706, 'Column3': "NAME", 'Column4': "DOB", 
                                   'Column5': "SEX", 'Column6': "BWT",
                                    'Column7': "SQ1", 'Column9': "SQ2", 'Column11': "SQ3",
                                     'Column13': "BP1", 'Column15': "BP2", 'Column17': "BP3",
                                     'Column19': "DL1", 'Column21': "DL2", 'Column23': "DL3",
                                     'Column25': "TOTAL", 'Column27': "WILKS"}, index=[25620])
            dfd[compid] = pd.concat([new_row, dfd[compid]])
        elif compid in [829]:
            del dfd[compid]
            
    #Fix CompID column
    for i, cdf in dfd.items():
        dfd[i] = dfd[i].astype(str)
        dfd[i].iat[0, 0] = "CompID"
        if dfd[i].iat[0, 1] == '.':
            dfd[i].iat[0, 1] = "Place"
    
def promote_headers(dfd):
    for i, cdf in dfd.items():
        dfd[i].columns = cdf.iloc[0]
        dfd[i] = dfd[i].iloc[1:]

def col_name_count(dfd, names):
    name_freq = {}
    for name in names:
        count = 0
        ls = []
        for k, cdf in dfd.items():
            if name in cdf.columns.to_list():
                count += 1
                ls.append(k)
        name_freq[name] = (count, ls)
    return name_freq

# def test(dfd, words):
#     Main = {}
#     for main in words.columns.to_list():
#         name_freq = {}
#         for name in words[main].to_list():
#             if type(name) == float and math.isnan(name):
#                 continue
#             count = 0
#             ls = []
#             for k, cdf in dfd.items():
#                 if name.strip()[1:-1] in cdf.columns.to_list():
#                     count += 1
#                     ls.append(k)
#             name_freq[name] = (count, ls)
#         Main[main] = name_freq
#     return Main
    

if __name__ == "__main__":
    #Read data
    df = pd.read_csv("../../Data/Raw_Full.csv", engine = 'python')
    
    #Separate links and save as separated CSV
    comp_links, df = separate_links(df)
    comp_links.to_csv("../../Data/Comp_Links.csv", index = False)
    
    #Remove school competitions
    df = df[~df['CompID'].isin(check_for_substrings(["School"], comp_links))]
    
    #Split df into dictionary of dfs for each competition
    dfdict = full_split(df)
    
    #Find comps with equipped lifters
    Eqp_Words = ["EQD", "EQP", "Equip", "EQUP"]
    Equipped_Comps = check_for_substrings(Eqp_Words, df)
    
    #Remove blank columns and superfluous rows, and deletes blank dataframes
    remove_bad_rowscols(dfdict)
    
    #Now first row should be header values. We'll check for exceptions manually
    bad_header_dfs = find_header_exceptions(dfdict)
    print("Broken headers: ", bad_header_dfs) # = [24, 36, 45, 59, 61, 72, 74, 75, 95, 97, 107, 129, 166, 177, 187, 195, 201, 214, 463, 706, 829] have bad headers
    
    #Fix broken headers
    fix_headers_custom(bad_header_dfs, dfdict) #NOTE: Data-specific implementation
    
    #Check fix worked
    bad_header_dfs = find_header_exceptions(dfdict)
    print("Broken headers: ", bad_header_dfs)
    
    #Promote headers
    promote_headers(dfdict)
    
    #Check the full list of headers in each row
    col_names = []
    for k, cdf in dfdict.items():
        col_names.extend(cdf.columns.to_list())
    print("Headers set: ", sorted(set(col_names))) #Sorted these headers into groups manually (Semantics.csv)
    
    #Found count of instances of each of these
    header_name_freq = col_name_count(dfdict, col_names)
    # sem = pd.read_csv("../../Data/Semantics.csv", )
    # testdf = test(dfdict, sem)
    
    #By inspection, these mostly appear to be variables, apart from nan, which requires further investigation
    
    