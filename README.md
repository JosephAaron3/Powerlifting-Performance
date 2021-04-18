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

#### Goals 2-4
tbd.