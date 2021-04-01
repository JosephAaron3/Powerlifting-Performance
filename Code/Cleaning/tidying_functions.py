import pandas as pd
import numpy as np
import math
import seaborn as sb
import matplotlib.pyplot as plt

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
    
def remove_bad_rowscolstables(dfd):
    for i, cdf in dfd.items():
        dfd[i] = cdf.dropna(axis = 1, how = 'all')
        for j, k in cdf.iterrows():
            if len(set(k.values)) <= 3:
                dfd[i] = dfd[i].drop(j)
    to_del = [i for i in dfd if len(dfd[i].columns) == 1]
    for key in to_del:
        del dfd[key]
    
def find_header_exceptions(dfd):
    #Simply find dfs without "Name" in the top row - Naive method, but fine for this dataset
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
# =============================================================================
# Lingering superfluous top row - 24, 74, 75, 95, 97, 177, 195, 463(x2), 
# nan where name should be - 36, 187, 214(and sex)
# Separate rows for lifts and attempt# - 45, 61, 72, 166
# Name column called something else (e.g. "Lifter") - 59, 107, 129, 201
# Header row completely missing - 706
# Strange format - 829
# CompID is just the compId number - All
# =============================================================================
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
            
    #Fix '.' columns
    for i, cdf in dfd.items():
        dfd[i].iat[0,0] = -1 #For easy referencing later
        if dfd[i].iat[0, 1] == '.':
            dfd[i].iat[0, 1] = "Place"
    
def promote_headers(dfd):
    for i, cdf in dfd.items():
        dfd[i].columns = cdf.iloc[0]
        if (len(dfd[i][-1].shape) != 1):
            print("Error: Multiple columns named -1")
        dfd[i].rename(columns = {-1: "CompID"}, inplace = True)
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

def na_col_details(dfd):
    #Return the dfs that have nulls, and where those nulls are, and plot the distribution
    na_ls = [k for k, cdf in dfd.items() if cdf.columns.hasnans]
    na_dict = {k: [i for i, isnan in enumerate(cdf.columns.isna()) if isnan] for k, cdf in dfdict.items() if k in na_ls}
    print(len(dfdict) - len(na_ls), "don't have na columns")
    print(len(na_ls), "have na columns")
    sb.set_style("whitegrid")
    plt.figure(figsize = (10,5))
    sb.distplot(na_ls, bins = 20, kde = True, color = 'teal', kde_kws=dict(linewidth = 4, color = 'black'))
    plt.show()
    return na_dict
    
def handle_na_cols_custom(dfd):
    manual_cases = [(45, 'Best', 'Delete'),
    (61, 'Best', 'Delete', 'Delete'),
    (64, 'Delete'),
    (72, 'TOTAL', 'Delete', 'Delete', 'WILKS'),
    (103, 'Squat', 'Delete', 'Deadlift', 'Delete'),
    (110, 'Delete', 'Delete'),
    (114, 'Squat', 'Delete', 'Deadlift', 'Delete'),
    (117, 'Squat', 'Squat', 'Bench', 'Bench', 'Deadlift', 'Deadlift', 'Delete', 'Delete', 'Delete', 'Delete'),
    (140, 'Delete'),
    (147, 'Squat', 'Squat', 'Delete', 'Bench', 'Bench', 'Delete', 'Deadlift', 'Deadlift', 'Delete'),
    (166, 'Best'),
    (411, 'Delete', 'Delete')]
    
    for case in manual_cases:
        case_no = case[0]
        s = pd.Series(dfd[case_no].columns)
        s = s.fillna('ToBeChanged' + (s.groupby(s.isnull()).cumcount()).astype(str))
        dfd[case_no].columns = s #Change nan column names to iterable names
        for num, col in enumerate(case[1:]):
            if col == 'Delete':
                dfd[case_no].drop(columns = {'ToBeChanged'+str(num)}, inplace = True)
            else:
                dfd[case_no].rename(columns = {'ToBeChanged'+str(num): col}, inplace = True)

def remove_na_col1(dfd, na_dict):
    for k, ls in na_dict.items():
        if 1 in ls:
            keep_cols = list(range(len(dfd[k].columns)))
            keep_cols.remove(1)
            dfd[k] = dfd[k].iloc[:, keep_cols]
    
def remove_na_col_rest(dfd, na_dict):
    for k in na_dict.keys():
        dfd[k] = dfd[k].loc[:, dfd[k].columns.notnull()]

