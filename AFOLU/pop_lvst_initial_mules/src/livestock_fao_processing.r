#process livestock data for afolu
dir_data<- r"(C:\Users\Usuario\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\Git-LAC-Calib\lac_decarbonization\calibration\AFOLU\SupportData\livestock_fao_data\)"
#dir_data<- r"(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\Git-LAC-Calib\lac_decarbonization\calibration\AFOLU\SupportData\livestock_fao_data\)"
data<-read.csv(paste0(dir_data,"FAOSTAT_data_7-4-2022(2).csv"))


#subset to countries of interest
dir_countries<-r"(C:\Users\Usuario\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\)"
#dir_countries<-r"(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\)"
countries<-read.csv(paste0(dir_countries,"CountriesList.csv"))
countries<-countries[,c("Nation_Fao","nation_SISEPUEDE")]
countries$Nation<-countries$nation_SISEPUEDE
countries$nation_SISEPUEDE<-NULL
#
dim(data)
data<-subset(data,Area%in%unique(countries$Nation_Fao))
dim(data)


#subset to classifications of interest
items<-read.csv(paste0(dir_data,"items_classification.csv"))

#to create table, load template
dir_template<-r"(C:\Users\Usuario\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\Git-LAC-Calib\lac_decarbonization\calibration\AFOLU\SupportData\)"
#dir_template<-r"(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\Git-LAC-Calib\lac_decarbonization\calibration\AFOLU\SupportData\)"
template<-read.csv(paste0(dir_template,"data_template.csv"))

for ( i in 1:length(items$Item_Fao))
#
{
#i<-9
 pivot<-subset(data,Item==items$Item_Fao[i])[,c("Area","Year","Unit","Value")]
 pivot$Nation_Fao<-pivot$Area
 pivot$Area<-NULL
 pivot[,items$File_Sisepuede[i]]<-pivot$Value
 pivot$Value<-NULL
 pivot<-merge(pivot,countries[,c("Nation_Fao","Nation")],by="Nation_Fao")
 pivot$Nation_Fao<-NULL

#merge pivot with templeate
 pivot<-Reduce(function(...) merge(..., all.x=T), list(template,pivot))
 pivot<-pivot[order(pivot$Nation,pivot$Year),]
#merge with medians to input missing values
 means<-aggregate(list(mean_var=pivot[,items$File_Sisepuede[i]]),list(Nation=pivot$Nation),function(x) {median(x,na.rm=TRUE)})
 pivot<-merge(pivot,means,by="Nation")
#input values
 pivot[,items$File_Sisepuede[i]]<-ifelse(is.na(pivot[,items$File_Sisepuede[i]])==TRUE,pivot$mean_var,pivot[,items$File_Sisepuede[i]])
 pivot[,items$File_Sisepuede[i]]<-ifelse(is.na(pivot[,items$File_Sisepuede[i]])==TRUE,0,pivot[,items$File_Sisepuede[i]])
 pivot$mean_var<-NULL
 pivot$Unit<-subset(unique(pivot$Unit),is.na(unique(pivot$Unit))==FALSE)
 write.csv(pivot,paste0(dir_data,items$File_Sisepuede[i],".csv"),row.names=FALSE)
 rm(pivot)
 rm(means)
}





#subset to items of interest and print corresponding table
#buffalo= "Buffaloes"
#cattle_dairy = "Cattle"
#cattle_nondairy = 30% of total cattle
#chickens = "Chickens"
#goats = "Goats"
#horses = "Horses"
#mules= "Asses"
#pigs = "Pigs"
#sheep = "Sheep"




"Asses"
"Camels"
"Cattle"
"Chickens"
"Goats"
"Horses"
"Mules"
"Sheep"
"Beehives"
"Ducks"
"Geese and guinea fowls"
 "Pigs"
 "Turkeys"
 "Rabbits and hares"
"Camelids, other"
"Rodents, other"
