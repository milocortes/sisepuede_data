import yaml

with open('/opt/ssp_config_params.yml', 'r') as file:
    ssp_params = yaml.safe_load(file)

### Crea nueva estrategia

cl_instrucciones = []


### Ejecutamos SSP con los parámetros obtenidos del yml
regions = ssp_params["ssp_config_params"]["regions"]
keys_strategy = ssp_params["ssp_config_params"]["keys_strategy"]
keys_design = ssp_params["ssp_config_params"]["keys_design"]
keys_future = ssp_params["ssp_config_params"]["keys_future"]
database_type = ssp_params["ssp_config_params"]["database_type"]

#### Preparamos los parámetros obtenidos del yml para pasarlos a los programas
regions = regions if isinstance(regions, int)  else regions.strip().replace(" ","")
keys_strategy = keys_strategy if isinstance(keys_strategy, int)  else keys_strategy.strip().replace(" ","")
keys_design = keys_design if isinstance(keys_design, int)  else keys_design.strip().replace(" ","")
keys_future = keys_future if isinstance(keys_future, int)  else keys_future.strip().replace(" ","")
database_type = database_type if isinstance(database_type, int)  else database_type.strip().replace(" ","")

##### Construye ejecución para inicializar templates
build_ssp_templates = f"bash /opt/build-ssp-templates.sh {regions}"
cl_instrucciones.append(build_ssp_templates)

##### Construye ejecución para obtener datos del repositorio
build_real_data = f"python3 /opt/build_real_data.py {regions}"
cl_instrucciones.append(build_real_data)

##### Construimos el código para ejecutar la nueva estrategia
if 'new_strategy_params' in ssp_params:
   print("CREAMOS LA NUEVA ESTRATEGIA CON PARÁMETROS")
   build_new_strategy = "python3 /opt/build_new_strategy.py"
   cl_instrucciones.append(build_new_strategy)
   
##### Construye ejecución para la creación de templates
build_ssp_input_data = f"python3 /opt/build_ssp_input_data.py {keys_strategy}"
cl_instrucciones.append(build_ssp_input_data)

##### Construye ejecución del modelo SSP
ssp_cl = f"bash /opt/ejecuta-sisepuede.sh --regions {regions} --keys-strategy {keys_strategy} --keys-design {keys_design} --keys-future {keys_future} --database-type {database_type} --save-inputs"
cl_instrucciones.append(ssp_cl)

##### Merge input and output data
merge_input_output = """
rm -rf /opt/SSP_RESULTS
mkdir /opt/SSP_RESULTS
find /opt/sisepuede/out/ -type f -name "*.csv" -exec mv  "{}" /opt/SSP_RESULTS \;
python3 /opt/merge_ssp_input_output_data.py
"""
cl_instrucciones.append(merge_input_output)

##### Compress results and retrieve them to the user file system where the container is running
regions_file_name = regions if not "," in regions else regions.replace(",","_")
vacio='"{}"'
comprime = f'find /opt/SSP_RESULTS/ -type f -name "*.csv" -exec zip -r -j "ssp_{regions_file_name}.zip" {vacio}  \;'
cl_instrucciones.append(comprime)

with open("/opt/main_ssp_execution.sh", 'w') as ssp_main:
   ssp_main.write("#!/bin/bash" + "\n")
   for cmd in cl_instrucciones:
      ssp_main.write(cmd+"\n")

