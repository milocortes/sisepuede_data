library(reshape2)

#load iso_code3 
FILE_PATH <- getwd()

dir_data <- file.path(dirname(file.path(FILE_PATH,"..")), "raw_data")

iso_code <- read.csv(file.path(PATH, "Countries_ISO3.csv"))

########################
##[1] fuel_electricity"
########################


data <- read.csv(paste0(dir_data,"world energy prices electricity.csv"))
#
id_years <- subset( colnames(data),!( colnames(data)%in%c("COUNTRY","SECTOR","PRODUCT","UNIT")))

#clean data  
for (i in 1:length(id_years))
{
  #i<-1
  data[,id_years[i]] <- as.numeric(data[,id_years[i]])  
}

#subset to unit of interest 
dim(data)
data <- subset(data,UNIT=="Total price (USD/unit using PPP)")
dim(data)


data_new <- melt(data,id.vars = c("COUNTRY","SECTOR","PRODUCT","UNIT"), measure.vars = id_years ) 
data_new$Year<- as.numeric(gsub("X","",data_new$variable))
data_new <- subset(data_new, Year >=2010)
data_new<-aggregate(list(price=data_new$value),list(Country.Name=data_new$COUNTRY,
                                                    fuel=data_new$PRODUCT,
                                                    UNIT=data_new$UNIT),function(x){mean(x,na.rm=TRUE)})
data_new$unit_denominator<-"Mwh"
data_new$unit_type<-"energy produced"
data_new$fuel <-"fuel_electricity" 	
head(data_new)

#merge with iso_code3
data_new$Country.Name <- gsub("Bolivarian Rep. of Venezuela" , "Venezuela",data_new$Country.Name)
data_new$Country.Name <- gsub("Czech Republic" , "Czechia",data_new$Country.Name)
data_new$Country.Name <- gsub("Hong Kong (China)" , "Hong Kong SAR, China",data_new$Country.Name)
data_new$Country.Name <- gsub("Islamic Republic of Iran" , "Iran",data_new$Country.Name)
data_new$Country.Name <- gsub("Kyrgyzstan" , "Kyrgyz Republic",data_new$Country.Name)
data_new$Country.Name <- gsub("People's Republic of China" , "China",data_new$Country.Name)
data_new$Country.Name <- gsub("Plurinational State of Bolivia" , "Bolivia",data_new$Country.Name)
data_new$Country.Name <- gsub("Republic of Moldova" , "Moldova",data_new$Country.Name)
data_new$Country.Name <- gsub("United Republic of Tanzania" , "Tanzania",data_new$Country.Name)
data_new$Country.Name <- gsub("Viet Nam" ,"Vietnam",data_new$Country.Name)

#merge 
data_new<-merge(data_new,iso_code,by="Country.Name")
data_new$iso_code3<-data_new$ISO3
data_new$ISO3<-NULL
subset(data_new,Country.Name%in%c("Mexico","Ecuador","Brazil","Chile"))
data1<-data_new
rm(data)
rm(data_new)

##############
#[2] fuel_gasoline
############
#dir_data <- r'(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\Data\IEA2018\World Energy Prices\)'
data <- read.csv(paste0(dir_data,"world energy prices transport.csv"))
data<-subset(data,PRODUCT%in%c("Regular motor gasoline (litre)","Mid-grade motor gasoline (litre)","High-grade gasoline (litre)"))
data<-subset(data,UNIT=="Total price (USD/unit using PPP)")

id_years <- subset( colnames(data),!( colnames(data)%in%c("COUNTRY","SECTOR","PRODUCT","UNIT")))

#clean data  
for (i in 1:length(id_years))
{
  #i<-1
  data[,id_years[i]] <- as.numeric(data[,id_years[i]])  
}

#subset to unit of interest 
dim(data)
data <- subset(data,UNIT=="Total price (USD/unit using PPP)")
dim(data)

data_new <- melt(data,id.vars = c("COUNTRY","SECTOR","PRODUCT","UNIT"), measure.vars = id_years ) 
data_new$Year<- as.numeric(gsub("X","",data_new$variable))
data_new <- subset(data_new, Year >=2010)
data_new<-aggregate(list(price=data_new$value),list(Country.Name=data_new$COUNTRY,
                                                    UNIT=data_new$UNIT),function(x){mean(x,na.rm=TRUE)})
