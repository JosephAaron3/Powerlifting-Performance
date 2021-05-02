"""Statistical tests for comparing the aggregated (yearly) means of TotalKg over time."""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as ss
from statsmodels.stats import multicomp

# Read data and separate group of interest
df = pd.read_csv("../../Data/OP_Cleaned.csv", index_col=0, parse_dates=['Date'])
dfg = df.loc[(df['Event'] == 'SBD') & (df['Sex'] == 'M') & (df['Equipment'] == 'Raw')
             & (df.Date.dt.year >= 1996) & (df.Date.dt.year < 2020) & (df['AgeClass'] == '24-34')]
dfg = dfg.set_index('Date')

# One-way ANOVA
values_per_group = [col.dropna() for col_name, col in dfg.groupby(pd.Grouper(freq="Y"))['TotalKg']]
results_anova = ss.f_oneway(*values_per_group)
print(f"ANOVA Results: F = {results_anova[0]} (p-value = {results_anova[1]})")

# Welch test
values_per_group = [(col_name.year, col.dropna())
                    for col_name, col in dfg.groupby(pd.Grouper(freq="Y"))['TotalKg']]
paired_groups = [(values_per_group[i], values_per_group[j]) for i in range(len(values_per_group))
                 for j in range(i + 1, len(values_per_group))]
print("Significant Welch results:")
for g1, g2 in paired_groups:
    results_welch = ss.ttest_ind(g1[1], g2[1], equal_var=False)
    if results_welch[1] < 0.05:
        print(f"({g1[0]}, {g2[0]}) F = {results_welch[0]} (p-value = {results_welch[1]})")

# Tukey
dfg['Year'] = dfg.index.year
dfg = dfg[dfg.TotalKg.notnull()]
results_tukey = multicomp.pairwise_tukeyhsd(dfg['TotalKg'], dfg['Year'], alpha=0.05)

# Plot Tukey
sns.set(font_scale=1.4)
fig = results_tukey.plot_simultaneous(2019, figsize=(10, 6), ylabel='Year',
                                      xlabel='Mean TotalKg with universal confidence intervals')
plt.title("Multiple (Tukey) comparisons - Male")
# fig.savefig("../../Output/TotalKg_time_meancomparison_male.png", dpi=60)
