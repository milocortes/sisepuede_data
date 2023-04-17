#process livestock data for afolu
#dir_data<- r"(C:\Users\L03537818\Documents\tec\R)"
dir_data<- r"(C:\Users\L03537818\Documents\tec\R\)"
data<-read.csv(paste0(dir_data,"FAOSTAT_data_7-6-2022.csv"))
#edit mate
data$Item<-gsub("MatÃ©","Mate",data$Item)

#subset to countries of interest
#dir_countries<-r"(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\)"
dir_countries<-r"(C:\Users\L03537818\Documents\tec\R\)"
countries<-read.csv(paste0(dir_countries,"CountriesList.csv"))
countries<-countries[,c("Nation_Fao","nation_SISEPUEDE")]
countries$Nation<-countries$nation_SISEPUEDE
countries$nation_SISEPUEDE<-NULL
#
dim(data)
data<-subset(data,Area%in%unique(countries$Nation_Fao))
dim(data)


#subset to classifications of interest
#items<-read.csv(paste0(dir_data,"items_classification.csv"))
#get data_crosswalk
#write.csv(read.csv("https://raw.githubusercontent.com/egobiernoytp/lac_decarbonization/main/ref/data_crosswalks/fao_crop_categories.csv"),paste0(dir_data,"fao_crop_categories.csv"),row.names=FALSE)
cw<-read.csv("https://raw.githubusercontent.com/egobiernoytp/lac_decarbonization/main/ref/data_crosswalks/fao_crop_categories.csv")
colnames(cw)<-c( "Item", "cat_1","sisepuede_item","super_cat")
#cw$Item<-gsub("MatÃƒÂ©","Mate",cw$Item)

#add cw to data and aggregate by yield means
data<-merge(data,cw,by="Item")

data<-aggregate(list(Value=data$Value),list(Area=data$Area,
                                            Year=data$Year,
                                            Item=data$sisepuede_item,
                                            Unit=data$Unit),function(x) {mean(x,na.rm=TRUE)})



#to create table, load template
#dir_template<-r"(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\Git-LAC-Calib\lac_decarbonization\calibration\AFOLU\SupportData\)"
dir_template<-r"(C:\Users\Usuario\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\Git-LAC-Calib\lac_decarbonization\calibration\AFOLU\SupportData\)"
template<-read.csv(paste0(dir_template,"data_template.csv"))

for ( i in 1:length(unique(cw$sisepuede_item)))
#
{
#i<-9
 pivot<-subset(data,Item==unique(cw$sisepuede_item)[i])[,c("Area","Year","Unit","Value")]
 pivot$Nation_Fao<-pivot$Area
 pivot$Area<-NULL
 file_name<-paste0("yf_agrc_",unique(cw$sisepuede_item)[i],"_tonne_ha")
 pivot[,file_name]<-pivot$Value
 pivot$Value<-NULL
 pivot<-merge(pivot,countries[,c("Nation_Fao","Nation")],by="Nation_Fao")
 pivot$Nation_Fao<-NULL

#merge pivot with templeate
 pivot<-Reduce(function(...) merge(..., all.x=T), list(template,pivot))
 pivot<-pivot[order(pivot$Nation,pivot$Year),]
#merge with medians to input missing values
 means<-aggregate(list(mean_var=pivot[,file_name]),list(Nation=pivot$Nation),function(x) {median(x,na.rm=TRUE)})
 pivot<-merge(pivot,means,by="Nation")
#input values
 pivot[,file_name]<-ifelse(is.na(pivot[,file_name])==TRUE,pivot$mean_var,pivot[,file_name])
 pivot[,file_name]<-ifelse(is.na(pivot[,file_name])==TRUE,0,pivot[,file_name])
 pivot$mean_var<-NULL
 #change units
 pivot[,file_name]<-pivot[,file_name]/10000 # 1[ton]=10000 [hg]
 pivot$Unit<-"tonne/ha"  #subset(unique(pivot$Unit),is.na(unique(pivot$Unit))==FALSE)
 write.csv(pivot,paste0(dir_data,file_name,".csv"),row.names=FALSE)
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