data_new$unit_denominator<-"liter"
data_new$unit_type<-"volume"
data_new$fuel <-"fuel_gasoline" 	

#merge with iso_code3
data_new$Country.Name <- gsub("Bolivarian Rep. of Venezuela" , "Venezuela",data_new$Country.Name)
data_new$Country.Name <- gsub("Czech Republic" , "Czechia",data_new$Country.Name)
data_new$Country.Name <- gsub("Hong Kong (China)" , "Hong Kong SAR, China",data_new$Country.Name)
data_new$Country.Name <- gsub("Islamic Republic of Iran" , "Iran",data_new$Country.Name)
data_new$Country.Name <- gsub("Kyrgyzstan" , "Kyrgyz Republic",data_new$Country.Name)
data_new$Country.Name <- gsub("People's Republic of China" , "China",data_new$Country.Name)
data_new$Country.Name <- gsub("Plurinational State of Bolivia" , "Bolivia",data_new$Country.Name)
data_new$Country.Name <- gsub("Republic of Moldova" , "Moldova",data_new$Country.Name)
data_new$Country.Name <- gsub("United Republic of Tanzania" , "Tanzania",data_new$Country.Name)
data_new$Country.Name <- gsub("Viet Nam" ,"Vietnam",data_new$Country.Name)

#merge 
data_new<-merge(data_new,iso_code,by="Country.Name")
data_new$iso_code3<-data_new$ISO3
data_new$ISO3<-NULL

#input missing values 
data_new$price <- ifelse(is.na(data_new$price)==TRUE,mean(data_new$price,na.rm=TRUE),  data_new$price)
subset(data_new,Country.Name%in%c("Mexico","Ecuador","Brazil","Chile"))
data2<-data_new
rm(data)
rm(data_new)

################################################################
#[3] fuel_diesel
#################################################################
#dir_data <- r'(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\Data\IEA2018\World Energy Prices\)'
data <- read.csv(paste0(dir_data,"world energy prices transport.csv"))
data<-subset(data,PRODUCT%in%c("Automotive diesel (litre)"))
data<-subset(data,UNIT=="Total price (USD/unit using PPP)")

id_years <- subset( colnames(data),!( colnames(data)%in%c("COUNTRY","SECTOR","PRODUCT","UNIT")))

#clean data  
for (i in 1:length(id_years))
{
  #i<-1
  data[,id_years[i]] <- as.numeric(data[,id_years[i]])  
}

#subset to unit of interest 
dim(data)
data <- subset(data,UNIT=="Total price (USD/unit using PPP)")
dim(data)

data_new <- melt(data,id.vars = c("COUNTRY","SECTOR","PRODUCT","UNIT"), measure.vars = id_years ) 
data_new$Year<- as.numeric(gsub("X","",data_new$variable))
data_new <- subset(data_new, Year >=2010)
data_new<-aggregate(list(price=data_new$value),list(Country.Name=data_new$COUNTRY,
                                                    UNIT=data_new$UNIT),function(x){mean(x,na.rm=TRUE)})
data_new$unit_denominator<-"liter"
data_new$unit_type<-"volume"
data_new$fuel <-"fuel_diesel" 	

#merge with iso_code3
data_new$Country.Name <- gsub("Bolivarian Rep. of Venezuela" , "Venezuela",data_new$Country.Name)
data_new$Country.Name <- gsub("Czech Republic" , "Czechia",data_new$Country.Name)
data_new$Country.Name <- gsub("Hong Kong (China)" , "Hong Kong SAR, China",data_new$Country.Name)
data_new$Country.Name <- gsub("Islamic Republic of Iran" , "Iran",data_new$Country.Name)
data_new$Country.Name <- gsub("Kyrgyzstan" , "Kyrgyz Republic",data_new$Country.Name)
data_new$Country.Name <- gsub("People's Republic of China" , "China",data_new$Country.Name)
data_new$Country.Name <- gsub("Plurinational State of Bolivia" , "Bolivia",data_new$Country.Name)
data_new$Country.Name <- gsub("Republic of Moldova" , "Moldova",data_new$Country.Name)
data_new$Country.Name <- gsub("United Republic of Tanzania" , "Tanzania",data_new$Country.Name)
data_new$Country.Name <- gsub("Viet Nam" ,"Vietnam",data_new$Country.Name)

