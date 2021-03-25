# Powerlifting-Performance
Scraping Powerlifting Australia competition data from the past 21 years and analysing to find new insights, predict performance and determine winning strategies.

## To do
- Clean dataset using R/tidyverse
- Feature engineering for success/failed lifts and BP only

## Log
- Scraping data from site using Excel's Power Query, since the tables were exported from Excel so they are read by Excel naturally
- Need to download local copies of html files, and use them as Power Query data sources
- Cleaning should be easiest in R, so I'll export tabulized data to work with in R
- There are 38K rows and they're quite heavily varied prior to ~2010, so I might limit need to limit the scope
- I've planned out the cleaning process to hopefully get most of the data. The general template for the results tables has updated over time, creating groups of template. I've separate these groups for separate cleaning. 