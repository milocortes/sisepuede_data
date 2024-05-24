import pandas as pd
from jinja2 import Environment, FileSystemLoader
from tx_original_params import afolu_original_params, energy_original_params
import yaml

# Cargamos parámetros del usuario 
with open('ssp_config_params.yml', 'r') as file:
    ssp_params = yaml.safe_load(file)

# Definimos la configuración de jinja
file_loader = FileSystemLoader('/opt/templates')
env = Environment(loader=file_loader)

# Cargamos el template
template_energy = env.get_template('template_energy')
template_afolu = env.get_template('template_afolu')
template_ce = env.get_template('template_ce')
template_ippu = env.get_template('template_ippu')
template_integrated = env.get_template("template_integrated")

# Actualizamos diccionarios con parámetros
if "energy" in ssp_params["tranformation_params"]:
   energy_original_params.update(ssp_params["tranformation_params"]["energy"])

if "afolu" in ssp_params["tranformation_params"]:
   afolu_original_params.update(ssp_params["tranformation_params"]["afolu"])

# Enviamos la lista de tablas al template
output_params_afolu = template_afolu.render(afolu_original_params = afolu_original_params)
output_params_energy = template_energy.render(energy_original_params = energy_original_params)

# Sustituimos parámetros en los templates y creamos los .py
with open("/opt/sisepuede/python/define_transformations_afolu.py", "w") as afolu_file:
    afolu_file.write(output_params_afolu)

with open("/opt/sisepuede/python/define_transformations_energy.py", "w") as energy_file:
    energy_file.write(output_params_energy)


