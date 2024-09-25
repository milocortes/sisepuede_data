#!/bin/bash

GDP=$1

### Enviamos los .py de definición de los parámetros de las intensidades de las transformaciones
cp define_transformation_updated/* ssp_india/opt/sisepuede/python

### Ejecutamos el programa de python para agregar el tipo de GPD (referencia o aspiracional)
python extrapolate_gdp_india.py $GDP

### Movemos el archivo real_data generado
cp real_data.csv ssp_india/opt/ssp_input_data

