# Powerlifting-Performance
Performing data analytics/modelling on powerlifting competition data from the past 21 years to find new insights, predict performance and determine winning strategies.

## Goals
1. Uncover general trends among powerlifting competitors through exploratory data analysis
2. Examine how general performance has changed over time as powerlifting has become more popular
3. Determine the best predictors of performance using supervised learning models
4. Develop a weight-choosing strategy to maximise likelihood of success

*Extra:*
- Apply clustering techniques to distinguish raw from equipped lifters


## Data
- Powerlifting Australia event results tables
	- Webscraped from Powerlifting Australia’s website event results directory
	- Approx. ~20,000 records
	- Not clean, requires significant semantic integration
- OpenPowerlifting Project full dataset
	- Available as a single CSV download from https://data.openpowerlifting.org
	- Approx. ~2.4 million records
	- Clean
	- Schema well-defined at https://openpowerlifting.gitlab.io/opl-csv/bulk-csv-docs.html

## Outcomes
### The sport and its competitors - Univariate EDA
![competitor_count_year](/Output/competitor_count_year.png)  
**Observations:**
- General trend - Powerlifting popularity is increasing (probably exponentially)
- Competitions/competitors increasing in tandom (verified separately)
- Sharp decrease in popularity in 2020 (COVID)
- Interesting popularity shifts in the early 1980s

![num_vars](/Output/num_vars.png)  
**Observations:**
- Age is positively skewed and possibly bimodal
- Bodyweights are systemically multi-modal, likely set at weight class limits
- Total has a unique distribution. The right side of SBD (>600kg) looks very "smooth". I suspect this is a single normal distribution "peaking out"
- Wilks is almost perfectly normal for each event type, which is by design of the wilks formula

![cat_vars](/Output/cat_vars.png)  
**Observations:**
- ~3x more males than females
- Age is positively skewed, as expected
- Although 24-34 is the largest age bracket, it also has the widest range
- IPF is by far the dominant parent federation
- Event type popularity decreases by a factor of ~3 for each subsequent event in the order
- Single ply is more popular than raw (surprising) but multiply is signficantly less popular (verified separately)

![bench_attempt_frequency](/Output/bench_attempt_frequencies.png)  
**Observations:**
- Male lifter mean weight (and possibly variation) is always larger
- The ratio between successful and failed lifts increases with attempt number
- 3rd attempt bench press seems to be missed more often than made (only lift with this behaviour - verified separately)

### Performance history - Temporal analysis
The two performance measures I'll be considering are Totals and Wilks coefficients (https://en.wikipedia.org/wiki/Wilks_coefficient).
While total is only fairly comparable within a given group of competitors (age, weight, sex, etc.), Wilks aims to provide a metric which allows inter-group comparisons.
However, we still require equivalent competition types (e.g. only SBD).

To evaluate performance with respect to Total, we need to choose certain groups to compare. Each other group could be subject to the same analysis, but there are too many variations to consider here.
The following graph shows overall changes in competition parameters over time.  
![comp_changes_over_time](/Output/comp_changes_over_time.png)  
**Observations:**
- SBD is by far the most common event type
- Although single-ply was more popular, raw has overtaken it in the past ~7 years
- Both males and females had sudden jumps in participation at around 2010 and 2014 respectively
- These aforementioned jumps in participation seem to have residual effects on other graphs
- The 24-34 age class has always been the most popular

Based on these observations, we'll limit attention to males/females, 24-34 age class, in the raw SBD event. Also, very early years are omitted due to low sample sizes, and 
2020/2021 are omitted due to COVID.

Given the irregularity and non-uniqueness of the observation frequency over time (by day), I've decided to use rolling quantiles to
examine the change in TotalKg distribution over time. This allows us to visually check the changes in centrality (absolute slope of the lines), 
variablity (relative slopes of the lines), and skewness (difference in distances between lines).  
![TotalKg_time_male](/Output/TotalKg_time_male.png)  
**Observations:**
- There is very little change over time of the distribution with regards to centrality (Linear regression coefficient = 0.0003 (R^2 = 0.0033)), variability and skewness.
- Although variance appears to decrease (more stable estimation of quantiles), this is just a result of an increasing competitor count. The red line shows the standard deviation, which does not decrease significantly.

We can do a year-wise comparison of means. I first used one-way ANOVA followed by Welch's test. I assumed normality of the distributions due to CLT, 
but I wasn't so sure about homostedasticity, hence the use of the Welch test. Both ANOVA (F=3.64, p=7.8e-9) and Welch (in 39 out of 276 pairs of years) rejected the null of equality of means.
Welch, being pairwise, gave a better indicator of differences. Most null-rejected tests were concerning comparisons with years prior to 2010. I also used Tukey's test to show comparisons with confidence intervals, as shown below.  
![TotalKg_time_meancomparison_male](/Output/TotalKg_time_meancomparison_male.png)

Now we shift our attention to females (equivalent filtering as above otherwise)  
![TotalKg_time_female](/Output/TotalKg_time_female.png)  
**Observations:**
- The distribution is clearly shifting positively over time (Linear regression coefficient = 0.0121 (R^2 = 0.7912)), indicating increased performance at all levels by the females.
- Variance is again not changing significantly.
- Due to limited numbers in the early days, the quantile estimations are very erratic prior to ~2008, so any comparisons by statistical inference before this time may be less reliable (with the methods used here).

Again, I used Tukeys test to do year-wise mean comparisons with confidence intervals, as shown below.  
![TotalKg_time_meancomparison_female](/Output/TotalKg_time_meancomparison_female.png)  
Unlike the males, females performance over time significantly enough to have non-overlapping CIs (rejecting the null in Tukey's test), shown in red.

The Wilks coefficient allows us to compare performance across groups within a given competition. First, let's keep Sex separated to investigate an interesting anomaly.
The graph below uses rolling quantiles (same as above) of Wilks (but using 1-year windows for more stability).  
![Wilks_over_time](/Output/Wilks_over_time.png)  
**Observations:**
- Samples prior to ~1990 are rather erratic due to sample size, and will be ignored here.
- Between ~1990 and ~2010, quantiles are becoming further separated, indicating increased variance.
- Both sexes have a sudden negative shift in the entire distribution, around 2010 for males and 2014 for females.

This aforementioned sudden shift is interesting. It wasn't encountered in the investigation of Totals, and looking back at the graph of competition parameter changes over time, 
the shifts correspond to points at which participation suddenly increased. tbc.

#### Goals 3-4
tbd.
