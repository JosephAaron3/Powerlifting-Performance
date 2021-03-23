library(tidyverse)
library(data.table)

Omit = c(650, 725, 804, 239)

raw_df <- read.csv("../Data/MostlyCleaned.csv", header=TRUE)
df = raw_df

df$Link = as.character(df$Link)
df = df[!like(df$Link, "School", ignore.case = TRUE),]
df = df[!df$CompID %in% Omit,]

##Create Competitions csv
comps = distinct(subset(df, select = c("CompID", "Link")))
#write.csv(comps, "../Data/Competitions.csv", row.names = FALSE)

##Create Results csv
#Whole table cleaning
results = subset(df, select = -c(Link)) #Remove link column

#Partial table cleaning
typeA = results %>% filter(CompID <= 203)
typeAClean = data.frame(CompID = character(), NAME = character(), DOB = character(), "M/F" = character(), SQ1 = character(), 
                        SQ2 = character(), SQ3 = character(), BP1 = character(), BP2 = character(), BP3 = character(), DL1 = character(), 
                        DL2 = character(), DL3 = character(), TOTAL = character(), WILKS = character(), stringsAsFactors = FALSE)

typeB = results %>% filter(CompID >= 204 & CompID <= 453)
typeBClean = data.frame(CompID = character(), NAME = character(), DOB = character(), "M/F" = character(), SQ1 = character(), 
                        SQ2 = character(), SQ3 = character(), BP1 = character(), BP2 = character(), BP3 = character(), DL1 = character(), 
                        DL2 = character(), DL3 = character(), TOTAL = character(), WILKS = character(), stringsAsFactors = FALSE)

typeC = results %>% filter(CompID >= 454)
typeCClean = data.frame(CompID = character(), NAME = character(), DOB = character(), "M/F" = character(), SQ1 = character(), 
                        SQ2 = character(), SQ3 = character(), BP1 = character(), BP2 = character(), BP3 = character(), DL1 = character(), 
                        DL2 = character(), DL3 = character(), TOTAL = character(), WILKS = character(), stringsAsFactors = FALSE)

CleanTBTable = function(i) {
    temp = typeB[typeB$CompID == i,]
    #Clean individual table
    rows_containing_eqp = which(str_detect(as.character(temp$Column2), "EQP|EQUIPPED|EQUIPPED BENCH PRESS"))
    if (length(rows_containing_eqp) != 0) {
        temp = temp[1:min(rows_containing_eqp),] #Remove rows after equipped is spotted
    }
    temp = temp[!apply(subset(temp, select = -c(CompID)) == "", 1, all),] #Remove blank rows
    temp = temp[str_detect(as.character(temp$Column3), "^M/F$|^M$|^F$"),] #Remove useless rows
    temp = subset(temp, select = -c(Column1)) #Remove useless columns
    temp = temp[!sapply(temp, function(x) all(x == ""))] #Remove blank columns
    temp[] <- lapply(temp, as.character) #Convert all to strings
    names(temp) = temp[1,] #Promote headers
    names(temp)[names(temp) == as.character(i)] = "CompID"
    temp = temp[-1,]
    temp = temp[, !duplicated(colnames(temp))] #Remove last duplicated rows
    names(temp)[names(temp) == "BP 1"] = "BP1" #Rename BP 1 to BP1
    temp = temp[, colnames(temp) %in% c("NAME", "M/F", "BWT", "SQ 1", "SQ 2", "SQ 3", "BP1", "BP 2", "BP 3", "DL 1", "DL 2", "DL 3", "TOTAL", "WILKS")] #Remove more useless columns
    # temp$CompID = as.integer(temp$CompID)
    # temp$DOB = as.double(temp$DOB)
    # temp$TOTAL = as.double(temp$TOTAL)
    # temp$WILKS = as.double(temp$WILKS)
    # options(digits=1)
    return(temp)
}

