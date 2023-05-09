
#set root 
root <- r'(C:\Users\L03054557\OneDrive\Edmundo-ITESM\)' 

#complete freight data  
#load OECD data 
dir_data <- r"(C:\Users\L03054557\Downloads\DP_LIVE_07042023031735889.csv)"
data_f <- read.csv(dir_data)

#load socioeconomic data  
dir_data <- paste0(root,r'(sisepuede_data\SocioEconomic\\)')
files <- list.files(dir_data)

DataIn <- list()
for (i in 1:length(files))
{
#i<-4
target_dir_historial <- r"(\input_to_sisepuede\historical\)"
target_dir_projected <- r"(\input_to_sisepuede\projected\)"
historical<-read.csv(paste0(dir_data,files[i],target_dir_historial,files[i],".csv"))
projected<-read.csv(paste0(dir_data,files[i],target_dir_projected,files[i],".csv"))
projected<-subset(projected,Year>max(historical$Year))
all <- rbind(historical,projected)
#edit colnames 
all$X<-NULL
colnames(all) <- gsub("Country","Nation",colnames(all))
colnames(all) <- gsub("ISO3","iso_code3",colnames(all))
DataIn <- append(DataIn,list(all))
rm(all)
}
#merge all data set  
DataIn <- Reduce(function(...) merge(...,), DataIn)

#subset to max time of freight data  
dim(DataIn)
DataIn<-subset(DataIn,Year <= max(data_f$TIME))
dim(DataIn)

#subset freight data by subject and train a linear model for each  
subjects <- unique(data_f$SUBJECT)

DataIn_F <- list()
for (i in 1:length(subjects))
{
#i<-2
pivot <- subset(data_f,SUBJECT == subjects[i])
dim(pivot)
pivot<-subset(pivot,pivot$TIME%in%unique(DataIn$Year))
pivot$iso_code3 <- pivot$LOCATION
pivot$Year <- pivot$TIME
dim(pivot)
ids<- c("iso_code3","Year")
socio_economic <- c("gdp_mmm_usd","population_gnrl_rural","population_gnrl_urban")
pivot <- Reduce(function(...) merge(...,), list(pivot,DataIn[,c(ids,socio_economic)]))
dim(pivot)

#create gdp per capita 
pivot$gdppc<-pivot$gdp_mmm_usd/(pivot$population_gnrl_rural+pivot$population_gnrl_urban)

#divide countries into two quantiles  
pivot$quant <- ifelse(pivot$gdppc>=quantile(pivot$gdppc,0.50),1,0)

#build linear model  
target_var<-"Value"
formula_imputation <- as.formula(paste(target_var,"~ gdp_mmm_usd+population_gnrl_urban",sep=""))


#if (subjects[i]=="COAST")
#{
#  formula_imputation <- as.formula(paste(target_var,"~ gdppc",sep=""))  
#} else  
#{
#  formula_imputation <- as.formula(paste(target_var,"~ gdp_mmm_usd+population_gnrl_urban",sep=""))
#}

#model_imputation <- lm(formula_imputation,pivot)
#summary(model_imputation)

#define two models 
#model 1
model_imputation0 <- lm(formula_imputation,subset(pivot,quant==1))
summary(model_imputation0)

#model 2
model_imputation1 <- lm(formula_imputation,subset(pivot,quant==0))
summary(model_imputation1)


#Use DataIn as the basis for imputation
DataIn_p <- DataIn[,c(ids,socio_economic)]
DataIn_p$gdppc<-DataIn_p$gdp_mmm_usd/(DataIn_p$population_gnrl_rural+DataIn_p$population_gnrl_urban)
DataIn_p$quant <- ifelse(DataIn_p$gdppc>=quantile(pivot$gdppc,0.75),1,0)

socio_economic <- c(socio_economic,"quant","gdppc")


#add observed value 
dim(DataIn_p)
DataIn_p <- Reduce(function(...) merge(...,all.x=TRUE), list(DataIn_p,pivot[,c(ids,"Value")]))
dim(DataIn_p)

#imputate missing values
#original
#DataIn_p[,paste0(target_var,"_imputation")] <- predict(model_imputation, DataIn_p[,c(socio_economic,"gdppc")] )

#alternative 
DataIn_p[,paste0(target_var,"_imputation0")] <- predict(model_imputation0, DataIn_p[,socio_economic] )
DataIn_p[,paste0(target_var,"_imputation1")] <- predict(model_imputation1, DataIn_p[,socio_economic] )
DataIn_p[,paste0(target_var,"_imputation")] <- ifelse(DataIn_p$quant==1,DataIn_p[,paste0(target_var,"_imputation0")],DataIn_p[,paste0(target_var,"_imputation1")])
DataIn_p[,paste0(target_var,"_imputation0")] <- NULL
DataIn_p[,paste0(target_var,"_imputation1")] <- NULL

#Create flag for imputation 
DataIn_p [, "Flag"] <- ifelse (is.na(DataIn_p [, target_var])==TRUE,"I","O") # I: imputation, O: observed 

#Correct errors in imputation 
DataIn_p[,paste0(target_var,"_imputation")] <- ifelse(DataIn_p[,paste0(target_var,"_imputation")] <0,0,DataIn_p[,paste0(target_var,"_imputation")] )
DataIn_p[,paste0(target_var,"_imputation")] <- ifelse(is.na(DataIn_p[,paste0(target_var,"_imputation")])==TRUE,mean(DataIn_p [, target_var],na.rm=TRUE),DataIn_p[,paste0(target_var,"_imputation")] )
DataIn_p [, target_var] <- ifelse (is.na(DataIn_p [, target_var])==TRUE,DataIn_p[,paste0(target_var,"_imputation")],DataIn_p[, target_var])

#finnally obtain impute ceros using mean per country
tab<-aggregate(list(mean=DataIn_p[,target_var]),list(iso_code3=DataIn_p$iso_code3),function(x) { x<-subset(x,x>0); mean(x)})
tab$mean <-ifelse(is.na(tab$mean)==TRUE,0,tab$mean)
dim(DataIn_p)
DataIn_p<-merge(DataIn_p,tab,by="iso_code3")
dim(DataIn_p)

#change ceros for the mean 
DataIn_p [, target_var] <- ifelse (DataIn_p [, target_var]==0.0,DataIn_p[,"mean"],DataIn_p[, target_var])

#if you still have ceros use the mean of the quantile 
tab<-aggregate(list(meanq=DataIn_p[,target_var]),list(quant=DataIn_p$quant),function(x) { quantile(x,0.25)})
dim(DataIn_p)
DataIn_p<-merge(DataIn_p,tab,by="quant")
dim(DataIn_p)
DataIn_p [, target_var] <- ifelse (DataIn_p [, target_var]==0.0,DataIn_p[,"meanq"],DataIn_p[, target_var])

#summary(DataIn_p)
#subset(DataIn_p,iso_code3%in%c("CHL","MEX"))
#mean(subset(DataIn_p,iso_code3%in%c("CHL"))$Value)

#complete characteristics of original data set 
DataIn_p$LOCATION <- DataIn_p$iso_code3
DataIn_p$TIME <- DataIn_p$Year 
DataIn_p$INDICATOR <- unique(pivot$INDICATOR)
DataIn_p$SUBJECT <- unique(pivot$SUBJECT)
DataIn_p$MEASURE <- unique(pivot$MEASURE)
DataIn_p$FREQUENCY <- unique(pivot$FREQUENCY)
DataIn_p[,c(ids,socio_economic,"Value_imputation","mean","meanq")] <- NULL

DataIn_F <- append(DataIn_F,list(DataIn_p))
rm(DataIn_p)
rm(pivot)
}

