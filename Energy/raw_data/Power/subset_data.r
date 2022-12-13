#subset power plant data

#select targetted countries
 dir.tcs<-"C:\\Users\\Usuario\\OneDrive\\Edmundo-ITESM\\3.Proyectos\\42. LAC Decarbonization\\"
 fn.tcs<-"CountriesList.csv"
 tcs<-read.csv(paste0(dir.tcs,fn.tcs))

 #read data file
 dir.data<-"C:\\Users\\Usuario\\OneDrive\\Edmundo-ITESM\\3.Proyectos\\42. LAC Decarbonization\\Data\\Power\\"
 fn.data<-"global_power_plant_database.csv"
 data<-read.csv(paste0(dir.data,fn.data))

#which countries are not in the data base
 subset(unique(tcs$Nation),!(unique(tcs$Nation)%in%unique(data$country_long)))

 #subset data
  data<-subset(data,country_long%in%unique(tcs$Nation))
  write.csv(data,paste0(dir.data,paste0("LAC_",fn.data)),row.names=FALSE)

#create aggregate table per country
  test<-aggregate(list(capacity_mw=data$capacity_mw),list(country_long=data$country_long,
                                                    primary_fuel=data$primary_fuel),sum)

  test<-subset(test,country_long=="Mexico")
