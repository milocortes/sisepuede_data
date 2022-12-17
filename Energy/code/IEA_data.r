root<-r"(C:\Users\AP03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\)"

dir_data <-paste0(root,r"(Data\IEA2018\World Energy Balances\)")
name_file <-"wconv.csv"
data <- read.csv(paste0(dir_data,name_file))

#first we clean data  
ids<-c("COUNTRY","FLOW","PRODUCT","UNIT")

vars<-subset(colnames(data),!(colnames(data)%in%ids))

datan<-data

for (i in 1:length(vars))
{
 datan[,vars[i]] <- ifelse(datan[,vars[i]]=="x",NA,datan[,vars[i]])
 datan[,vars[i]] <- ifelse(datan[,vars[i]]=="..",NA,datan[,vars[i]])  
 datan[,vars[i]] <- as.numeric(as.character(datan[,vars[i]] ) )
}

#
datan$Mean<-rowMeans(datan[,vars],na.rm=TRUE)
datan<-subset(datan,datan$UNIT=="toe/t")

#keep only the values we need, and merge iso_code3 values 
datan<-datan[,c(ids,"Mean")]
head(datan)

#merge data crosswalk 
dir_data <- paste0(root,r"(calibration_lac_dec\observed_data\Energy\efficfactor_enfu_industrial_energy_fuel_natural_gas\raw_data\)")
data_cw<-read.csv(paste0(dir_data,"data_cross_walk.csv"))
head(data_cw)

dim(datan)
dim(data_cw)
test<-Reduce(function(...) merge(..., all.x=T), list(datan,data_cw))
dim(test)
test$Nation <- test$COUNTRY

#append nation names 
test$Nation <- gsub("Viet Nam", "Vietnam",test$Nation)
test$Nation <- gsub("Plurinational State of Bolivia", "Bolivia",test$Nation)
test$Nation <- gsub("Bolivarian Republic of Venezuela", "Venezuela",test$Nation)
test$Nation <- gsub("People's Republic of China", "China",test$Nation)
test$Nation <- gsub("Republic of the Congo", "Congo",test$Nation)

#merge with list of countries 
dir_countries <- root
clist <- read.csv(paste0(dir_countries,"Countries_ISO3.csv"))
colnames(clist) <- c("Nation","iso_code3")

dim(test)
test <- merge(test, clist, by = "Nation")
dim(test)

#now lest print the files
sisepuede_vars <- subset(data_cw,is.na(data_cw$FLOW)==FALSE)$sipuede_item
#first all for which we have information 

for ( i in 1:length(sisepuede_vars))
{
i<-6
dir_out <- paste0(root,r"(calibration_lac_dec\observed_data\Energy\)",sisepuede_vars[i],r"(\input_to_sisepuede\)")

#target sisepuede_vars
pivot <- subset(test,sipuede_item==sisepuede_vars[i])
#head(pivot)

#input NAs using average  
pivot[, sisepuede_vars[i] ] <- ifelse(is.na(pivot$Mean) == TRUE , mean(pivot$Mean, na.rm=TRUE), pivot$Mean) 
pivot <- pivot[ ,c("Nation","iso_code3",sisepuede_vars[i])]

pivot_historic<-merge(pivot,data.frame(Year=c(2001:2021)))
#head(pivot_historic)
dir.create(paste0(dir_out,r"(historical\)"),recursive = TRUE)
write.csv(pivot_historic,paste0(dir_out,r"(historical\)",sisepuede_vars[i],".csv"),row.names=FALSE)

pivot_projected<-merge(pivot,data.frame(Year=c(2022:2050)))
#head(pivot_projected)
dir.create(paste0(dir_out,r"(projected\)"),recursive = TRUE)
write.csv(pivot_projected,paste0(dir_out,r"(projected\)",sisepuede_vars[i],".csv"),row.names=FALSE)
}

#second for those we do no have informations, but can assume a constant value  
sisepuede_varsb <- subset(data_cw,is.na(data_cw$FLOW)==TRUE)$sipuede_item

i<-3
pivot<-unique(test[,c("Nation","iso_code3")])
pivot[,sisepuede_varsb[i]]  <- subset(data_cw, sipuede_item == sisepuede_varsb[i])$Default


dir_out <- paste0(root,r"(calibration_lac_dec\observed_data\Energy\)",sisepuede_varsb[i],r"(\input_to_sisepuede\)")

pivot_historic<-merge(pivot,data.frame(Year=c(2001:2021)))
dir.create(paste0(dir_out,r"(historical\)"),recursive = TRUE)
write.csv(pivot_historic,paste0(dir_out,r"(historical\)",sisepuede_varsb[i],".csv"),row.names=FALSE)

pivot_projected<-merge(pivot,data.frame(Year=c(2022:2050)))
dir.create(paste0(dir_out,r"(projected\)"),recursive = TRUE)
write.csv(pivot_projected,paste0(dir_out,r"(projected\)",sisepuede_varsb[i],".csv"),row.names=FALSE)