DataIn_F <- do.call("rbind",DataIn_F)

#final check deals with making sure shares are not above known percentage 

totals <- aggregate(list(ValueTotal=DataIn_F$Value),list(TIME=DataIn_F$TIME, LOCATION=DataIn_F$LOCATION),sum)
dim(totals)
dim(DataIn_F)
DataIn_F <- Reduce(function(...) merge(...,), list(DataIn_F,totals))
dim(DataIn_F)

#value check  
DataIn_F$Value_check <- DataIn_F$Value/DataIn_F$ValueTotal

#review maximum values of observed  
test<-subset(DataIn_F,Flag=="O")
Thresholds <- aggregate(list(Threshold=test$Value_check), list(SUBJECT=test$SUBJECT),function(x) {quantile(x,0.90)})
Thresholds$ThresholdEPS<- c(0.15,0.58,0.23,0.43)


#adjust 
dim(DataIn_F)
DataIn_F <- Reduce(function(...) merge(...,), list(DataIn_F,Thresholds))
dim(DataIn_F)

#
head(DataIn_F)
#DataIn_F[,"Value_Imputation"] <- ifelse(DataIn_F$Value_check>DataIn_F$Threshold,DataIn_F[,"ValueTotal"]*DataIn_F[,"Threshold"],DataIn_F[,"Value"])
DataIn_F[,"Value_Imputation"] <- DataIn_F[,"ValueTotal"]*DataIn_F[,"ThresholdEPS"]
DataIn_F[,"Value"] <- ifelse(DataIn_F$Flag=="I" & DataIn_F$SUBJECT%in%c("RAIL","COAST") ,DataIn_F[,"Value_Imputation"],DataIn_F[,"Value"])
DataIn_F[,"Value"] <- ifelse(DataIn_F[,"Value"]==0,DataIn_F[,"Value_Imputation"],DataIn_F[,"Value"])

#remove undeeded columns 
DataIn_F[,c("ValueTotal","Value_check","Threshold","ThresholdEPS","Value_Imputation")] <- NULL


#check brazil and mexico 

test1<-subset(DataIn_F,LOCATION%in%c("BRA","CHL","ECU","MEX") & TIME==2021)
totals <- aggregate(list(ValueTotal=test1$Value),list(TIME=test1$TIME, LOCATION=test1$LOCATION),sum)
dim(totals)
dim(test1)
test1 <- Reduce(function(...) merge(...,), list(test1,totals))
dim(test1)

test1$Value_check <- test1$Value/test1$ValueTotal
test1[,c("LOCATION","TIME","SUBJECT","Value","ValueTotal","Value_check")]

DataIn_F$Flag <- NULL
write.csv(DataIn_F,"imputated_freight_data.csv",row.names=FALSE)
