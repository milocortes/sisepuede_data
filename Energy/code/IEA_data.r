
#dir_data <-r"(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\calibration_lac_dec\observed_data\Energy\cost_enfu_fuel_coal_usd_per_m3\raw_data\)"
dir_data <-r"(C:\Users\AP03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\Data\IEA2018\World Energy Balances\)"
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


#










summary(datan)

means_table <- aggregate(list(Mean=datan$Mean),list(FLOW = datan$FLOW, PRODUCT = datan$PRODUCT,UNIT = datan$UNIT),mean, na.rm=TRUE)
subset(means_table, FLOW == "Average net calorific value")
subset(means_table, FLOW == "NCV in industry")

subset(means_table, FLOW == "NCV in main activity producer electricity plants")




subset(datan, FLOW == "Average net calorific value")[,c("FLOW","COUNTRY","PRODUCT","Mean")]




test<-subset(data,FLOW=="Average net calorific value")
test<-subset(test,UNIT=="toe/t")
#test<-subset(test,TIME>=2000)
test<-subset(test,COUNTRY=="Mexico")





#Got it
#estimate TJ per fuel  using IEA 
#then divide by total value added in industry 
#

efficfactor_enfu_industrial_energy_fuel_biomass
efficfactor_enfu_industrial_energy_fuel_coal
efficfactor_enfu_industrial_energy_fuel_coke
efficfactor_enfu_industrial_energy_fuel_diesel
efficfactor_enfu_industrial_energy_fuel_electricity
efficfactor_enfu_industrial_energy_fuel_gas_furnace
efficfactor_enfu_industrial_energy_fuel_gas_petroleum_liquid
efficfactor_enfu_industrial_energy_fuel_gasoline
efficfactor_enfu_industrial_energy_fuel_hydrogen
efficfactor_enfu_industrial_energy_fuel_kerosene
efficfactor_enfu_industrial_energy_fuel_natural_gas
efficfactor_enfu_industrial_energy_fuel_oil
efficfactor_enfu_industrial_energy_fuel_solar

test<-subset(data,FLOW=="Industry")
test<-subset(test,UNIT=="TJ")
test<-subset(test,TIME>=2000)
test<-subset(test,COUNTRY=="Mexico")

ids<-c("COUNTRY","FLOW","UNIT","TIME")

vars<-subset(colnames(test),!(colnames(test)%in%ids))

for (i in 1:length(vars))
{
 print( unique(test[,vars[i]]) )  
}

for (i in 1:length(vars))
{
 test[,vars[i]] <- ifelse(test[,vars[i]]=="x",NA,test[,vars[i]])
 test[,vars[i]] <- ifelse(test[,vars[i]]=="..",NA,test[,vars[i]])  
 test[,vars[i]] <- as.numeric(as.character(test[,vars[i]] ) )
}



strsplit(data$TIMESERIES, ".")