#merge 
data_new<-merge(data_new,iso_code,by="Country.Name")
data_new$iso_code3<-data_new$ISO3
data_new$ISO3<-NULL

#input missing values 
data_new$price <- ifelse(is.na(data_new$price)==TRUE,mean(data_new$price,na.rm=TRUE),  data_new$price)
subset(data_new,Country.Name%in%c("Mexico","Ecuador","Brazil","Chile"))
data3<-data_new
rm(data)
rm(data_new)


################################################
#[4] fuel_oil
################################################
#dir_data <- r'(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\Data\IEA2018\Energy Prices and Taxes 3Q2018\End-Use Prices\)'
data <- read.csv(paste0(dir_data,"end_us.csv"))
#fix data 
id_years <- subset( colnames(data),!( colnames(data)%in%c("COUNTRY","PRODUCT","SECTOR","FLOW")))
omits <-subset(id_years,grepl("Q",id_years)==TRUE)
id_years <- subset(id_years,!(id_years%in%omits))
data[,omits]<-NULL

data<-subset(data,PRODUCT%in%c("High sulphur fuel oil (tonne)","Low sulphur fuel oil (tonne)"  ))
data<-subset(data,FLOW=="Total price (USD/unit using PPP)")
head(data)

#clean data  
for (i in 1:length(id_years))
{
  #i<-1
  data[,id_years[i]] <- as.numeric(data[,id_years[i]])  
}

head(data)

data_new <- melt(data,id.vars = c("COUNTRY","SECTOR","PRODUCT","FLOW"), measure.vars = id_years ) 
data_new$Year<- as.numeric(gsub("X","",data_new$variable))
data_new <- subset(data_new, Year >=2010)
data_new<-aggregate(list(price=data_new$value),list(Country.Name=data_new$COUNTRY,
                                                    UNIT=data_new$FLOW),function(x){mean(x,na.rm=TRUE)})
data_new<-merge(iso_code,data_new,by="Country.Name",all.x=TRUE)
data_new$iso_code3<-data_new$ISO3
data_new$ISO3<-NULL

data_new$unit_denominator<-"tonne"
data_new$unit_type<-"volume"
data_new$fuel <-"fuel_oil" 	
data_new$UNIT <- unique(data_new$UNIT)[2]

#input missing values 
input_val <- subset(data_new,iso_code3=="USA")$price
data_new$price <- ifelse(is.na(data_new$price)==TRUE,input_val,  data_new$price)
subset(data_new,Country.Name%in%c("Mexico","Ecuador","Brazil","Chile"))
data4<-data_new
rm(data)
rm(data_new)

#########################################################
# [5] fuel_coal
########################################################
#dir_data <- r'(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\Data\IEA2018\Energy Prices and Taxes 3Q2018\End-Use Prices\)'
data <- read.csv(paste0(dir_data,"end_us.csv"))
#fix data 
id_years <- subset( colnames(data),!( colnames(data)%in%c("COUNTRY","PRODUCT","SECTOR","FLOW")))
omits <-subset(id_years,grepl("Q",id_years)==TRUE)
id_years <- subset(id_years,!(id_years%in%omits))
data[,omits]<-NULL

data<-subset(data,PRODUCT%in%c("Steam coal (tonne)","Coking coal (tonne)"))
data<-subset(data,FLOW=="Total price (USD/unit using PPP)")
head(data)

#clean data  
for (i in 1:length(id_years))
{
  #i<-1
  data[,id_years[i]] <- as.numeric(data[,id_years[i]])  
}

head(data)

data_new <- melt(data,id.vars = c("COUNTRY","SECTOR","PRODUCT","FLOW"), measure.vars = id_years ) 
data_new$Year<- as.numeric(gsub("X","",data_new$variable))
data_new <- subset(data_new, Year >=2010)
data_new<-aggregate(list(price=data_new$value),list(Country.Name=data_new$COUNTRY,
                                                    UNIT=data_new$FLOW),function(x){mean(x,na.rm=TRUE)})
data_new<-merge(iso_code,data_new,by="Country.Name",all.x=TRUE)
data_new$iso_code3<-data_new$ISO3
data_new$ISO3<-NULL

