
dir_data <-r"(C:\Users\L03054557\OneDrive\Edmundo-ITESM\3.Proyectos\42. LAC Decarbonization\calibration_lac_dec\observed_data\Energy\cost_enfu_fuel_coal_usd_per_m3\raw_data\)"
name_file <-"prices.csv"
data <- read.csv(paste0(dir_data,name_file))

strsplit(data$TIMESERIES, ".")