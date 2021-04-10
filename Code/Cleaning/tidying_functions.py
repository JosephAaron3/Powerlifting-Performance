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
            new_row = pd.DataFrame({'CompID': 706, 'Column2': "Place", 'Column3': "NAME",
                                    'Column4': "DOB", 'Column5': "SEX", 'Column6': "BWT",
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
    (72, 'TOTAL', 'Place', 'Delete', 'WILKS'),
    (103, 'Squat', 'Delete', 'Deadlift', 'Delete'),
    (110, 'Delete', 'Delete'),
    (114, 'Squat', 'Delete', 'Deadlift', 'Delete'),
    (117, 'Squat', 'Squat', 'Bench', 'Bench', 'Deadlift', 'Deadlift', 'Delete', 'Delete', 'Delete', 'Delete'),
    (140, 'Place'),
    (147, 'Squat', 'Squat', 'Delete', 'Bench', 'Bench', 'Delete', 'Deadlift', 'Deadlift', 'Delete'),
    (166, 'Best'),
    (411, 'Place', 'Delete')]
    
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

def rename_na_col1(dfd, na_dict):
    for k, ls in na_dict.items():
        if 1 in ls:
            col_names = dfd[k].columns.to_list()
            col_names[1] = 'Place'
            dfd[k].columns = col_names
    
def remove_na_col_rest(dfd, na_dict):
    for k in na_dict.keys():
        dfd[k] = dfd[k].loc[:, dfd[k].columns.notnull()]

def validate_rows_by_sex(dfd):
    #Change some row names to make analysis easier
    for k in [59, 183, 219, 198, 147]:
        dfd[k].rename(columns = {'CAT?': 'Class', 'CAT.': 'Division', 'CAT1': 'Division', 'DIV': 'Class', 'DIV.': 'Class',
                                    'Category': 'Division', 'Division': 'Class', 'M/W': 'M/F'}, inplace = True)
    dfd[331].rename(columns = {'DIV': 'M/F', 'M/F': 'Division'}, inplace = True)
    
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
    cat_without_mf_vals = {k: list(dfdict[k]['CAT'].values) for k in cat_without_mf}
    #By inspection, the following tables don't have sex information in CAT
    cat_not_mf = {37, 38, 74, 76, 81, 91, 94, 143, 157, 159, 162, 163, 185, 190, 195, 200, 225, 226}
    no_sex.extend(cat_not_mf)
    cat_is_mf = set(cat_without_mf) - cat_not_mf
    
    #Handle cat tables where cat is mf
    for k in cat_is_mf:
        dfd[k].rename(columns = {'CAT': 'M/F'}, inplace = True)
        dfd[k] = dfd[k][dfd[k]['M/F'].str.match('(^[MFmfwW]$)|(^[MF]-)|(^[MF] -)|(- [MF]$)', na = False)]
    
    #Handle no sex tables (39 instances) by inspection
    to_del = [25, 36, 37, 45, 46, 59, 60, 61, 72, 182, 187, 194, 198, 200] #No sex information
    to_fix = [k for k in no_sex if k not in to_del]
    for key in to_del:
        del dfd[key]
    
    #Delete bad rows manually
    dfd[74].drop(index = [2015, 2016, 2017], inplace = True)
    dfd[76].drop(index = [2103, 2104], inplace = True)
    dfd[81].drop(index = [2204, 2205], inplace = True)
    dfd[148].drop(index = [4262, 4282, 4296, 4301, 4315, 4320], inplace = True)
    dfd[166].drop(index = [4722, 4723, 4732, 4733, 4747, 4748, 4752, 4753, 4775, 4776], inplace = True)
    dfd[173].drop(index = [4951], inplace = True)
    #Comp 650 is a big comp with a unique result table layout. This will be handled individually
    #A row is valid if and only if DOB is an int > 1900
    dfd[650] = dfd[650][dfd[650]['DOB'].str.isnumeric()]
    dfd[650] = dfd[650][dfd[650]['DOB'].astype(int) > 1900]
    
    return to_fix

def add_sex(dfd):
    dfd[38]['M/F'] = ['F']*2 + ['M']*(len(dfd[38]) - 2)
    dfd[52]['M/F'] = ['F']*2 + ['M']*(len(dfd[52]) - 2)
    dfd[74]['M/F'] = ['F']*3 + ['M']*(len(dfd[74]) - 3)
    dfd[76]['M/F'] = ['M']*len(dfd[76]); dfd[76].loc[2072:2083, 'M/F'] = 'F'
    dfd[81]['M/F'] = ['F']*3 + ['M']*(len(dfd[81]) - 3); dfd[81].loc[2186, 'M/F'] = 'F'; dfd[81].loc[2199, 'M/F'] = 'F'
    dfd[91]['M/F'] = 'M'
    dfd[94]['M/F'] = ['M']*len(dfd[94])
    dfd[143]['M/F'] = ['M']*len(dfd[143])
    dfd[148]['M/F'] = ['F']*12 + ['M']*(len(dfd[148]) - 12)
    dfd[157]['M/F'] = ['M']*len(dfd[157]); dfd[157].loc[4469, 'M/F'] = 'F'; dfd[157].loc[4474, 'M/F'] = 'F'
    dfd[159]['M/F'] = ['F']*1 + ['M']*(len(dfd[159]) - 1)
    dfd[161]['M/F'] = ['M']*len(dfd[161])
    dfd[162]['M/F'] = ['M']*len(dfd[162])
    dfd[163]['M/F'] = ['M', 'M', 'M', 'M', 'F', 'F', 'M']
    dfd[166]['M/F'] = ['F']*12 + ['M']*(len(dfd[166]) - 12); dfd[166].loc[4749:4750, 'M/F'] = 'F'
    dfd[173]['M/F'] = ['F']*3 + ['M']*(len(dfd[173]) - 3)
    dfd[178]['M/F'] = ['M']*len(dfd[178])
    dfd[185]['M/F'] = ['M']*len(dfd[185])
    dfd[186]['M/F'] = ['M']*len(dfd[186])
    dfd[190]['M/F'] = ['M']*len(dfd[190])
    dfd[195]['M/F'] = ['M']*len(dfd[195]); dfd[195].loc[[5509,5512,5516], 'M/F'] = 'F'
    dfd[219]['M/F'] = ['F']*3 + ['M']*(len(dfd[219]) - 3)
    dfd[225]['M/F'] = ['F']*2 + ['M']*(len(dfd[225]) - 2)
    dfd[226]['M/F'] = ['F']*2 + ['M']*(len(dfd[226]) - 2)
    dfd[650]['M/F'] = ['M']*len(dfd[650]); dfd[650].loc[22393:22490, 'M/F'] = 'F'; dfd[650].loc[[22552, 22602], 'M/F'] = 'F'
    
def fix_duplicate_colnames(dfd):
    dup_colname_comps = [k for k, cdf in dfd.items() if len(set(cdf.columns)) != len(cdf.columns)]
    dup_colname_strings = {k: set(dfd[k].columns[dfd[k].columns.duplicated()]) for k in dup_colname_comps}
                   
    #Case 1: Useless 1st+ instance columns - Delete all but last duplicated column
    #(126, 165*)
    dfd[126].columns = ['CompID', 'Name', 'M/F', 'BW', 'Wt Class', 'Wilks Coeff.', 'Sq1', 'Sq2', 'Sq3', 'Best Sq', 'DELETE', 'BP1', 'BP2', 'BP3', 'Best BP', 'DELETE', 'Sub Total', 'DELETE', 'DL1', 'DL2', 'DL3', 'Best DL', 'DELETE', 'Total', 'Wilks', 'Place']
    dfd[126].drop(columns = ['DELETE'], inplace = True)
    dfd[165].columns = ['CompID', 'NAME', 'DELETE', 'CAT', 'DIV', 'M/F', 'BWT', 'SQUAT1', 'SQUAT2', 'SQUAT3', 'BENCH PRESS1', 'BENCH PRESS2', 'BENCH PRESS3', 'Sub Total', 'DEADLIFT1', 'DEADLIFT2', 'DEADLIFT3', 'Total']
    dfd[165].drop(columns = ['DELETE'], inplace = True)
    
    #Case 2: Lifts aren't numbered  - Add lift number after them
    #(103, 109, 114, 117, 147, 149, 150, 151, 152, 173, 189, 203, 211, 229, 230, 236, 261)
    cases = [103, 109, 114, 117, 149, 150, 151, 152, 173, 189, 203, 211, 229, 230, 236, 261]
    for k in cases:
        dups = dfd[k].columns[dfd[k].columns.duplicated()]
        dup_counter = {name: 0 for name in dups}
        name_list = []
        for i, col in enumerate(dfd[k].columns):
            if col not in dups:
                name_list.append(col)
            else:
                dup_counter[col] += 1
                name_list.append(col + ' ' + str(dup_counter[col]))
        dfd[k].columns = name_list
                    
    
    #Case 3: Lifts are only numbers - Add lift name before them
    #(166, 38)
    dfd[166].columns = ['CompID', 'NR', 'BDW.', 'Cat', 'NAME', 'State', 'SQ 1', 'SQ 2', 'SQ 3', 'Best','BP 1', 'BP 2', 'BP 3', 'SUB.', 'DL 1', 'DL 2', 'DL 3', 'TOT.', 'Wilks', 'PL.', '4. SQ', '4. BP', '4.DL', 'M/F']
    dfd[38].columns = ['CompID', 'DIV', 'BDW.', 'NAME', 'CAT', 'STATE', 'BP1', 'BP2', 'BP3', 'TOT.', 'PL.', '4TH', 'M/F'] #Not duplicate, but still needs fixing
    
    #Case 4: Useless 2nd+ instance columns - Delete all but first duplicated column
    #(872+)
    for k in [j for j in dup_colname_comps if j >= 872]:
        dfd[k].columns = pd.io.parsers.ParserBase({'names':dfd[k].columns})._maybe_dedup_names(dfd[k].columns)
        dfd[k].drop(list(dfd[k].filter(regex = '\.[1-9]$')), axis = 1, inplace = True)
    
    
    #Case 5: Column named wrong - Rename column
    #(366, 237*, 239*)
    dfd[366].columns = ['CompID', 'NAME', 'M/F', 'DIV', 'CLASS', 'BWT', 'SQ 1', 'SQ 2', 'SQ 3', 'BP 1', 'BP 2', 'BP 3', 'DL 1', 'DL 2', 'DL 3', 'TOTAL', 'WILKS']
    dfd[237].columns = ['CompID', 'NAME', 'DIV', 'M/F', 'BWT', 'CLASS', 'BP 1', 'BP 1o', 'BP 2', 'BP 2o', 'BP 3', 'BP 3o', 'Total', 'Wilks?', 'Place']
    dfd[239].columns = ['CompID', 'NAME', 'DIV', 'M/F', 'BWT', 'CLASS', 'SQ 1', 'SQ 1o', 'SQ 2', 'SQ 2o', 'SQ 3', 'SQ 3o', 'BP 1', 'BP 1o', 'BP 2', 'BP 2o', 'BP 3', 'BP 3o', 'DL 1', 'DL 1o', 'DL 2', 'DL 2o', 'DL 3', 'DL 3o', 'Total', 'Wilks Total', 'Place']

    #Case 6: 2nd instance column has lift outcome - Merge with 1st column
    #(237*, 239*)
    dfd[237]['BP 1'] = dfd[237]['BP 1'] + dfd[237]['BP 1o'].fillna('')
    dfd[237]['BP 2'] = dfd[237]['BP 2'] + dfd[237]['BP 2o'].fillna('')
    dfd[237]['BP 3'] = dfd[237]['BP 3'] + dfd[237]['BP 3o'].fillna('')
    dfd[237].drop(columns = ["BP 1o", "BP 2o", "BP 3o"], inplace = True)
    
    for lift in [i + ' ' + j for i in ['SQ', 'BP', 'DL'] for j in ['1', '2', '3']]:
        dfd[239][lift] = dfd[239][lift] + dfd[239][lift + 'o'].fillna('')
        dfd[239].drop(columns = [lift + 'o'], inplace = True)
    
    #Case 7: Bodyweight columns separated by sex - Merge
    #(157, 195, 225, 226)
    dfd[157]['MBW'] = dfd[157]['MBW'].fillna('') + dfd[157]['FBWT'].fillna(''); dfd[157].drop(columns = ['FBWT'], inplace = True)
    dfd[195]['MBW'] = dfd[195]['MBW'].fillna('') + dfd[195]['FBWT'].fillna(''); dfd[195].drop(columns = ['FBWT'], inplace = True)
    dfd[225]['Male Body Wt (kg)'] = dfd[225]['Male Body Wt (kg)'].fillna('') + dfd[225]['Female Body Weight (kg)'].fillna(''); dfd[225].drop(columns = ['Female Body Weight (kg)'], inplace = True)
    dfd[226]['Male Body Wt (kg)'] = dfd[226]['Male Body Wt (kg)'].fillna('') + dfd[226]['Female Body Weight (kg)'].fillna(''); dfd[226].drop(columns = ['Female Body Weight (kg)'], inplace = True)
    
    #Special cases - Fix manually
    #(147, 222)
    dfd[147].columns = ['CompID', 'M/F', 'Class', 'BW', 'Name', 'SQ 1', 'SQ 2', 'SQ 3', 'Best SQ', 'BP 1', 'BP 2', 'BP 3', 'Best BP', 'Sub.', 'DL 1', 'DL 2', 'DL 3', 'Best DL', 'Tot.', 'Points', 'Place', 'SQ', 'BP', 'DL']
    dfd[147].drop(columns = ['SQ', 'BP', 'DL'], inplace = True)
    dfd[222].drop(columns = ['MWILKS'], inplace = True)
    
def homogenize_column_contents(dfd):
    mixed_col_names = ['DIV', 'Div', 'Cat', 'CAT', 'CLASS'] #These names have mixed meanings across tables
    #We will change these to either DivisionCustom or ClassCustom (to avoid duplicate headers)
    
    #Special cases
    dfd[11].loc[440:442, 'CAT'] = dfd[11].loc[440:442, 'DIV']
    dfd[11].loc[440:442, 'DIV'] = ['Open']*3
    dfd[210].loc[5870, 'DIV'] = 'J'; dfd[210]['ClassCustom'] = '100'; dfd[210].rename(columns = {'DIV': 'DivisionCustom'}, inplace = True)
    dfd[216].loc[5956, 'DIV'] = 'SJ'; dfd[216]['ClassCustom'] = '60'; dfd[216].rename(columns = {'DIV': 'DivisionCustom'}, inplace = True)
    dfd[221].loc[6083, 'DIV'] = 'J'; dfd[221]['ClassCustom'] = '100'; dfd[221].rename(columns = {'DIV': 'DivisionCustom'}, inplace = True)
    dfd[54].drop(columns = ['Cat'], inplace = True)
    dfd[218].rename(columns = {'GROUP': 'DivisionCustom'}, inplace = True)
    dfd[197].rename(columns = {'Wt': 'BWT'}, inplace = True)
    dfd[104].rename(columns = {'WEIGHT': 'Best BP'}, inplace = True)
    dfd[738]['Place'] = ['1', '1', '2', '1', '1', '2', '3', '1', '2', '1', '2', '1', '2', '1', '1', '1', '2', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '2', '3', '1', '2', '1', '1', '2', '3', '1', '1', '2', '1', '1', '2', '3', '1', '2', '1', '1', '2', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1']
    dfd[148].loc[4263:4319, 'TOTAL'] = dfd[148].loc[4263:4319, 'PLACE']
    dfd[148].loc[4263:4319, 'PLACE'] = np.nan
    
    #Div
    for k in [k for k in dfdict if 'Div' in dfdict[k].columns]:
        if k not in [49, 68, 420]:
            dfd[k].rename(columns = {'Div': 'ClassCustom'}, inplace = True)
        else:
            dfd[k].rename(columns = {'Div': 'DivisionCustom'}, inplace = True)
    
    #CLASS
    dfd[270].drop(columns = ['CLASS'], inplace = True)
    dfd[310].rename(columns = {'DIV': 'ClassCustom', 'CLASS': 'DivisionCustom'}, inplace = True)
    for k in [k for k in dfdict if 'CLASS' in dfdict[k].columns]:
        dfd[k].rename(columns = {'CLASS': 'ClassCustom'}, inplace = True)
    
    #Cat
    for k in [k for k in dfdict if 'Cat' in dfdict[k].columns]:
        if k in [49, 68, 166, 197]:
            dfd[k].rename(columns = {'Cat': 'ClassCustom'}, inplace = True)
        else:
            dfd[k].rename(columns = {'Cat': 'DivisionCustom'}, inplace = True)
    
    #CAT
    for k in [k for k in dfdict if 'CAT' in dfdict[k].columns]:
        if k in [11, 16, 21, 23, 26, 32, 33, 81, 174, 225, 226]:
            dfd[k].rename(columns = {'CAT': 'ClassCustom'}, inplace = True)
        else:
            dfd[k].rename(columns = {'CAT': 'DivisionCustom'}, inplace = True)

    #DIV
    for k in [k for k in dfdict if 'DIV' in dfdict[k].columns]:
        if k < 237 or k > 400:
            if k in [11, 16, 21, 23, 26, 32, 33, 81, 422, 431, 443]:
                dfd[k].rename(columns = {'DIV': 'DivisionCustom'}, inplace = True)
            else:
                dfd[k].rename(columns = {'DIV': 'ClassCustom'}, inplace = True)
        else:
            if k in [241, 242, 266, 276, 310, 320, 355, 360, 364, 370]:
                dfd[k].rename(columns = {'DIV': 'ClassCustom'}, inplace = True)
            else:
                dfd[k].rename(columns = {'DIV': 'DivisionCustom'}, inplace = True)

def homogenize_header_names(dfd):
    semdf = pd.read_csv("../../Data/Semantics.csv", engine = 'python')
    
    #Map words to semantic meaning
    semdict = {tuple(semdf[semdf[col].notnull()][col]): col for col in semdf.columns}
    semmap = {}
    for k, v in semdict.items():
        for key in k:
            semmap[key] = v
    
    #Change header names
    for k in dfd:
        dfd[k].rename(columns = semmap, inplace = True)
        if 'Misc.' in dfd[k].columns:
            dfd[k].drop(columns = ['Misc.'], inplace = True)

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
    
    #Handle the na columns by either removing or renaming. Note that 505-517 (of Comp 454+) are of very similar format,
    # so I'll deal with the first 12 individually then handle the others together
    handle_na_cols_custom(dfdict) #NOTE: Data-specific implementation
    
    #Recheck na columns
    na_dict = na_col_details(dfdict)
    #Most of these only have NA in column 1, which is place column. Let's verify this
    
    vals_in_col1 = {k: list(dfdict[k].iloc[:, [1]].values.flatten()) for k, ls in na_dict.items() if 1 in ls}
    #By inspection, all column 1 na columns are placings and can be renamed
    
    #Rename na columns occuring in column 1
    rename_na_col1(dfdict, na_dict)
    
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
    to_fix = validate_rows_by_sex(dfdict)
    print("Columns to add sex info to:", to_fix)
    
    #Add sex info to the columns to fix
    add_sex(dfdict)
    
    #Ensure each dataframe has no duplicated column names
    fix_duplicate_colnames(dfdict)

    #Homogenize contents of divison, category, and class columns
    homogenize_column_contents(dfdict)
    
    #Homogenize header names
    homogenize_header_names(dfdict)
    
    #Concatenate all dataframes
    final = pd.concat([cdf for cdf in dfdict.values()], ignore_index=True, sort=False)
    
    #Check no loss of information
    print("Non-nulls in dfdict:", sum([cdf.notnull().sum().sum() for cdf in dfdict.values()]))
    print("Non-nulls in final:", final.notnull().sum().sum())
    print("# unique columns in dfdict:", len(set(sum([list(cdf.columns) for cdf in dfdict.values()], []))))
    print("# columns in final:", len(set(final.columns)))
    
    #Save tidy data
    final.to_csv("../../Data/Tidy_Full.csv", index_label = 'Index')