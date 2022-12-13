


#first go for socio economic  
data_in_projected<-r"(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\Git-LAC-Calib\lac_decarbonization\calibration\SocioEconomic\input_to_sisepuede\projected_data\)"
data_in_historic<-r"(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\Git-LAC-Calib\lac_decarbonization\calibration\SocioEconomic\input_to_sisepuede\historical_data\)"

#population
#pop<-read.csv(paste0(data_in,'pop_all_future.csv'))
pop_rural_h<-read.csv(paste0(data_in_historic,'population_gnrl_rural.csv'))
pop_rural_p<-read.csv(paste0(data_in_projected,'population_gnrl_rural.csv'))
pop_rural_p<-subset(pop_rural_p,Year>max(pop_rural_h$Year))

pop_rural <- rbind(pop_rural_h,pop_rural_p)

pop_urban_h<-read.csv(paste0(data_in_historic,'population_gnrl_urban.csv'))
pop_urban_p<-read.csv(paste0(data_in_projected,'population_gnrl_urban.csv'))
pop_urban_p<-subset(pop_urban_p,Year>max(pop_urban_h$Year))

pop_urban <- rbind(pop_urban_h,pop_urban_p)


#add gdp
#gdp<-read.csv(paste0(data_in,'gdp_all_future.csv'))

gdp_h<-read.csv(paste0(data_in_historic,'gdp_mmm_usd.csv'))
gdp_p<-read.csv(paste0(data_in_projected,'gdp_mmm_usd.csv'))
gdp <- rbind(gdp_h,gdp_p)

#add ha
#areas<-read.csv(paste0(data_in,'areas_future.csv'))
areas<-read.csv(paste0(data_in,'area_gnrl_country_ha.csv'))

#merge the three socio-economic variables
dim(gdp)
dim(areas)
dim(pop_rural)
dim(pop_urban)

#subset to target nations
target_nations<-read.csv(r"(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\CountriesList.csv)")$iso_code3
gdp<-subset(gdp,Year>2010 & iso_code3%in%target_nations)
dim(gdp)

areas<-subset(areas,iso_code3%in%target_nations)[,c("area_gnrl_country_ha","iso_code3")]
dim(areas)

pop_rural<-subset(pop_rural,Year>2010 & iso_code3%in%target_nations)
dim(pop_rural)
pop_rural$Nation<-NULL

pop_urban<-subset(pop_urban,Year>2010 & iso_code3%in%target_nations)
dim(pop_urban)
pop_urban$Nation<-NULL

#merge all socio-econoimc 
DataIn <-Reduce(function(...) merge(...,), list(gdp,pop_rural,pop_urban,areas))
dim(DataIn)
head(DataIn)

#now add all variables 
dir_data<- r"(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\calibration_lac_dec\observed_data\Energy\)"
files<-list.files(dir_data)
files<-subset(files,!(files%in%c("code","input_to_sisepuede","raw_data","nada.txt","nemomod_entc_residual_capacity_pp_waste_incineration_gw","README.md")))
files

for (i in 1:length(files))
{
#i<-1
target_dir_historial <- r"(\input_to_sisepuede\historical\)"
target_dir_projected <- r"(\input_to_sisepuede\projected\)"
historical<-read.csv(paste0(dir_data,files[i],target_dir_historial,files[i],".csv"))
projected<-read.csv(paste0(dir_data,files[i],target_dir_projected,files[i],".csv"))
all <- rbind(historical,projected)
dim(all)
all <-subset(all,Year%in%unique(DataIn$Year) & iso_code3%in%target_nations)
dim(all)
all$Nation<-NULL
DataIn <-Reduce(function(...) merge(...,), list(DataIn,all))
dim(DataIn)
rm(all)
}

#add fake data  
dir.data<-r"(C:\Users\L03054557\Downloads\)"
fake_data_complete<-read.csv(paste0(dir.data,"fake_data_complete_new.csv"))
ids <- c("Nation","iso_code3","Year")
#target_vars<-subset(colnames(DataIn),!(colnames(DataIn)%in%ids))
fake_data_complete[,(colnames(DataIn))]<-NULL
fake_data_complete <- fake_data_complete[fake_data_complete$time_period==0,]
fake_data_complete$time_period<-NULL
DataIn$time_period<-DataIn$Year-2015

DataIn <-Reduce(function(...) merge(...,), list(DataIn,fake_data_complete))
dim(DataIn)
write.csv(DataIn ,paste0(r"(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\Git-LAC-Calib\lac_decarbonization\calibration\SocioEconomic\input_to_sisepuede\for JAmes\)",'data_complete_future_2022_12_09_test.csv'),row.names=FALSE)



#below is not useful 


for (i in 1:length(files))
{
i<-25
target_dir_historial <- r"(\input_to_sisepuede\historical\)"
target_dir_projected <- r"(\input_to_sisepuede\projected\)"
historical<-read.csv(paste0(dir_data,files[i],target_dir_historial,files[i],".csv"))
head(historical)

#"option 1"
  historical$iso_code3<-historical$ISO3
  historical$Nation<-historical$Country
  historical$X<-NULL
  historical$Country<-NULL
  historical$ISO3<-NULL
  head(historical)

#option 2 
  historical$Code<-NULL
  head(historical)
#
write.csv(historical,paste0(dir_data,files[i],target_dir_historial,files[i],".csv"),row.names=FALSE)

}


#
i<-24
target_dir_historial <- r"(\input_to_sisepuede\historical\)"
target_dir_projected <- r"(\input_to_sisepuede\projected\)"
projected<-read.csv(paste0(dir_data,files[i],target_dir_projected,files[i],".csv"))
head(projected)

#"option 1"
  projected$iso_code3<-projected$ISO3
  projected$Nation<-projected$Country
  projected$X<-NULL
  projected$Country<-NULL
  projected$ISO3<-NULL
  head(projected)

#option 2 
  projected$Code<-NULL
  head(projected)

#subset 
historical<-read.csv(paste0(dir_data,files[i],target_dir_historial,files[i],".csv"))
max(historical$Year)
projected<-subset(projected,Year>max(historical$Year))
head(projected)
#
write.csv(projected,paste0(dir_data,files[i],target_dir_projected,files[i],".csv"),row.names=FALSE)




print(head(projected))