data_new$unit_denominator<-"tonne"
data_new$unit_type<-"volume"
data_new$fuel <-"fuel_coal" 	
data_new$UNIT <- unique(data_new$UNIT)[2]

#input missing values 
input_val <- subset(data_new,iso_code3=="USA")$price
data_new$price <- ifelse(is.na(data_new$price)==TRUE,input_val,  data_new$price)
subset(data_new,Country.Name%in%c("Mexico","Ecuador","Brazil","Chile"))
data5<-data_new
rm(data)
rm(data_new)

#######################################
# [6] fuel_natural_gas
########################################
#dir_data <- r'(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\Data\IEA2018\Energy Prices and Taxes 3Q2018\End-Use Prices\)'
data <- read.csv(paste0(dir_data,"end_us.csv"))
#fix data 
id_years <- subset( colnames(data),!( colnames(data)%in%c("COUNTRY","PRODUCT","SECTOR","FLOW")))
omits <-subset(id_years,grepl("Q",id_years)==TRUE)
id_years <- subset(id_years,!(id_years%in%omits))
data[,omits]<-NULL

data<-subset(data,PRODUCT%in%c("Natural gas (MWh)"))
data<-subset(data,FLOW=="Total price (USD/unit using PPP)")
head(data)

#clean data  
for (i in 1:length(id_years))
{
  #i<-1
  data[,id_years[i]] <- as.numeric(data[,id_years[i]])  
}

head(data)

data_new <- melt(data,id.vars = c("COUNTRY","SECTOR","PRODUCT","FLOW"), measure.vars = id_years ) 
data_new$Year<- as.numeric(gsub("X","",data_new$variable))
data_new <- subset(data_new, Year >=2010)
data_new<-aggregate(list(price=data_new$value),list(Country.Name=data_new$COUNTRY,
                                                    UNIT=data_new$FLOW),function(x){mean(x,na.rm=TRUE)})
data_new<-merge(iso_code,data_new,by="Country.Name",all.x=TRUE)
data_new$iso_code3<-data_new$ISO3
data_new$ISO3<-NULL

data_new$unit_denominator<-"MWH"
data_new$unit_type<-"energy produced"
data_new$fuel <-"fuel_natural_gas" 	
data_new$UNIT <- unique(data_new$UNIT)[2]

#input missing values 
input_val <- subset(data_new,iso_code3=="USA")$price
data_new$price <- ifelse(is.na(data_new$price)==TRUE,input_val,  data_new$price)
subset(data_new,Country.Name%in%c("Mexico","Ecuador","Brazil","Chile"))
data6<-data_new
rm(data)
rm(data_new)

##########################################################
#[7] fuel_coke
###########################################################
#dir_data <- r'(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\Data\IEA2018\Energy Prices and Taxes 3Q2018\End-Use Prices\)'
data <- read.csv(paste0(dir_data,"end_us.csv"))
#fix data 
id_years <- subset( colnames(data),!( colnames(data)%in%c("COUNTRY","PRODUCT","SECTOR","FLOW")))
omits <-subset(id_years,grepl("Q",id_years)==TRUE)
id_years <- subset(id_years,!(id_years%in%omits))
data[,omits]<-NULL

data<-subset(data,PRODUCT%in%c("Coking coal (tonne)"))
data<-subset(data,FLOW=="Total price (USD/unit using PPP)")
head(data)

#clean data  
for (i in 1:length(id_years))
{
  #i<-1
  data[,id_years[i]] <- as.numeric(data[,id_years[i]])  
}

head(data)

data_new <- melt(data,id.vars = c("COUNTRY","SECTOR","PRODUCT","FLOW"), measure.vars = id_years ) 
data_new$Year<- as.numeric(gsub("X","",data_new$variable))
data_new <- subset(data_new, Year >=2010)
data_new<-aggregate(list(price=data_new$value),list(Country.Name=data_new$COUNTRY,
                                                    UNIT=data_new$FLOW),function(x){mean(x,na.rm=TRUE)})
data_new<-merge(iso_code,data_new,by="Country.Name",all.x=TRUE)
data_new$iso_code3<-data_new$ISO3
data_new$ISO3<-NULL

data_new$unit_denominator<-"tonne"
data_new$unit_type<-"volume"
data_new$fuel <-"fuel_coke" 	
data_new$UNIT <- unique(data_new$UNIT)[2]

