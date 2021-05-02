#Imports
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set(font_scale = 1.4)
from sklearn import linear_model
from matplotlib.lines import Line2D

#Read data and separate group of interest
df = pd.read_csv("../../Data/OP_Cleaned.csv", index_col = 0, parse_dates = ['Date'])
dfg = df.loc[(df['Event'] == 'SBD') & (df['Sex'] == 'F') & (df['Equipment'] == 'Raw') & (df.Date.dt.year >= 1996) & (df.Date.dt.year < 2020) & (df['AgeClass'] == '24-34')]

#Calculate rolling quantiles based on date
dfg = dfg.set_index('Date')
TopQ = dfg['TotalKg'].rolling('180D').quantile(0.9)
MidQ = dfg['TotalKg'].rolling('180D').quantile(0.5)
BotQ = dfg['TotalKg'].rolling('180D').quantile(0.1)
Std = dfg['TotalKg'].rolling('180D').std()

#Linear regression of quantiles
X = (TopQ.index - TopQ.index[0]).days.to_numpy().reshape(-1,1)
lrTop = linear_model.LinearRegression().fit(X, TopQ.values)
lrMid = linear_model.LinearRegression().fit(X, MidQ.values)
lrBot = linear_model.LinearRegression().fit(X, BotQ.values)

#Plot rolling quantiles
fig = plt.figure(figsize = (10, 10))
legend_elements = [Line2D([0], [0], color='blue', lw=4, label='90th quantile'),
                   Line2D([0], [0], color='orange', lw=4, label='50th quantile'),
                   Line2D([0], [0], color='green', lw=4, label='10th quantile'),
                   Line2D([0], [0], color='red', lw=4, label='Standard deviation')]
plt.ylabel('TotalKg')
plt.title("Rolling quantiles (180 days) - Female lifters")
ax = TopQ.plot()
MidQ.plot()
BotQ.plot()
Std.plot()

#Add LR to plot (only start/end values for faster execution)
ax2 = ax.twiny()
ax2.tick_params(labeltop = False, top = False)
ax.set(ylim = (0,600))
ax.legend(handles=legend_elements, loc = 'best')
X_start, X_end = X[0][0], X[-1][0]
sns.lineplot([dfg.index[0], dfg.index[-1]], lrTop.predict([[X_start], [X_end]]), ax = ax2)
sns.lineplot([dfg.index[0], dfg.index[-1]], lrMid.predict([[X_start], [X_end]]), ax = ax2)
sns.lineplot([dfg.index[0], dfg.index[-1]], lrBot.predict([[X_start], [X_end]]), ax = ax2)

#fig.savefig("../../Output/TotalKg_time_female.png",dpi=60)

#Print LR output
print("Median linear regression output:")
print("Coefficient =", lrMid.coef_[0], f"(R^2 = {lrMid.score(X, MidQ.values)})")