CleanTCTable = function(i) {
    temp = typeC[typeC$CompID == i,]
    #Clean individual table
    rows_containing_eqp = which(str_detect(as.character(temp$Column2), "EQP|EQUIPPED|EQUIPPED BENCH PRESS"))
    if (length(rows_containing_eqp) != 0) {
        temp = temp[1:min(rows_containing_eqp),] #Remove rows after equipped is spotted
    }
    temp = temp[!apply(subset(temp, select = -c(CompID)) == "", 1, all),] #Remove blank rows
    temp = temp[str_detect(as.character(temp$Column4), "^M/F$|^M$|^F$"),] #Remove useless rows
    temp = subset(temp, select = -c(Column1)) #Remove useless columns
    temp = temp[!sapply(temp, function(x) all(x == ""))] #Remove blank columns
    temp[] <- lapply(temp, as.character) #Convert all to strings
    names(temp) = temp[1,] #Promote headers
    names(temp)[names(temp) == as.character(i)] = "CompID"
    temp = temp[-1,]
    temp = temp[, !duplicated(colnames(temp))] #Remove last duplicated rows
    temp = temp[, colnames(temp) != ""] #Remove more useless columns
    # temp$CompID = as.integer(temp$CompID)
    # temp$DOB = as.double(temp$DOB)
    # temp$TOTAL = as.double(temp$TOTAL)
    # temp$WILKS = as.double(temp$WILKS)
    # options(digits=1)
    return(temp)
}

# for (i in 204:453) {
#     if (i %in% Omit) {
#         next
#     }
#     temp = CleanTBTable(i)
#     # if (i %% 10 == 0) {
#     #     write.csv(temp, paste("../Data/Test/",as.character(i),".csv"), row.names = TRUE)
#     # }
#     #Add cleaned table to type table
#     typeBClean = rbind(typeBClean, temp) #Combine 2 dataframes by row (column names must match)
# }

for (i in 454:max(typeC$CompID)) {
    if (i %in% Omit) {
        next
    }
    temp = CleanTCTable(i)
    # if (i %% 10 == 0) {
    #     write.csv(temp, paste("../Data/Test/",as.character(i),".csv"), row.names = TRUE)
    # }
    #Add cleaned table to type table
    typeCClean = rbind(typeCClean, temp) #Combine 2 dataframes by row (column names must match)
}

Test = function(i) {
    temp = typeB[typeB$CompID == i,]
    #Clean individual table
    rows_containing_eqp = which(str_detect(as.character(temp$Column3), "EQP|EQUIPPED|EQUIPPED BENCH PRESS"))
    if (length(rows_containing_eqp) != 0) {
        temp = temp[1:min(rows_containing_eqp),] #Remove rows after equipped is spotted
    }
    temp = temp[!apply(subset(temp, select = -c(CompID)) == "", 1, all),] #Remove blank rows
    temp = temp[str_detect(as.character(temp$Column3), "^M/F$|^M$|^F$"),] #Remove useless rows
    temp = subset(temp, select = -c(Column1)) #Remove useless columns
    temp = temp[!sapply(temp, function(x) all(x == ""))] #Remove blank columns
    temp[] <- lapply(temp, as.character) #Convert all to strings
    names(temp) = temp[1,] #Promote headers
    names(temp)[names(temp) == as.character(i)] = "CompID"
    temp = temp[-1,]
    temp = temp[, !duplicated(colnames(temp))] #Remove last duplicated rows
    names(temp)[names(temp) == "BP 1"] = "BP1" #Rename BP 1 to BP1
    temp = temp[, colnames(temp) %in% c("NAME", "M/F", "BWT", "SQ 1", "SQ 2", "SQ 3", "BP1", "BP 2", "BP 3", "DL 1", "DL 2", "DL 3", "TOTAL", "WILKS")] #Remove more useless columns
    # temp$CompID = as.integer(temp$CompID)
    # temp$DOB = as.double(temp$DOB)
    # temp$TOTAL = as.double(temp$TOTAL)
    # temp$WILKS = as.double(temp$WILKS)
    # options(digits=1)
    return(temp)
}
