import pandas as pd
import numpy as np
from scipy import interpolate
import subprocess
import os
import sys

## Año objetivo
year_extend = 2060
time_period = year_extend - 2015
last_column = 35

## Define sectores
ssp_sectores = ["af","ce","en","ip","se"]

## Define rutas
DATA_PATH = "/opt/sisepuede/ref/ingestion/calibrated/armenia"
SSP_SECTOR_DATA_PATH = {ssp_sector : os.path.join(DATA_PATH, f"model_input_variables_armenia_{ssp_sector}_calibrated.xlsx") for ssp_sector in ssp_sectores}

## Función para extrapolación
def extrapola(datos : np.array,
              extrapolation_time : int) -> np.array:

    f = interpolate.interp1d(datos[:,0], datos[:,1], fill_value = "extrapolate")
    return f(range(extrapolation_time))

## Diccionario sector-sheet-names
sector_template_sheet_names = {ssp_sector : pd.ExcelFile(ssp_sector_path).sheet_names for ssp_sector,ssp_sector_path in SSP_SECTOR_DATA_PATH.items()}

## Define estrategias
estrategias = [0, 1015,5009]

## Diccionario sector-estrategias
estrategias_sector = {
                        ssp_sector : 
                        
                        {
                            estrategia : pd.read_excel(ssp_sector_path, sheet_name=f"strategy_id-{estrategia}") 
                            for estrategia in estrategias 
                            if f"strategy_id-{estrategia}" in sector_template_sheet_names[ssp_sector]
                        }
                        for ssp_sector,ssp_sector_path in SSP_SECTOR_DATA_PATH.items() 
                    }

## Actualiza al año objetivo para cada pestaña de cada sector
for ssp_sector,ssp_sector_path in SSP_SECTOR_DATA_PATH.items():
    # Abre excel a actualiza
    writer = pd.ExcelWriter(ssp_sector_path, engine='openpyxl', mode='a')
    workBook = writer.book


    # Itera para cada estrategia de cada sector
    for estrategia_id, datos_estrategia in estrategias_sector[ssp_sector].items():

        """
        if ssp_sector=="se" and estrategia_id==0:
            # Extrapola gdp_mmm_usd, population_gnrl_rural y population_gnrl_urban
            gdp_mmm_usd = np.array([[i,j] for i,j in estrategias_sector["se"][0].set_index("variable").loc["gdp_mmm_usd", range(last_column+1)].to_dict().items()])
            population_gnrl_rural = np.array([[i,j] for i,j in estrategias_sector["se"][0].set_index("variable").loc["population_gnrl_rural", range(last_column+1)].to_dict().items()])
            population_gnrl_urban = np.array([[i,j] for i,j in estrategias_sector["se"][0].set_index("variable").loc["population_gnrl_urban", range(last_column+1)].to_dict().items()])

            gdp_mmm_usd_extrapolate = extrapola(gdp_mmm_usd, time_period+1)
            population_gnrl_rural_extrapolate = extrapola(population_gnrl_rural, time_period+1)
            population_gnrl_urban_extrapolate = extrapola(population_gnrl_urban, time_period+1)
        """
        # Actualiza columnas
        for columna_name in range(1, time_period - last_column + 1):
            datos_estrategia[int(columna_name+last_column)] = datos_estrategia[last_column]

        """
        if ssp_sector=="se" and estrategia_id==0:
            datos_estrategia = datos_estrategia.set_index("variable")
            datos_estrategia.loc["gdp_mmm_usd", range(time_period+1)] = gdp_mmm_usd_extrapolate
            datos_estrategia.loc["population_gnrl_rural", range(time_period+1)] = population_gnrl_rural_extrapolate
            datos_estrategia.loc["population_gnrl_urban", range(time_period+1)] = population_gnrl_urban_extrapolate
            datos_estrategia = datos_estrategia.reset_index()
        """
        # Guarda estrategia actualizada
        workBook.remove(workBook[f"strategy_id-{estrategia_id}"])
        datos_estrategia.to_excel(writer, sheet_name = f"strategy_id-{estrategia_id}", index = False)

    # Cierra excel
    writer.close()