def check_valid_rows(dfd):
    #Change some row names to make analysis easier
    for k in [59, 183, 219, 198, 147]:
        dfd[k].rename(columns = {'CAT?': 'Class', 'CAT.': 'Class', 'CAT1': 'Class', 
                                    'Category': 'Class', 'M/W': 'M/F'}, inplace = True)
    
    #Tables without sex column to handle separately
    sex_semantics = ['M/F', 'M / F', 'Sex', 'SEX', 'CAT']
    no_sex = [k for k in dfd.keys() if not any(substring in dfd[k].columns for substring in sex_semantics)]
    
    #Handle M/F and Sex tables
    for k in dfd:
        dfd[k].rename(columns = {'M / F': 'M/F', 'Sex': 'M/F', 'SEX': 'M/F'}, inplace = True)
        if 'M/F' not in dfd[k].columns:
            continue
        dfd[k] = dfd[k][dfd[k]['M/F'].str.match('(^[MFmfwW]$)|(^[MF]-)', na = False)]
        
    #Sort out cat tables
    #Assume CAT is weight/age category when M/F column is present, and inspect the rest
    cat_without_mf = [k for k in dfdict if not 'M/F' in dfdict[k].columns and 'CAT' in dfdict[k].columns]
    # no_sex.extend(k for k in [j for j in dfdict if 'CAT' in dfdict[j].columns] if k not in cat_without_mf)
    cat_without_mf_vals = {k: list(dfdict[k]['CAT'].values) for k in cat_without_mf}
    #By inspection, the following tables don't have sex information in CAT
    cat_not_mf = {37, 38, 74, 76, 81, 91, 94, 143, 157, 159, 162, 163, 185, 190, 195, 200, 225, 226}
    no_sex.extend(cat_not_mf)
    cat_is_mf = set(cat_without_mf) - cat_not_mf
    
    #Handle cat tables where cat is mf
    for k in cat_is_mf:
        dfd[k].rename(columns = {'CAT': 'M/F'}, inplace = True)
        dfd[k] = dfd[k][dfd[k]['M/F'].str.match('(^[MFmfwW]$)|(^[MF]-)|(^[MF] -)|(- [MF]$)', na = False)]
    
    #Handle no sex tables (39 instances)
    
    
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
    
    #Find comps with equipped lifters (for potential use later)
    Eqp_Words = ["EQD", "EQP", "Equip", "EQUP"]
    Equipped_Comps = check_for_substrings(Eqp_Words, df)
    
    #Remove blank columns and unnecessary rows, and delete blank dataframes
    remove_bad_rowscolstables(dfdict)
    
    #Now first row should be header values. We'll check for exceptions manually
    bad_header_dfs = find_header_exceptions(dfdict)
    print("Broken headers: ", bad_header_dfs) # = [24, 36, 45, 59, 61, 72, 74, 75, 95, 97, 107, 129, 166, 177, 187, 195, 201, 214, 463, 706, 829] have bad headers
    
    #Fix broken headers
    fix_headers_custom(bad_header_dfs, dfdict) #NOTE: Data-specific implementation
    
    #Check fix worked
    bad_header_dfs = find_header_exceptions(dfdict)
    print("Broken headers after fix: ", bad_header_dfs)
    
    #Promote headers
    promote_headers(dfdict)
    
    #Remove bad rows/cols again (some could have emerged from previous operations)
    remove_bad_rowscolstables(dfdict)
    
    #Check the full list of headers from each df
    col_names = []
    for k, cdf in dfdict.items():
        col_names.extend(cdf.columns.to_list())
    print("Headers set: ", set(col_names)) #Sorted these headers into groups manually (See Semantics.csv)
    
    #Find count of instances of each of these
    header_name_freq = col_name_count(dfdict, col_names)
    # sem = pd.read_csv("../../Data/Semantics.csv", )
    # testdf = test(dfdict, sem)
    #By inspection, these mostly appear to be variables, apart from nan, which requires further investigation
    
    #Check where na columns are located
    na_dict = na_col_details(dfdict)
    #Also, most na cols are in the latter half of the comps
    
    #Handle the na columns by either removing or renaming. Note that 505/517 (Comp 454+) are of very similar format,
    # so I'll deal with the first 12 individually then handle the others together
    handle_na_cols_custom(dfdict) #NOTE: Data-specific implementation
    
    #Recheck na columns
    na_dict = na_col_details(dfdict)
    #Most of these only have NA in column 1, which is place column. Let's verify this
    
    vals_in_col1 = {k: list(dfdict[k].iloc[:, [1]].values.flatten()) for k, ls in na_dict.items() if 1 in ls}
    #By inspection, all column 1 na columns are placings and can be removed
    
    #Remove na columns occuring in column 1
    remove_na_col1(dfdict, na_dict)
    
    #Recheck na columns
    na_dict = na_col_details(dfdict)
    #Down from 505 tables with na columns to 174 tables.879
    #By inspection (of [[print(list(dfdict[k].iloc[:, num].values))) for num in cols] for k, cols in na_dict.items())]),
    # all other na columns are mostly na, containing only Australian/world record info. The exception to this is the nan
    # in comp 879, which is just a duplicate column anyway
    
    #Remove all remaining na columns
    remove_na_col_rest(dfdict, na_dict)
    
    #Recheck na columns
    na_dict = na_col_details(dfdict)
    #Now all columns are variables
    
    #To make all observations rows (and all rows observations), we can find rows without m/f/M/F (or the like) in the column
    # representing sex (based on headers set), and delete rows with invalid entries. Note some 'CAT' columns have 
    # sex info, but other variations of cat do not. Also, some 'CAT' columns have weight/age class info, and some tables 
    # don't have sex info at all. This will all be handled in the following function.
    check_valid_rows(dfdict)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
