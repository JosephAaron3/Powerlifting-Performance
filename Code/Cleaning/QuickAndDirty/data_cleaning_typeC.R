library(tidyverse)
library(data.table)

setwd("D:/Professional/Projects/Powerlifting-Performance/Code")
raw_df <- read.csv("../Data/PartialCleanC.csv", header=TRUE)
typeC = raw_df %>% filter(!Col1=="NA")

#Whole table cleaning

typeCClean = data.frame(CompID = character(), NAME = character(), DOB = character(), "M/F" = character(), "SQ 1" = character(), "SQ 2" = character(),
                        "SQ 3" = character(), "BP1" = character(), "BP 2" = character(), "BP 3" = character(), "DL 1" = character(),
                        "DL 2" = character(), "DL 3" = character(), TOTAL = character(), WILKS = character(), stringsAsFactors = FALSE)

CleanTCTable = function(i) {
    temp = typeC[typeC$Col1 == i,]
    temp = temp[!sapply(temp, function(x) all(x == ""))] #Remove blank columns
    temp[] <- lapply(temp, as.character) #Convert all to strings
    names(temp) = temp[1,] #Promote headers
    names(temp)[names(temp) == as.character(i)] = "CompID"
    temp = temp[-1,]
    temp = temp[, !duplicated(colnames(temp))] #Remove last duplicated rows
    temp = temp[, colnames(temp) != ""] #Remove more useless columns
    return(temp)
}

for (i in 454:max(typeC$Col1)) {
    temp = CleanTCTable(i)
    #Add cleaned table to type table
    typeCClean = rbind(typeCClean, temp) #Combine 2 dataframes by row (column names must match)
}

#Combine and output cleaned data
write.csv(typeCClean, paste("../Data/FullyCleanTypeC.csv"), row.names = FALSE)