#input missing values 
input_val <- subset(data_new,iso_code3=="USA")$price
data_new$price <- ifelse(is.na(data_new$price)==TRUE,input_val,  data_new$price)
subset(data_new,Country.Name%in%c("Mexico","Ecuador","Brazil","Chile"))
data7<-data_new
rm(data)
rm(data_new)

###########################################################
#[8] fuel_kerosene
###########################################################
#dir_data <- r'(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\Data\IEA2018\World Energy Prices\)'
data <- read.csv(paste0(dir_data,"world energy prices other products.csv"))
ids <- strsplit(data$TIMESERIES,"\\.")
ids <- data.frame(do.call("rbind", ids))
colnames(ids) <- c("Nation","Product_Unit","Sector")
data <- cbind(ids,data)
product_ids <- strsplit(unique(data$Product_Unit)," \\(")
product_ids <- data.frame(do.call("rbind", product_ids))
colnames(product_ids) <- c("Product","Unit")
product_ids$Unit <- gsub("\\)","",product_ids$Unit)
data <- cbind(product_ids,data)
data$Product_Unit <- NULL 
data$TIMESERIES <- NULL 

id_years <- subset( colnames(data),!( colnames(data)%in%c("Product","Unit","Nation","Sector","UNIT")))

#clean data  
for (i in 1:length(id_years))
{
  #i<-1
  data[,id_years[i]] <- as.numeric(data[,id_years[i]])  
}

#subset to unit of interest 
dim(data)
data <- subset(data,Product=="Kerosene")
dim(data)

#subset to price of interest 
dim(data)
data <- subset(data,UNIT=="Total price (USD/unit)")
dim(data)

data_new <- melt(data,id.vars = c("Product","Unit","Nation","Sector","UNIT"), measure.vars = id_years ) 
data_new$Year<- as.numeric(gsub("X","",data_new$variable))
data_new <- subset(data_new, Year >=2010)
data_new<-aggregate(list(price=data_new$value),list(Country.Name=data_new$Nation,
                                                    UNIT=data_new$UNIT),function(x){mean(x,na.rm=TRUE)})
data_new<-merge(iso_code,data_new,by="Country.Name",all.x=TRUE)
data_new$iso_code3<-data_new$ISO3
data_new$ISO3<-NULL

data_new$unit_denominator<-"1000 liters"
data_new$unit_type<-"volume"
data_new$fuel <-"fuel_kerosene" 	
data_new$UNIT <- unique(data_new$UNIT)[2]

#input missing values 
input_val <- mean(data_new$price,na.rm=TRUE)
data_new$price <- ifelse(is.na(data_new$price)==TRUE,input_val,  data_new$price)
subset(data_new,Country.Name%in%c("Mexico","Ecuador","Brazil","Chile"))
data8<-data_new
rm(data)
rm(data_new)

#########################################################################
# [9] fuel_biofuels
#########################################################################
#dir_data <- r'(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\Data\IEA2018\World Energy Prices\)'
data <- read.csv(paste0(dir_data,"world energy prices other products.csv"))
ids <- strsplit(data$TIMESERIES,"\\.")
ids <- data.frame(do.call("rbind", ids))
colnames(ids) <- c("Nation","Product_Unit","Sector")
data <- cbind(ids,data)
product_ids <- strsplit(unique(data$Product_Unit)," \\(")
product_ids <- data.frame(do.call("rbind", product_ids))
colnames(product_ids) <- c("Product","Unit")
product_ids$Unit <- gsub("\\)","",product_ids$Unit)
data <- cbind(product_ids,data)
data$Product_Unit <- NULL 
data$TIMESERIES <- NULL 

id_years <- subset( colnames(data),!( colnames(data)%in%c("Product","Unit","Nation","Sector","UNIT")))

#clean data  
for (i in 1:length(id_years))
{
  #i<-1
  data[,id_years[i]] <- as.numeric(data[,id_years[i]])  
}

#subset to unit of interest 
dim(data)
data <- subset(data,Product=="Bioethanol")
dim(data)

#subset to price of interest 
dim(data)
data <- subset(data,UNIT=="Total price (USD/unit using PPP)")
dim(data)

data_new <- melt(data,id.vars = c("Product","Unit","Nation","Sector","UNIT"), measure.vars = id_years ) 
data_new$Year<- as.numeric(gsub("X","",data_new$variable))
data_new <- subset(data_new, Year >=2010)
data_new<-aggregate(list(price=data_new$value),list(Country.Name=data_new$Nation,
                                                    UNIT=data_new$UNIT),function(x){mean(x,na.rm=TRUE)})
data_new<-merge(iso_code,data_new,by="Country.Name",all.x=TRUE)
data_new$iso_code3<-data_new$ISO3
data_new$ISO3<-NULL

data_new$unit_denominator<-"1000 liter"
data_new$unit_type<-"volume"
data_new$fuel <-"fuel_biofuels" 	
data_new$UNIT <- unique(data_new$UNIT)[2]

#input missing values 
input_val <- mean(data_new$price,na.rm=TRUE)
data_new$price <- ifelse(is.na(data_new$price)==TRUE,input_val,  data_new$price)
subset(data_new,Country.Name%in%c("Mexico","Ecuador","Brazil","Chile"))
data9<-data_new
rm(data)
rm(data_new)

####the remaining costs are estimated based on comparisons with the ones for which we have data 

###########################
# [10] fuel_biogas
###########################
#https://www.iea.org/reports/outlook-for-biogas-and-biomethane-prospects-for-organic-growth/sustainable-supply-potential-and-costs
data10 <- data9 
data10$fuel <- "fuel_biogas"
data10$unit_type <- "energy produced"
data10$unit_denominator <- "MBtu"
data10$price <- 22
head(data10)

##########################
# [11] fuel_biomass
#########################
#https://www.eia.gov/biofuels/biomass/#:~:text=Domestic%20sales%20of%20densified%20biomass,and%20averaged%20%24223.78%20per%20ton.
data11 <- data9 
data11$fuel <- "fuel_biomass"
data11$unit_type <- "volume"
data11$unit_denominator <- "tonne"
data11$price <- 209.78
head(data11)

###########################
# [12] fuel_crude
###########################
data12 <- data4 
data12$fuel <- "fuel_crude"
data12$unit_type <- "volume"
data12$unit_denominator <- "tonne"
data12$price <- data12$price*0.70
head(data12)

#########################
## [13] fuel_waste
##########################
#https://www.iea.org/reports/outlook-for-biogas-and-biomethane-prospects-for-organic-growth/sustainable-supply-potential-and-costs
data13 <- data9 
data13$fuel <- "fuel_waste"
data13$unit_type <- "energy produced"
data13$unit_denominator <- "MBtu"
data13$price <- 13.4*0.7
head(data13)

#######################
## [14] fuel_furnace_gas
##################
#dir_data <- r'(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\Data\IEA2018\World Energy Prices\)'
data <- read.csv(paste0(dir_data,"world energy prices other products.csv"))
ids <- strsplit(data$TIMESERIES,"\\.")
ids <- data.frame(do.call("rbind", ids))
colnames(ids) <- c("Nation","Product_Unit","Sector")
data <- cbind(ids,data)
product_ids <- strsplit(unique(data$Product_Unit)," \\(")
product_ids <- data.frame(do.call("rbind", product_ids))
colnames(product_ids) <- c("Product","Unit")
product_ids$Unit <- gsub("\\)","",product_ids$Unit)
data <- cbind(product_ids,data)
data$Product_Unit <- NULL 
data$TIMESERIES <- NULL 

id_years <- subset( colnames(data),!( colnames(data)%in%c("Product","Unit","Nation","Sector","UNIT")))

#clean data  
for (i in 1:length(id_years))
{
  #i<-1
  data[,id_years[i]] <- as.numeric(data[,id_years[i]])  
}

#subset to unit of interest 
dim(data)
data <- subset(data,Product=="Liquified Petroleum Gas")
dim(data)

#subset to price of interest 
dim(data)
data <- subset(data,UNIT=="Total price (USD/unit using PPP)")
dim(data)

data_new <- melt(data,id.vars = c("Product","Unit","Nation","Sector","UNIT"), measure.vars = id_years ) 
data_new$Year<- as.numeric(gsub("X","",data_new$variable))
data_new <- subset(data_new, Year >=2010)
data_new <- subset(data_new,Sector=="Transport")
data_new<-aggregate(list(price=data_new$value),list(Country.Name=data_new$Nation,
                                                    UNIT=data_new$UNIT),function(x){mean(x,na.rm=TRUE)})
data_new<-merge(iso_code,data_new,by="Country.Name",all.x=TRUE)
data_new$iso_code3<-data_new$ISO3
data_new$ISO3<-NULL

data_new$unit_denominator<-"liter"
data_new$unit_type<-"volume"
data_new$fuel <-"fuel_furnace_gas" 	
data_new$UNIT <- unique(data_new$UNIT)[2]

#input missing values 
input_val <- mean(data_new$price,na.rm=TRUE)
data_new$price <- ifelse(is.na(data_new$price)==TRUE,input_val,  data_new$price)
subset(data_new,Country.Name%in%c("Mexico","Ecuador","Brazil","Chile"))
data14<-data_new
rm(data)
rm(data_new)

###################################
#[15]fuel_hydrogen
###################################
#https://stillwaterassociates.com/how-does-the-cost-of-hydrogen-stack-up-against-gasoline/#:~:text=In%202021%2C%20hydrogen%20retailed%20%248.50,or%20conventional%20gasoline%20vehicles%20respectively.
data15 <- data2 
data15$fuel <- "fuel_hydrogen"
data15$unit_type <- "volume"
data15$unit_denominator <- "liter"
data15$price <- data15$price*3.0  
head(data15)

###################################
#[16] fuel_hydrocarbon_gas_liquids
##################################
#dir_data <- r'(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\Data\IEA2018\World Energy Prices\)'
data <- read.csv(paste0(dir_data,"world energy prices other products.csv"))
ids <- strsplit(data$TIMESERIES,"\\.")
ids <- data.frame(do.call("rbind", ids))
colnames(ids) <- c("Nation","Product_Unit","Sector")
data <- cbind(ids,data)
product_ids <- strsplit(unique(data$Product_Unit)," \\(")
product_ids <- data.frame(do.call("rbind", product_ids))
colnames(product_ids) <- c("Product","Unit")
product_ids$Unit <- gsub("\\)","",product_ids$Unit)
data <- cbind(product_ids,data)
data$Product_Unit <- NULL 
data$TIMESERIES <- NULL 

id_years <- subset( colnames(data),!( colnames(data)%in%c("Product","Unit","Nation","Sector","UNIT")))

#clean data  
for (i in 1:length(id_years))
{
  #i<-1
  data[,id_years[i]] <- as.numeric(data[,id_years[i]])  
}

#subset to unit of interest 
dim(data)
data <- subset(data,Product=="Ethane")
dim(data)

#subset to price of interest 
dim(data)
data <- subset(data,UNIT=="Total price (USD/unit using PPP)")
dim(data)

data_new <- melt(data,id.vars = c("Product","Unit","Nation","Sector","UNIT"), measure.vars = id_years ) 
data_new$Year<- as.numeric(gsub("X","",data_new$variable))
data_new <- subset(data_new, Year >=2010)
data_new<-aggregate(list(price=data_new$value),list(Country.Name=data_new$Nation,
                                                    UNIT=data_new$UNIT),function(x){mean(x,na.rm=TRUE)})
data_new<-merge(iso_code,data_new,by="Country.Name",all.x=TRUE)
data_new$iso_code3<-data_new$ISO3
data_new$ISO3<-NULL

data_new$unit_denominator<-"Mwh"
data_new$unit_type<-"energy produced"
data_new$fuel <-"fuel_hydrocarbon_gas_liquids" 	
data_new$UNIT <- unique(data_new$UNIT)[2]

#input missing values 
input_val <- mean(data_new$price,na.rm=TRUE)
data_new$price <- ifelse(is.na(data_new$price)==TRUE,input_val,  data_new$price)
subset(data_new,Country.Name%in%c("Mexico","Ecuador","Brazil","Chile"))
data16<-data_new
rm(data)
rm(data_new)

#rbdind all

all <- rbind(data1,data2,data3,data4,data5,data6,data7,data8,data9,data10,data11,data12,data13,data14,data15,data16)

dir_output <- file.path(dirname(file.path(FILE_PATH,"..")), "input_to_sisepuede")
dir_file_output <- file.path(dir_output, "fuel_prices.csv")

write.csv(all,'(fuel_prices.csv)')
